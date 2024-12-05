import boto3
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError
import os
import sys


class PollyTTS:
    def __init__(self, file_path=None, text=None, voice="Matthew", language="en-US"):
        self.file_path = file_path
        self.text = text
        self.voice = voice
        self.language = language

    def validate_inputs(self):
        if not self.text or not isinstance(self.text, str):
            raise ValueError("Text must be a non-empty string.")
        if not self.file_path or not isinstance(self.file_path, str):
            raise ValueError("File path must be a valid string.")
        if not os.path.isdir(os.path.dirname(self.file_path)):
            raise ValueError(
                f"Directory does not exist: {os.path.dirname(self.file_path)}"
            )

    def synthesize_speech(self):
        # Validate inputs before making the request
        try:
            self.validate_inputs()
        except ValueError as e:
            raise Exception(f"Amazon Polly an value error occurred: {e}")

        try:
            client = boto3.client("polly", region_name="us-east-1")
            response = client.synthesize_speech(
                OutputFormat="mp3",
                Text=self.text,
                TextType="text",
                VoiceId=self.voice,
                Engine="neural",
            )

            if "AudioStream" not in response:
                raise Exception(f"No AudioStream in Polly response")

            with closing(response["AudioStream"]) as stream:
                try:
                    with open(self.file_path, "wb") as file:
                        file.write(stream.read())
                        print(f"Audio file saved at: {self.file_path}")
                except IOError as error:
                    raise Exception(f"File I/O Error in Polly module: {error}")

        except (BotoCoreError, ClientError) as error:
            raise Exception(f"Polly API Error: {error}")
        except RuntimeError as error:
            raise Exception(f"Polly Runtime Error: {error}")

        return self.file_path
