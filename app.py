from flask import Flask, request, send_file, request, render_template, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from moviepy.editor import VideoFileClip
from requests.structures import CaseInsensitiveDict
import requests
import os
import json
import time
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = '<SECRET_KEY>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    study_materials = db.relationship('StudyMaterial', backref='user', lazy=True)


class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    courseName = db.Column(db.String(100), nullable=False)
    lectures = db.relationship('Lecture', backref='study_material', lazy=True)

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    study_material_id = db.Column(db.Integer, db.ForeignKey('study_material.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    lecture_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    file_path = db.Column(db.String(100), nullable=False)

class LectureData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)
    topic_title = db.Column(db.String(100), nullable=False)
    topic_description = db.Column(db.String(5000), nullable=False)
    topic_keywords = db.Column(db.String(500), nullable=False)
    important_information = db.Column(db.String(5000), nullable=False)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['mp4'])
LATEST_COURSE_JSON_NAME = 'latest_course.json'

# function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file_as_dict(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
        file_dict = json.loads(file_contents)
    return file_dict

def write_dict_to_file(file_path, data_dict):
    with open(file_path, 'w') as file:
        json.dump(data_dict, file)

def get_creation_time(entry):
    creation_time = entry.stat().st_ctime
    formatted_time = time.ctime(creation_time)
    return formatted_time

