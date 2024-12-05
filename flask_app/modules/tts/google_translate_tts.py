""" Synthesize speech from text using Google translate Text-to-Speech API """

from flask import current_app
from gtts import gTTS, gTTSError


class GoogleTranslateTTS(object):
    def __init__(self, file_path=None, text=None, voice="us"):

        self.file_path = file_path
        self.text = text
        self.voice = voice

    def synthesize_speech(self):

        speech_file_path = self.file_path
        tts = None

        current_app.logger.info("Processing content GTTS")
        try:
            tts = gTTS(text=self.text, lang="en", tld=self.voice)

        except AssertionError as e:
            raise Exception(f"Google Translate AssertionError during request: {e}")

        except ValueError as e:
            raise Exception(f"Google Translate ValueError error during request: {e}")

        except RuntimeError as e:
            raise Exception(f"Google Translate RuntimeError during request: {e}")

        except gTTSError as e:
            raise Exception(f"Google Translate gTTSError during request: {e}")

        except Exception as e:
            raise Exception(f"Google Translate unexpected error during request: {e}")

        # save the file
        try:
            tts.save(speech_file_path)

        except gTTSError as e:
            raise Exception(f"Google Translate gTTSError during save: {e}")

        except Exception as e:
            raise Exception(f"Google Translate unexpected error during save: {e}")

        return speech_file_path
