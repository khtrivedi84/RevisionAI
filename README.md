# RevisionAI

RevisionAI is a web application that utilizes artificial intelligence (AI) to generate topic-wise summaries and extract important information from uploaded class recordings. With this application, you can easily summarize your recorded lectures, identify key topics, and extract essential details for exams, midterms, assignments, or preparing for future lectures.

## Features

Topic-wise Summaries: The AI-powered analyzes the uploaded class recordings and generates concise summaries for each topic covered in the lecture. These summaries provide a quick overview of the main points discussed, enabling you to review the content more efficiently.

Keyword Extraction: The application extracts relevant keywords for each topic, helping you identify the core concepts and significant terms associated with the lecture content. These keywords can be useful for creating study notes or searching for specific information within the recordings. The keywords are interactive and a more "detailed" or "simple" explanation would be generated in the context of the paragraph that contains the keyword.

Importance Indicators: Class Recording Summarizer automatically identifies the importance of each topic for various academic purposes, such as exams, midterms, assignments, or preparing for future lectures. This feature assists you in prioritizing your study or preparation efforts based on the significance of each topic.

Saves Time and Effort: By automating the process of summarizing class recordings and extracting crucial information, the application saves you valuable time and effort. You can quickly access the most vital details from your lectures, enabling a more focused and efficient approach to studying and review.

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

## Technologies Used

OpenAI Whisper Model: Used for audio-to-text transcription, converting the class recordings into textual format for further processing.

ai21 Text Segmentation API: Utilized for segmenting the transcribed text into topic-wise sections, allowing for focused analysis and summarization.

WhisperX: Used for long-audio transcription, enabling the processing of lengthy class recordings while maintaining accuracy and efficiency.

PyAnnotate: Employed for speaker diarization, separating speakers' voices within the class recordings, facilitating a more organized analysis and summary generation.

OpenAI GPT-3.5-turbo-16k: Leveraged for various natural language processing tasks, including topic summarization, generating topic headings, extracting keywords, and identifying important information. This powerful language model enhances the application's ability to provide comprehensive and informative summaries.

Python Flask: Chosen as the web application framework for its simplicity and flexibility. Flask enables efficient development and deployment of the application's backend functionality.

HTML, CSS, and JavaScript: Used for the frontend development, creating an intuitive and user-friendly interface for interacting with the application. These web technologies provide the necessary structure, styling, and interactivity to enhance the user experience.

Bootstrap: Employed as a frontend framework to streamline the design and layout process. Bootstrap offers a responsive grid system and a wide range of pre-built components, allowing for faster and consistent development of the application's frontend.

SQLite: Selected as the database management system for its lightweight nature and seamless integration with Python. SQLite efficiently stores and retrieves data, supporting the application's functionality related to user accounts, uploaded files, and other relevant information.
