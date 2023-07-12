from python:3.11.1-buster

WORKDIR /

RUN pip install runpod
RUN pip install GPUtil
RUN pip install pytube
RUN pip install whisper
RUN pip install git+https://github.com/m-bain/whisperx.git
RUN pip install pydub
RUN pip install reportlab
RUN pip install langchain
RUN pip install tiktoken
RUN pip install openai
RUN apt-get update && apt-get install -y ffmpeg

ADD handler.py .

CMD [ "python", "-u", "/handler.py" ]