# @app.route('/')
# def index():
#     return render_template('course.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['fname']
        
        # Check if the username is already taken
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Username already exists.')
        
        # Create a new user
        new_user = User(name=name ,email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        directory = "uploads/" + email
        os.mkdir(directory)
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find the user by username
        user = User.query.filter_by(email=email).first()
        
        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password.')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('dashboard'))

@app.route('/')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    study_materials = user.study_materials
    return render_template('course.html', user=user, study_materials=study_materials)

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if request.files['file']:
            file = request.files['file']


        user = User.query.get(session['user_id'])
        courseName = request.args.get('course')
        # courseName = request.form.get('course')
        title = request.form.get('title')
        lecture_number = request.form.get('number')
        if courseName == '' or title == '' or file.filename == '' or lecture_number == '':
            error = " Please fill all the details"
            return render_template('addacourse.html', response=error)
        
        # Save the file to a directory and get the file path
        # file_path = f'uploads/{file.filename}'
        # file.save(file_path)
        user = User.query.get(session['user_id'])
        video_directory = "uploads/" + user.email + "/" + courseName + "/" + lecture_number+ "/" + "video"
        os.makedirs(video_directory)
        file_path = f'{video_directory}/{file.filename}'
        print(file_path)
        file.save(file_path)

        audio_directory = "uploads/" + user.email + "/" + courseName + "/" + lecture_number + "/" + "audio"
        os.makedirs(audio_directory)

        output_file = f'{audio_directory}/{file.filename}'
        output_file = output_file.replace("mp4", "wav")

        video = VideoFileClip(file_path)
        audio = video.audio
        audio.write_audiofile(output_file)

        # Perform a database query to find the row with the matching data
        row = StudyMaterial.query.filter_by(user=user, courseName=courseName).first()
        lecture_details = Lecture(user_id = row.user_id, study_material_id=row.id, title=title, lecture_number=lecture_number, file_path=file_path)
        db.session.add(lecture_details)
        db.session.commit()

        url_filename = file.filename
        url_filename = url_filename.replace(".mp4", "")
        email = user.email

        url = "https://api.runpod.ai/v2/2v29gahx7n42uc/run"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer <RUNPOD_API_KEY>"
        headers["Content-Type"] = "application/json"

        data = '{{"input": {{"public_ip": "<YOUR_LINUX_IMAGE_IP>", "port": "<YOUR_PORT>", "course_name": "{0}", "user_email": "{1}", "lecture_number": "{2}", "file_name": "{3}"}}}}'.format(courseName, email, lecture_number, url_filename)
        print(data)
        
        resp = requests.post(url, headers=headers, data=data)
        response_text = resp.text
        time.sleep(2)
        print(response_text)
        jsonResponse = json.loads(response_text)
        requestId = jsonResponse["id"]
        print(requestId)

        status = True
        while status:
            new_url = "https://api.runpod.ai/v2/2v29gahx7n42uc/status/" + requestId
            new_resp = requests.post(new_url, headers=headers)
            checking_status = new_resp.text
            status_jsonResponse = json.loads(checking_status)
            current_status = status_jsonResponse["status"]
            if current_status == "IN_QUEUE" or current_status == "IN_PROGRESS":
                time.sleep(20)
                continue
            else:
                status = False

        new_response_text = new_resp.text
        new_response_text = new_response_text.replace(r'\"', '"')

        # Remove the leading and trailing double quotes
        new_response_text = new_response_text.strip('"')
        print("new_response_text")
        print(new_response_text)

        # Parse the response text as JSON
        response_json = json.loads(new_response_text)

        # Save the JSON to a file
        with open('output.json', 'w') as file:
            json.dump(response_json, file, indent=4)

        with open('output.json', 'r') as file:
            json_content = file.read()

        data = json.loads(json_content)
        segments = data['output']['result']['segments']

        previous_speaker = segments[0]['speaker']
        text = f'{previous_speaker}:'
        for segment in segments:
            if segment['speaker'] == previous_speaker:
                text+= " " + segment['text']
            else:
                text += "\n" + f'{segment["speaker"]}: {segment["text"]}'
                previous_speaker = segment['speaker']

        wordtune_api_url = "https://api.ai21.com/studio/v1/segmentation"

        print("Printing text after speaker diarization: \n")
        print(text)

        payload = {
            "sourceType": "TEXT",
            "source": text,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "Bearer <API_KEY_FROM_AI21>"
        }

        wordtune_response = requests.post(wordtune_api_url, json=payload, headers=headers)
        wordtune_response = wordtune_response.json()

        # print(wordtune_response)
        with open('response.json', 'w') as json_file:
            json.dump(wordtune_response, json_file, indent=4)

        response_segments = wordtune_response['segments']
        print("Segmentation using wordtune API:")
        print(response_segments)

        openai.api_key = "<API_KEY_FROM_OPENAI>"
        message = [ {"role": "system", "content": "I want you to act as a summarizer who summarizes transcript of a class recording. I'll give you transcript in multiple parts and you have to generate summaries as I give. For each new input, if it is a continuation of the previous topic, start the response with 'Old topic: ' or else start with 'New topic: '"} ]
        final_response = []
        for segment in response_segments:
            segment_text = segment["segmentText"]
            message.append(
                {"role": "user", "content": f'{segment_text}'}
            )
            flag = True
            count = 0
            while flag:
                try:
                    chat = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k", messages=message
                    )
                    flag = False
                except:
                    if count <= 3:
                        print("Error occured. Trying again...")
                        count += 1
                        continue
                    else:
                        print("Error occured. Exiting...")
                        break
            reply = chat.choices[0].message.content
            message.append({"role": "assistant", "content": reply})
            print("Message length: ", len(message))
            final_response.append(chat.choices[0].message.content)
            print("FInal response length: ", len(final_response))
            if len(final_response) >35:
                del message[1]
                del message[2]
            # print(final_response)

        print(len(message))
        print(message)
        print(len(final_response))
        print(final_response)

        time.sleep(10)

        str_response = str(final_response)

        with open('paraphrased_segment.txt', 'w') as file:
            file.write(str_response)
        print(len(message))
        print(message)
        print(len(final_response))
        print(final_response)

        # read the file and store it in a variable
        print("Reading the file paraphrased_segment.txt file")
        with open('paraphrased_segment.txt', 'r') as file:
            data = file.read().replace('\n', '')

        # print(data)
        print("Converting the string to a list using eval() function")
        data = eval(data)

        topics = []
        temp_string = ''

        print("Removing the 'Old topics: ' and 'New topic: ' text from the list")
        for item in data:
            if item.startswith('Old topic: '):
                # Remove the 'New topic: ' from the string
                item = item.replace('Old topic: ', '')
                temp_string = temp_string + item
            elif item.startswith('New topic: '):
                topics.append(temp_string)
                temp_string = ''
                # Remove the 'Old topic: ' from the string
                item = item.replace('New topic: ', '')
                temp_string = temp_string + item
        topics.append(temp_string)

        print("Printing the topics list")
        for i in topics:
            print(len(i))
            print('\n')
            print(i)   
            print('\n')


        openai.api_key = "<API_KEY_FROM_OPENAI>"

        print("Generating topic heading and keywords for each topic")

        topic_headings = []
        topic_keywords = []
        topic_and_keywords = []
        for topic in topics:
            message = [ {"role": "system", "content": "Give a topic heading for the my input paragraph and a python list that contains 5 to 10 keywords or technical words. It should strictly be a python list only and should be in the format 'keywords: <item1>,<item2>,...'. The topic should be in the format 'Topic: <topic name>'. Do not write or generate anything else."} ]
            message.append(
                {"role": "user", "content": f'{topic}'}
            )
            flag = True
            count = 0
            while flag:
                try:
                    chat = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k", messages=message
                    )
                    flag = False
                except:
                    if count <= 3:
                        print("Error occured. Trying again...")
                        count += 1
                        continue
                    else:
                        print("Error occured. Exiting...")
                        break
            reply = chat.choices[0].message.content
            message = []

            # Extract topic
            topic_start_index = reply.find("Topic: ") + len("Topic: ")
            topic_end_index = reply.find("\nKeywords:")
            topic1 = reply[topic_start_index:topic_end_index].strip()
            topic_headings.append(topic1)

            # Extract keywords
            keywords_start_index = reply.find("Keywords: ") + len("Keywords: ")
            keywords_string = reply[keywords_start_index:]
            keywords1 = [keyword.strip() for keyword in keywords_string.split(",")]
            topic_keywords.append(keywords1)

            topic_and_keywords.append(reply)

        print("Printing length of topic and keywords array and the array itself")
        print(len(topic_and_keywords))
        print(topic_and_keywords)

        print("Topic headings: ")
        print(topic_headings)
        print("Topic keywords: ")
        print(topic_keywords)

        time.sleep(10)

        print("Extracting important information...")
        important_information = []
        for topic in topics:
            message = [ {"role": "system", "content": "If it is specifically mentioned that this topic is important for the midterm exam, assignment, or finals, note it down. Do not mark it as important because you feel it is important. If any deadlines are mentioned, to the reply, add what the deadline is. If something has to be prepared before the next class, add that information too. List all of this in an unordered list. Do not summarize or remention any point."} ]
            message.append(
                {"role": "user", "content": f'{topic}'}
            )
            flag = True
            count = 0
            while flag:
                try:
                    chat = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k", messages=message
                    )
                    flag = False
                except:
                    if count <= 3:
                        print("Error occured. Trying again...")
                        count += 1
                        continue
                    else:
                        print("Error occured. Exiting...")
                        break
            reply = chat.choices[0].message.content
            message = []

            important_information.append(reply)

        # print(topic_and_keywords)

        print("Printing length of important information array and the array itself")
        for i in important_information:
            print(len(i))
            print('\n')
            print(i)   
            print('\n')


        print(len(topics))
        print(len(topic_headings))
        print(len(topic_keywords))
        print(len(important_information))

        json_data = []
        for i in range(len(topics)):
            item = {
                'title': topic_headings[i],
                'topic': topics[i],
                'keywords': topic_keywords[i],
                'important_information': important_information[i]
            }
            json_data.append(item)

        with open('final_output.json', 'w') as file:
            json.dump(json_data, file, indent=4)
        with open('final_output.json', 'r') as file:
            json_content = file.read()

        lecture_data = json.loads(json_content)
        print("Printing the lecture datas")
        print(lecture_data)

        print("Saving the lecture data to the database...")
        for item in lecture_data:
            topic_title = item['title']
            topic_description = item['topic']
            topic_keywords = json.dumps(item['keywords'])
            important_information = item['important_information']
            lecture_id_getter = Lecture.query.filter_by(user_id=user.id, study_material_id=row.id, title=title, lecture_number=lecture_number).first()
            lecture_data = LectureData(lecture_id=lecture_id_getter.id, topic_title=topic_title, topic_description=topic_description, topic_keywords=topic_keywords, important_information=important_information)
            db.session.add(lecture_data)
            db.session.commit()
        
        print("Saving the lecture data to the database... Done")

        return redirect('/classes?course={}'.format(courseName))

