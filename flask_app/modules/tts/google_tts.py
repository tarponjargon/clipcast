"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""

from google.api_core.exceptions import GoogleAPIError, InvalidArgument
from google.cloud import texttospeech


class GoogleTTS(object):
    def __init__(
        self, file_path=None, text=None, voice="en-US-Neural2-D", language="en-US"
    ):

        self.file_path = file_path
        self.text = text
        self.voice = voice
        self.language = language

    def synthesize_speech(self):
        """Synthesizes speech from the input string of text."""

        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=self.text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.language,
            name=self.voice,
            # ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = None
        try:
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

        except InvalidArgument as e:
            raise Exception(f"Google TTS invalid argument error: {e}")

        except GoogleAPIError as e:
            raise Exception(f"Google TTS API error: {e}")

        except Exception as e:
            raise Exception(f"Google TTS an unexpected error occurred: {e}")

        # The response's audio_content is binary.
        try:
            with open(self.file_path, "wb") as out:
                out.write(response.audio_content)
                print(f"Google TTS Audio content written to file {self.file_path}")

        except IOError as e:
            raise Exception(
                f"Failed to write audio content to file {self.file_path}: {e}"
            )

        except AttributeError as e:
            raise Exception(f"Audio content is missing or invalid: {e}")

        except Exception as e:
            raise Exception(
                f"An unexpected error occurred writing file  {self.file_path}: {e}"
            )

        return self.file_path
