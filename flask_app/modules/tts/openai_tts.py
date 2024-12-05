""" Synthesize speech from text using OpenAI Text-to-Speech API """

import openai
from openai import OpenAIError
from requests.exceptions import HTTPError, Timeout


class OpenAITTS(object):
    def __init__(self, file_path=None, text=None, voice="alloy"):

        self.file_path = file_path
        self.text = text
        self.voice = voice

    def synthesize_speech(self):

        client = openai.OpenAI()
        speech_file_path = self.file_path

        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=self.text,
            )
            response.stream_to_file(speech_file_path)

        except HTTPError as e:
            raise Exception(f"OpenAI HTTPError: {e}")

        except Timeout:
            raise Exception(f"OpenAI timeout error occurred: {e}")

        except OpenAIError as e:
            raise Exception(f"OpenAI error occurred: {e}")

        return self.file_path