@app.route("/topic-explanation", methods=["GET", "POST"])
def getTopicExplanation():
    openai.api_key = "<API_KEY_FROM_OPENAI>"
    data = request.get_json()
    topic = data['text']
    topic_para = data['topic_para']
    action = data['action']

    if action == 'easy':
        print("Easy explanation")
        message = [ {"role": "system", "content": "I will give you a paragraph and a word in that paragraph and you have to explain the word in the context of the given paragraph as if you are explaining it to a 10 year old kid but do not use the informal language. If possible, add 1 or 2 examples to explain it better. Do not explain it out of the context."} ,
                   {"role": "user", "content": f' Paragraph is {topic_para} and the word is {topic}'},
                ]
        
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k", messages=message
        )

        reply = chat.choices[0].message.content

        response = {"message": reply}
    else:
        print("Detailed explanation")
        message = [ {"role": "system", "content": "I will give you a paragraph and a word in that paragraph and you have to explain the word in detail and in the context of the given paragraph. Explain as if you are explaining it to a PHD holder or a scholar. If possible, add 1 or 2 examples to explain it better. Do not explain it out of the context."} ,
                   {"role": "user", "content": f' Paragraph is {topic_para} and the word is {topic}'},
                ]
        
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k", messages=message
        )

        reply = chat.choices[0].message.content

        response = {"message": reply}
    return jsonify(response)

@app.route("/download", methods=["GET"])
def download():
    print("download")
    user_email = request.args.get('userEmail')
    courseName = request.args.get('courseName')
    lecture_number = request.args.get('lectureNumber')
    filename = request.args.get('filename')
    # if courseName == '':
    #     return "CourseName not found in query params", 400
    return send_file("uploads/"+ f"{user_email}/" + f"{courseName}/" + f"{lecture_number}/" + "audio/" + f"{filename}" + '.wav', as_attachment=True)

