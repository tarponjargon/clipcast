import os
import json
import boto3
import time
import sys
from datetime import datetime, timedelta
import nltk
from nltk.tokenize import sent_tokenize
from slugify import slugify
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from flask import current_app
from flask_app.modules.extensions import DB
from flask_app.modules.http import report_error_http
from flask_app.modules.helpers import get_first_n_words, match_uuid
from flask_app.modules.user.user import load_user
from flask_app.modules.tts.google_tts import GoogleTTS
from flask_app.modules.tts.openai_tts import OpenAITTS
from flask_app.modules.tts.google_translate_tts import GoogleTranslateTTS
from flask_app.modules.tts.polly_tts import PollyTTS

nltk.download("punkt")  # Downloads necessary data for tokenization
nltk.download("punkt_tab")


def split_text_to_chunks(text, row_id):
    """Split text into chunks, with each chunk containing {chunk_size} sentences concatenated together"""

    sentences = sent_tokenize(text)
    chunk_size = current_app.config.get("TTS_SENTENCE_CHUNK_SIZE")
    chunks = []
    current_chunk = []

    # create a new list that contains every {chunk_size} sentences concatenated together in an element
    for index, sentence in enumerate(sentences):
        current_chunk.append(sentence)

        if (index + 1) % chunk_size == 0:
            mychunk = " ".join(current_chunk)
            chunks.append(mychunk)
            current_chunk = []

    # handle stragglers at the end
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def openai_speech(file_path, text, voice="alloy"):
    """Create MP3 files for each chunk of text using OpenAI's TTS API"""
    tts = OpenAITTS(file_path=file_path, text=text, voice=voice)
    speech_file_path = file_path
    try:
        speech_file_path = tts.synthesize_speech()
    except Exception as e:
        print(f"Error with OpenAI TTS: {e}")
        report_error_http(f"Error with OpenAI TTS: {e}")
        return {"error": e, "speech_file_path": None}
    return {"error": None, "speech_file_path": speech_file_path}


def google_translate_speech(file_path, text, voice="us"):
    """Create MP3 files for each chunk of text using gTTS (a google translate model)"""
    tts = GoogleTranslateTTS(file_path=file_path, text=text, voice=voice)
    speech_file_path = file_path
    try:
        speech_file_path = tts.synthesize_speech()
    except Exception as e:
        print(f"Error with Google Translate TTS: {e}")
        report_error_http(f"Error with Google Translate TTS: {e}")
        return {"error": e, "speech_file_path": None}
    return {"error": None, "speech_file_path": speech_file_path}


def google_tts(file_path, text, voice="en-IN-Neural2-C", language_code="en-US"):
    """Create MP3 files for each chunk of text using Google's TTS API"""
    tts = GoogleTTS(file_path=file_path, text=text, voice=voice, language=language_code)
    speech_file_path = file_path
    try:
        speech_file_path = tts.synthesize_speech()
    except Exception as e:
        print(f"Error with Google TTS: {e}")
        report_error_http(f"Error with Google TTS: {e}")
        return {"error": e, "speech_file_path": None}
    return {"error": None, "speech_file_path": speech_file_path}


def polly_tts(file_path, text, voice="Matthew", language_code="en-US"):
    """Create MP3 files for each chunk of text using Amazon's TTS API"""
    tts = PollyTTS(file_path=file_path, text=text, voice=voice, language=language_code)
    speech_file_path = file_path
    try:
        speech_file_path = tts.synthesize_speech()
    except Exception as e:
        print(f"Error with Polly TTS: {e}")
        report_error_http(f"Error with Polly TTS: {e}")
        return {"error": e, "speech_file_path": None}
    return {"error": None, "speech_file_path": speech_file_path}


def get_user_selected_voice(user_id, voice_code):
    """Get the user's selected voice from the database"""

    q = DB.fetch_one("SELECT premium_voice FROM user WHERE user_id = %s", (user_id))
    voice_code = q.get("premium_voice", current_app.config.get("DEFAULT_PREMIUM_VOICE"))

    res = None
    if voice_code == "random":
        user = load_user(user_id)
        plan = user.get("plan") if user and user.get("plan") else "base"

        res = DB.fetch_one(
            "SELECT * FROM voices WHERE visible = 1 AND plan = %s ORDER BY RAND() LIMIT 1",
            (plan),
        )
    else:
        res = DB.fetch_one(
            "SELECT * FROM voices WHERE voice_code = %s AND plan = 'premium'",
            (voice_code),
        )
    return res


