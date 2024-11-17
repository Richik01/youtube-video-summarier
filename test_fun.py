# import os

# from groq import Groq
# from dotenv import load_dotenv
# import assemblyai as aai
# from django.conf import settings
# from pytubefix import YouTube
# from pytubefix.cli import on_progress
# import pytest
# load_dotenv()

# API_KEY = os.environ.get("GROQ_API_KEY")
# @pytest.fixture
# def data():
#     return 'https://www.youtube.com/watch?v=0CmtDk-joT4'

# def test_llama():
#     client = Groq(
#         api_key=API_KEY,
#     )

#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": "Hello world",
#             }
#         ],
#         model="llama3-8b-8192",
#     )

#     print(chat_completion.choices[0].message.content)
#     assert isinstance(chat_completion.choices[0].message.content, str)
#     assert len(chat_completion.choices[0].message.content) > 0


# def test_get_transcription(data):
#     yt = YouTube(data, on_progress_callback = on_progress)
#     caption = yt.captions
#     caption.save_captions('caption.txt')

#     # Open the caption file
#     with open("caption.txt", "r") as file:
#         lines = file.readlines()

#     # Initialize a list to hold caption lines
#     captions = []

#     # Process the lines
#     for line in lines:
#         line = line.strip()  # Remove leading/trailing whitespace
#         # Skip lines that are timestamps or numbering
#         if not line or line.isdigit() or "-->" in line:
#             continue
#         # Add remaining lines to captions list
#         captions.append(line)

#     # Combine the lines into a single paragraph
#     output = " ".join(captions)

#     # Optionally save to a new file
#     with open("caption.txt", "w") as outfile:
#         outfile.write(output)
#     print(output)
#     assert isinstance(output, str)
#     assert len(output) > 0

from pytubefix import YouTube

yt = YouTube("https://www.youtube.com/watch?v=sWdTsesGvfU")
subtitles = yt.title
print(subtitles)