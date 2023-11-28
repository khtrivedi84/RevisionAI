# RevisionAI 

RevisionAI is a web application that utilizes artificial intelligence (AI) to generate topic-wise summaries and extract important information from uploaded class recordings. With this application, you can easily summarize your recorded lectures, identify key topics, and extract essential details for exams, midterms, assignments, or preparing for future lectures. 

The system is optimized to deal with the issue of hallucinations that the LLMs are infamous for. It also demonstrates on how efficient prompt engineering can help utilise the power of Large Language Models and get accurate results (even with a small context window of 8k or 16k tokens). 

**(Screen Recording at the bottom)**

## Features

**Topic-wise Summaries**: The AI-powered analyzes the uploaded class recordings and generates concise summaries for each topic covered in the lecture. These summaries provide a quick overview of the main points discussed, enabling you to review the content more efficiently.

**Keyword Extraction**: The application extracts relevant keywords for each topic, helping you identify the core concepts and significant terms associated with the lecture content. These keywords can be useful for creating study notes or searching for specific information within the recordings. The keywords are interactive and a more "detailed" or "simple" explanation would be generated in the context of the paragraph that contains the keyword.

**Importance Indicators**: Class Recording Summarizer automatically identifies the importance of each topic for various academic purposes, such as exams, midterms, assignments, or preparing for future lectures. This feature assists you in prioritizing your study or preparation efforts based on the significance of each topic.

**Saves Time and Effort**: By automating the process of summarizing class recordings and extracting crucial information, the application saves you valuable time and effort. You can quickly access the most vital details from your lectures, enabling a more focused and efficient approach to studying and review.

## Getting Started

### Installation

To use RevisionAI, follow these steps:

Clone this repository to your local machine.

```bash
  git clone https://github.com/kishan12345/RevisionAI.git
```
Run following commands to install required modules and packages

```bash
  pip install flask
  pip install flask_sqlalchemy
  pip install flask_migrate
  pip install moviepy
  pip install openai
```
Install Docker and create docker image using the Dockerfile and handler.py file provided in this repository. Push the docker image to DockerHub and use this Docker image from DockerHub to create a serverless endpoint at Runpod.io (Instructions to use runpod.io can be found in their documentation)

Obtain required keys from the OpenAI, RunPod, and AI21 and replace them in the "app.py" file. Also, make sure to update the "public_ip" and "port" with your amazon ec2 instance ip or any other cloud service you might be using.

Run following command to start the flask server
```bash
  flask --app app run
```

Voila! Your app must have started and you can start summarizing your lectures.

## Technologies Used

**OpenAI Whisper Model and WhisperX**: Used for long audio-to-text transcription enabling the processing of lengthy class recordings.

**AI21 Text Segmentation API**: Utilized for segmenting the transcribed text into topic-wise sections, allowing for focused analysis and summarization.

**PyAnnotate**: Employed for speaker diarization, separating speakers' voices within the class recordings, facilitating a more organized analysis and summary generation.

**OpenAI GPT-3.5-turbo-16k**: Leveraged for various natural language processing tasks, including topic summarization, generating topic headings, extracting keywords, and identifying important information. This powerful language model enhances the application's ability to provide comprehensive and informative summaries.

**Web application**: Flask for back-end, Bootstrap for front-end, and SQLite as database for storing userinfo and lecture summaries.

## Upcoming features

**Pinecone Vector Database**: Utilize Pinecone, a vector database, to store and retrieve class materials for improved accuracy.

**Retrieval Search and Retrieval Augmentation**: Implement retrieval search techniques to fetch relevant information from the knowledge base, enhancing summaries. Retrieve and incorporate content from class materials to provide comprehensive summaries.

**Integrated ChatGPT for Question Answering**: Seamlessly integrate ChatGPT for general question answering, allowing users to obtain specific information from the class recordings.

**GPT-4 32k Model Integration**: Incorporate the powerful GPT-4 32k model to enable a larger context window for analysis, leading to more accurate and detailed summaries.

**LangChain for Text Splitting and Chunk Creation**: Utilize LangChain to effectively split text into manageable chunks, improving the precision of analysis and generating higher-quality summaries and question answering results.

## Screen Recording (Demo)

[<img src="https://img.youtube.com/vi/Zxm7Bf4VSi0/maxresdefault.jpg" width="50%">](https://youtu.be/Zxm7Bf4VSi0)