def create_intro_mp3(row):
    """Create an intro MP3 file for the podcast episode"""

    combined_audio = AudioSegment.empty()

    # create an intro mp3 file
    intro_file_path = (
        f"{current_app.config.get("TMP_DIR")}/{row.get('content_id')}-intro.mp3"
    )
    intro_voice = DB.fetch_one(
        "SELECT * FROM voices WHERE voice_code = %s",
        (current_app.config.get("TRANSITION_VOICE")),
    )
    title = row.get("title")
    author = row.get("author")
    text = f"""Thank you for using ClipCast.  Here is your podcast entitled "{title}" by {author}."""

    intro = openai_speech(intro_file_path, text, intro_voice.get("voice_code"))

    if not intro.get("speech_file_path"):
        return None

    print(f"INTRO: {intro}")
    intro_audio = None
    try:
        intro_audio = AudioSegment.from_mp3(intro.get("speech_file_path"))
    except Exception as e:
        print(f"Error with intro audio: {e}")
        report_error_http(f"Error with intro audio: {e}")
        return

    print(f"INTRO AUDIO: {intro_audio}")
    # os.remove(intro.get("speech_file_path"))

    # concatenate a transition audio file
    transition_file_path = (
        f"{current_app.config.get("PUBLIC_HTML")}/assets/audio/transition1.mp3"
    )
    transition_audio = AudioSegment.from_mp3(transition_file_path)

    combined_audio = intro_audio + transition_audio

    # add the intro and transition to the combined audio
    segment_file_path = (
        current_app.config.get("TMP_DIR") + f"/{row.get('content_id')}-segment1.mp3"
    )

    print(f"SEGMENT FILE PATH: {segment_file_path}")

    combined_audio.export(segment_file_path, format="mp3")

    return segment_file_path


def create_chunk_mp3s(text_chunks, row, start_time):
    """Create MP3 files for each chunk of text using ChatGPT's TTS API"""
    files = []
    errors = []
    voice = get_user_selected_voice(row.get("user_id"), row.get("voice_code"))

    print(f"VOICE: {voice}")
    print(f"TOTAL CHUNKS: {len(text_chunks)}")

    # create an intro mp3 file
    intro_file_path = create_intro_mp3(row)
    if intro_file_path:
        files.append(intro_file_path)

    print(f"FILES: {files}")
    # tell the record how many chunks there are (for progress report)
    updq = DB.update_query(
        """
        UPDATE podcast_content SET
        total_chunks = %s
        WHERE content_id = %s
      """,
        (len(text_chunks), row.get("content_id")),
    )

    for count, chunk in enumerate(text_chunks, 1):
        print(f"Chunk {count} (size {len(chunk)}):")
        print(f"CHUNK: {chunk}\n")

        # generate tts for each chunk
        speech_file_path = (
            current_app.config.get("TMP_DIR") + f"/{row.get('content_id')}-{count}.mp3"
        )
        output = None
        if voice.get("tts_model") == "openai":
            output = openai_speech(speech_file_path, chunk, voice.get("voice_code"))
        elif voice.get("tts_model") == "googletts":
            output = google_tts(
                speech_file_path,
                chunk,
                voice.get("voice_code"),
                voice.get("language_code"),
            )
        elif voice.get("tts_model") == "pollytts":
            output = polly_tts(
                speech_file_path,
                chunk,
                voice.get("voice_code"),
                voice.get("language_code"),
            )
        else:
            output = google_translate_speech(
                speech_file_path, chunk, voice.get("voice_code")
            )

        if output.get("speech_file_path"):
            files.append(output.get("speech_file_path"))
        if output.get("error"):
            errors.append(str(output.get("error")))

        current_time = time.time()
        elapsed_time = current_time - start_time

        # update the record with the processing time and number of chunks processed
        DB.update_query(
            """
            UPDATE podcast_content SET
            processing_time_seconds = %s,
            processed_chunks = %s
            WHERE content_id = %s
          """,
            (elapsed_time, count, row.get("content_id")),
        )

    return files, voice.get("voice_code"), errors


def delete_mp3s(files):
    """Delete the chunk MP3 files"""
    for file_path in files:
        if "/assets/audio/" not in file_path:
            os.remove(file_path)


def concatenate_mp3s(files, output):
    """Concatenate multiple MP3 files into a single file"""

    print(f"Concatenating files: {files} to {output}")
    # Start with an empty AudioSegment
    combined = AudioSegment.empty()

    # add any intros
    # intro = f"{current_app.config.get("PUBLIC_HTML")}/assets/audio/clipcast_intro.mp3"
    # transition = f"{current_app.config.get("PUBLIC_HTML")}/assets/audio/transition1.mp3"
    # files.insert(0, transition)
    # files.insert(0, intro)
    # files.append(transition)

    # Loop through all the files and append them
    for file in files:
        audio = AudioSegment.from_mp3(file)
        combined += audio

    # Export the concatenated audio to a file
    combined.export(output, format="mp3")