@app.route("/courses/transcript", methods=["GET"])
def getFilesToGenerateTranscript():
    courses = read_file_as_dict(LATEST_COURSE_JSON_NAME)
    return jsonify(courses)

@app.route("/courses")
def getCourses():
    count = 1
    courses = []
    for entry in os.scandir("course"):
        dict = {"courseId": "COEN-" + str(count), "courseName": entry.name, "createAt": get_creation_time(entry)}
        count = count + 1
        courses.append(dict)

    json_data = json.dumps(courses)
    return json_data

@app.route("/classes", methods=["GET"])
def lectures():
    print("We are here")
    course = request.args.get('course')
    user = User.query.get(session['user_id'])
    course_id_getter = StudyMaterial.query.filter_by(user=user, courseName=course).first()
    lectures = Lecture.query.filter_by(study_material_id=course_id_getter.id).all()
    # lecture_data = LectureData.query.filter_by(lecture_id=lectures[0].id).all()
    # lecture_description = lecture_data[0].topic_description
    # if lecture_description == '':
    #     lecture_description = lecture_data[1].topic_description[:270] + "...."

    lecture_descriptions = []
    for lecture in lectures:
        lecture_data = LectureData.query.filter_by(lecture_id=lecture.id).all()
        lecture_descriptions.append((lecture_data[1].topic_description)[:270] + "....")

    print(len(lectures))
    print(len(lecture_descriptions))
    return render_template('classes.html', lectures=lectures, course=course, lecture_descriptions=lecture_descriptions)

@app.route("/course/summary", methods=["GET"])
def getCourseSummary():
    courses = []
    courseName = request.args.get('courseName')
    if courseName == '':
        return "CourseName not found in query params", 400

    recording = request.args.get('recordingId')
    if recording == '':
        return "recording not found in query params", 400

    recordingDir = "course/" + courseName + "/" + recording

    file_names = [file for file in os.listdir(recordingDir) if os.path.isfile(os.path.join(recordingDir, file))]
    for file_name in file_names:
        if file_name.endswith("json"):

            with open(recordingDir + "/" + file_name, 'r') as file:
                json_data = json.load(file)
                keywords = json_data[0]['keywords']
                summary = json_data[1]['summary']
                return render_template('notes.html', keywords=keywords, summary=summary)

    return render_template('notes.html', keywords="['none']", summary="Not processed yet.")

@app.route("/courses/transcript", methods=["POST"])
def saveTranscriptForCourse():
    courseName = request.args.get('courseName')
    if(courseName == ''):
        return "Course Name is not Specified", 400

    request_data = request.data
    request_json = json.loads(request_data)

    # Write the request data to a JSON file
    with open("course/" + courseName + '.json', 'w') as file:
        json.dump(request_json, file)

    courses = read_file_as_dict(LATEST_COURSE_JSON_NAME)
    courses.remove(courseName)
    write_dict_to_file(LATEST_COURSE_JSON_NAME, courses)

    return "Saved Transcript"

@app.route('/notes')
def notes():
    lecture_number = request.args.get('lecture_number')
    courseName = request.args.get('courseName')
    user = User.query.get(session['user_id'])
    course_id_getter = StudyMaterial.query.filter_by(user=user, courseName=courseName).first()
    previous_lectures = Lecture.query.filter_by(study_material_id=course_id_getter.id).all()
    lecture_id_getter = Lecture.query.filter_by(user_id=user.id, study_material_id=course_id_getter.id, lecture_number=lecture_number).first()
    lecture_data = LectureData.query.filter_by(lecture_id=lecture_id_getter.id).all()
    lecture_data.pop(0)

    lecture_descriptions = []
    for lecture in previous_lectures:
        lecture_data = LectureData.query.filter_by(lecture_id=lecture.id).all()
        lecture_descriptions.append((lecture_data[1].topic_title)[:270] + "....")

    return render_template('notes.html', course_id_getter = course_id_getter, lecture_data=lecture_data, lecture_descriptions=previous_lectures)

@app.route('/addCourseForm' , methods=['GET', 'POST'])
def addCourseForm():
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login'))

        courseName = request.form.get('courseName')
        title = request.form.get('title')
        if courseName == '' or title == '':
            error = " Please fill all the details"
            return render_template('addacourse.html', response=error)
        
        # Create a new study material associated with the current user
        user = User.query.get(session['user_id'])
        study_material = StudyMaterial(user=user, courseName=courseName, title=title)
        db.session.add(study_material)
        db.session.commit()

        directory = "uploads/" + user.email + "/" + courseName
        os.mkdir(directory)
        
        return redirect(url_for('dashboard'))
    return render_template('addacourse.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