def tag_mp3(file, title, author, album, article_date):
    """Add ID3 tags to an MP3 file"""

    if not author:
        author = album

    if not article_date:
        article_date = datetime.now().strftime("%Y-%m-%d")

    audio = MP3(file, ID3=EasyID3)
    audio["title"] = title
    audio["artist"] = author
    audio["album"] = author
    audio["date"] = str(article_date)
    audio["genre"] = "Podcast"
    audio.save()


def get_mp3_duration(file):
    """Get the duration of an MP3 file HH:MM:SS"""
    audio = MP3(file)
    return str(timedelta(seconds=round(audio.info.length)))


def get_title(title, content):
    """Get the title of the podcast episode.  if there isn't one, use the first few words of the content"""
    if not title:
        title = get_first_n_words(content, 10)
    return title


def create_episode_filename(title):
    """Create a filename for the podcast episode"""

    episode_basename = slugify(
        title, max_length=32, word_boundary=True, save_order=True
    )
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return episode_basename + "-" + timestamp + ".mp3"


def upload_to_s3(file_path):
    """Upload a file to an S3 bucket"""

    s3_client = boto3.client(
        service_name="s3",
        endpoint_url=current_app.config.get("S3_URL"),
        aws_access_key_id=current_app.config.get("S3_ACCESS_KEY"),
        aws_secret_access_key=current_app.config.get("S3_SECRET_ACCESS_KEY"),
        region_name="auto",
    )
    object_name = os.path.basename(file_path)
    bucket_name = current_app.config.get("S3_BUCKET")

    print(f"Uploading {file_path} to {bucket_name} as {object_name}")

    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        report_error_http(f"Error uploading to S3: {e}")
        raise e
        return None

    return current_app.config.get("S3_PUBLIC_URL") + object_name


def process_episode(content_id):
    """Process a single episode"""
    with current_app.app_context():
        episode = DB.fetch_one(
            """
          SELECT
            content_id,
            user_id,
            title,
            author,
            hostname,
            article_date,
            content
          FROM podcast_content
          WHERE content_id = %s
        """,
            (content_id),
        )

        if not episode:
            return ["Episode not found"]

        errors = []
        row_id = episode.get("content_id")
        start_time = time.time()

        DB.update_query(
            """
          UPDATE podcast_content
          SET current_status = 'processing',
          processing_start_time = NOW()
          WHERE content_id = %s
        """,
            (row_id,),
        )

        title = get_title(episode.get("title"), episode.get("content"))
        hostname = episode.get("hostname", "")
        author = episode.get("author", hostname)
        article_date = episode.get("article_date", "")
        text_chunks = split_text_to_chunks(episode.get("content", ""), row_id)
        mp3_files, voice_code, tts_errors = create_chunk_mp3s(
            text_chunks, episode, start_time
        )

        # if there are errors, we're done
        if tts_errors:
            errors.extend(tts_errors)
            # mark as complete
            upd = DB.update_query(
                """
            UPDATE podcast_content SET
            current_status = 'error',
            error_message = %s,
            processing_end_time = NOW()
            WHERE content_id = %s
        """,
                (", ".join(tts_errors), row_id),
            )
            return errors

        episode_filename = create_episode_filename(title)
        final_mp3 = current_app.config.get("TMP_DIR") + f"/{episode_filename}"

        # Concatenate the audio files
        concatenate_mp3s(mp3_files, final_mp3)

        # Add ID3 tags
        tag_mp3(final_mp3, title, author, hostname, article_date)

        # Upload to S3
        episode_url = upload_to_s3(final_mp3)

        # get byte size of file
        file_size = os.path.getsize(final_mp3)

        # get duration of audio file
        duration = get_mp3_duration(final_mp3)

        # delete the chunk audio files and final file
        mp3_files.append(final_mp3)
        delete_mp3s(mp3_files)

        # record the processing time for progress bar
        end_time = time.time()
        elapsed_time = end_time - start_time

        # record estimated cost in cents.  best guess at this time is 0.01 per 600 characters
        estimated_cost_cents = round(len(episode.get("content")) / 600, 2)

        # # mark as complete
        upd = DB.update_query(
            """
        UPDATE podcast_content SET
        current_status = 'complete',
        mp3_url = %s,
        mp3_file_size = %s,
        mp3_duration = %s,
        processing_time_seconds = %s,
        estimated_cost_cents = %s,
        processing_end_time = NOW(),
        voice_code = %s
        WHERE content_id = %s
    """,
            (
                episode_url,
                file_size,
                duration,
                elapsed_time,
                estimated_cost_cents,
                voice_code,
                row_id,
            ),
        )

        # add notification
        DB.insert_query(
            """
        INSERT INTO notification (user_id, message)
        VALUES (%s, %s)
    """,
            (episode.get("user_id"), f"Your podcast episode '{title}' is ready!"),
        )
