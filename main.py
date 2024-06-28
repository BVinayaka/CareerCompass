import csv
import os
import re
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request, redirect, session,url_for, flash
from flask_mail import Mail, Message
import secrets
from pymongo import MongoClient
import bcrypt
import random
import string
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
from flask import flash
import cv2
import numpy as np
import base64
import requests
from tqdm import tqdm
from openpyxl import Workbook
import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from pymongo import MongoClient
from tqdm import tqdm
from functools import wraps
from skills_extraction import skills_extractor
app = Flask(__name__)
app.secret_key = os.getenv('app.secret_key')
load_dotenv()
from email.message import EmailMessage

client = MongoClient(os.getenv('uri'))
db = client['Major_Project']
users_collection = db['students']
profiles_collection = db['profiles'] 
sessions_collection = db['sessions']  
# answer_collection=db['quiz']
collection = db['careerOption']


headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWU5ODcyMTMtZmEyYy00NWU1LThjNmEtODg1OTc3ZjRhYjZlIiwidHlwZSI6ImFwaV90b2tlbiJ9.V2B4wZtSze1HlRD6m6NcoIr1DWQUiI4ZJcIhuXlWBF4"}

url = "https://api.edenai.run/v2/text/question_answer"

@app.route('/')
def index():
    return render_template('index.html', section='home')

@app.route('/result_page1')
def result():
    return render_template('result.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password1 = request.form['password']
        password2 = request.form['confirm_password']

        if password1 != password2:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')

        if not (len(password1) >= 8 and any(c.isupper() for c in password1)
                and any(c.islower() for c in password1) and any(c.isdigit() for c in password1)
                and any(c in string.punctuation for c in password1)):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters.', 'error')
            return render_template('signup.html')

        hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already exists!', 'signup_error')
            return render_template('signup.html')

        access_code = ''.join(random.choices(string.digits, k=6))

        session['access_code'] = access_code
        session['access_code_created_at'] = datetime.now()

        session['name'] = name
        session['email'] = email
        session['mobile'] = mobile
        session['password'] = hashed_password

        send_verification_email(email, access_code)

        return redirect('/validate') 
    return render_template('signup.html')

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'POST':
        entered_code = request.form['code']
        access_code = session.get('access_code')
        access_code_created_at = session.get('access_code_created_at')
        if access_code and access_code == entered_code:
            if access_code_created_at:
                access_code_created_at = access_code_created_at.replace(tzinfo=timezone('UTC'))
                if datetime.now(timezone('UTC')) - access_code_created_at <= timedelta(seconds=60):
                    name = session.pop('name', None)
                    email = session.pop('email', None)
                    mobile = session.pop('mobile', None)
                    password = session.pop('password', None)
                    user_data = {
                        'name': name,
                        'email': email,
                        'mobile': mobile,
                        'password': password
                    }
                    users_collection.insert_one(user_data)
                    return jsonify(success=True)
                else:
                    return jsonify(success=False, message='Access code has expired!')
            else:
                return jsonify(success=False, message='Access code creation time not found!')
        else:
            return jsonify(success=False, message='Invalid access code!')
    return render_template('validate.html')

@app.route('/resend', methods=['POST','GET'])
def resend_verification_code():
    try:
        access_code = ''.join(random.choices(string.digits, k=6))
        session['access_code'] = access_code
        session['access_code_created_at'] = datetime.now()
        send_verification_email(session['email'], access_code)

        flash('Verification code resent successfully!', 'success')
    except Exception as e:
        print('An error occurred while resending the verification code:', e)
        flash('Failed to resend verification code. Please try again later.', 'error')

    return redirect('/validate')

def generate_session_id():
    return secrets.token_urlsafe(16)

def create_session(email):
    session_id = generate_session_id()
    session['session_id'] = session_id
    session['email'] = email
    return session_id

def invalidate_session():
    session.clear()

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            invalidate_sessions(email)
            session_id = create_session(email)
            session['user_id'] = str(user['_id'])
            session['email'] = email
            return redirect('/')
        else:
            flash('Invalid email or password!', 'login_error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/resume')
@login_required
def resume():
    return render_template('resume.html')


@app.route('/quiz')
def quiz():
    return render_template('quiz.html',questions=correct_answers.keys())

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        answers = []
        for i in range(10): 
            answer = request.form.get(f'answer-{i+1}')
            answers.append(answer)
        df = pd.DataFrame({'Question': [f'Question {i+1}' for i in range(10)],
                           'Answer': answers})
        excel_file = 'user_answers.xlsx'
        df.to_excel(excel_file, index=False)
        return 'Answers submitted successfully!'


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        firstname = request.form['firstName']
        lastname = request.form['lastName']
        mobile = request.form['mobile']
        addr = request.form['addr']
        email = request.form['email']
        dob = request.form['dob']
        education = request.form['education']
        country = request.form['country']
        state = request.form['state']
        profile_data = {
            'firstname': firstname,
            'lastname': lastname,
            'mobile': mobile,
            'address': addr,
            'email': email,
            'dob': dob,
            'education': education,
            'country': country,
            'state': state
        }

        try:
            profiles_collection.insert_one(profile_data)
            flash('Profile saved successfully!', 'success')
            return redirect('/quiz')
        except Exception as e:
            flash(f'Error saving profile: {str(e)}', 'error')
            return redirect('/edit_profile') 
    return render_template('profile.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            verification_code = ''.join(random.choices(string.digits, k=6))
            users_collection.update_one({'email': email}, {'$set': {'verification_code': verification_code}}, upsert=True)
            send_verification_email(email, verification_code)
            flash('Verification code sent to your email.')
            return redirect(url_for('verify_code', email=email))
        else:
            flash('The provided email is not registered. Please check and try again.','validate_error')
            return render_template('forgot_password.html')

    return render_template('forgot_password.html')

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        email = request.form['email']
        user_code = request.form['verification_code']  
        user = users_collection.find_one({'email': email})
        if user:
            stored_code = user.get('verification_code')
            
            if user_code == stored_code:
                return redirect(url_for('set_new_password', email=email))
            else:
                flash('Invalid verification code. Please try again.', 'danger')
        else:
            flash('Email not found. Please check your email.', 'danger')
    
    email = request.args.get('email')
    return render_template('verify_code.html', email=email)

@app.route('/set_new_password', methods=['GET', 'POST'])
def set_new_password():
    if request.method == 'POST':
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']
        password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#@$!%*?&])[A-Za-z\d@$#!%*?&]{7,12}$')

        if password1 != password2:
            flash('Passwords do not match. Please try again.')
        elif not password_regex.match(password1):
            flash('Password must be 7 to 12 characters long, include one digit, one lowercase letter, one uppercase letter, and one special character.')
        else:
            hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
            users_collection.update_one({'email': email}, {'$set': {'password': hashed_password}})
            flash('Password updated successfully.')
            return redirect(url_for('login')) 

    email = request.args.get('email')
    return render_template('set_new_password.html', email=email)

def send_verification_email(email, access_code):
    smtp_server = 'smtp.gmail.com'  
    smtp_port = 587  
    sender_email = os.getenv('EMAIL_ADDRESS')  
    sender_password = os.getenv('EMAIL_PASSWORD')  

    # Create message
    message = EmailMessage()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = 'Your Career Campus App Verification Code Inside'

    message.set_content(f"""
Dear Sir,

Thank you for registering with the Career Campus App!

Your verification code is: {access_code}

Please enter this code in the app to complete your registration.

If you have any questions or need further assistance, feel free to contact our support team.

Best regards,
The Career Campus Team
""")

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, email, message.as_string())
        print('Verification email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the verification email:', e)
    finally:
        server.quit()

def invalidate_sessions(email):
    sessions_collection.delete_many({'email': email})


def create_session(email):
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    session_data = {
        'email': email,
        'session_id': session_id,
        'created_at': datetime.now()
    }
    sessions_collection.insert_one(session_data)
    return session_id



def crop_face(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        print("Error: No face detected in the input image.")
        return None
    x, y, w, h = faces[0]
    extended_x = max(0, x - int(0.2 * w))
    extended_y = max(0, y - int(0.2 * h))
    extended_w = min(image.shape[1] - extended_x, int(1.4 * w))
    extended_h = min(image.shape[0] - extended_y, int(1.4 * h))
    cropped_face = image[extended_y:extended_y+extended_h, extended_x:extended_x+extended_w]
    return cropped_face

def create_passport_photo(image):
    # Check if a face is detected
    if image is None:
        print("Error: Cannot create passport photo because no face was detected.")
        return None
    passport_size = (80, 100)
    face_aspect_ratio = image.shape[1] / image.shape[0]
    head_shoulder_aspect_ratio = passport_size[0] / passport_size[1]
    if face_aspect_ratio > head_shoulder_aspect_ratio:
        scale_factor = passport_size[0] / image.shape[1]
    else:
        scale_factor = passport_size[1] / image.shape[0]
    resized_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
    white_background = np.full((passport_size[1], passport_size[0], 3), 255, dtype=np.uint8)
    x_offset = (passport_size[0] - resized_image.shape[1]) // 2
    y_offset = (passport_size[1] - resized_image.shape[0]) // 2
    white_background[y_offset:y_offset+resized_image.shape[0], x_offset:x_offset+resized_image.shape[1]] = resized_image
    return white_background


@app.route('/process_photo', methods=['POST'])
def process_photo():
    image_data_uri = request.form['imageData']
    encoded_data = image_data_uri.split(',')[1]
    decoded_data = base64.b64decode(encoded_data)
    nparr = np.frombuffer(decoded_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cropped_face = crop_face(image)
    passport_photo = create_passport_photo(cropped_face)
    _, buffer = cv2.imencode('.png', passport_photo)
    output_image_data_uri = 'data:image/png;base64,' + base64.b64encode(buffer).decode()
    return jsonify({'outputImage': output_image_data_uri})

correct_answers = {
    "question-1": "Java",
    "question-2": "To eliminate data duplication",
    "question-3": "To block unauthorized access",
    "question-4": "PHP",
    "question-5": "Agile",
    "question-6": "Managing project timelines",
    "question-7": "Structured Query Language",
    "question-8": "Asymmetric encryption",
    "question-9": "HTML",
    "question-10": "To detect vulnerabilities in a system",
    "question-11": "Product, Price, Place, Promotion",
    "question-12": "Balance sheet",
    "question-13": "Marketing and advertising",
    "question-14": "Providing strategic advice and solutions to improve organizational performance",
    "question-15": "Current Ratio",
    "question-16": "It is typically funded by venture capital or angel investors",
    "question-17": "Market penetration",
    "question-18": "To assess internal strengths and weaknesses and external opportunities and threats",
    "question-19": "Return on Equity (ROE)",
    "question-20": "Product launch",
    "question-21": "Providing direct patient care",
    "question-22": "Physician Assistant",
    "question-23": "Dispensing medications and providing medication counseling",
    "question-24": "Physical Therapist",
    "question-25": "Conducting experiments and studies to advance medical knowledge",
    "question-26": "Registered Nurse",
    "question-27": "Helping patients regain mobility and functionality",
    "question-28": "Registered Nurse",
    "question-29": "Administering medications as prescribed",
    "question-30": "Physician Assistant",
    "question-31": "Inquiry-based learning",
    "question-32": "Designing educational materials and lesson plans",
    "question-33": "Differentiation",
    "question-34": "A system of guaranteed employment for faculty members",
    "question-35": "Managing school operations and personnel",
    "question-36": "Middle school",
    "question-37": "Constructivism",
    "question-38": "Use of mixed-age classrooms",
    "question-39": "To evaluate student learning at the end of an instructional unit",
    "question-40": "Problem-based learning",
    "question-41": "Adobe Illustrator",
    "question-42": "User Interface",
    "question-43": "Basic layout schematic",
    "question-44": "Autodesk Maya",
    "question-45": "Fashion Designer",
    "question-46": "Rendering",
    "question-47": "Balance",
    "question-48": "Arrangement of text elements",
    "question-49": "UI/UX Design",
    "question-50": "To plan the sequence of scenes",
    "question-51": "Developing mechanical systems and devices",
    "question-52": "Civil Engineering",
    "question-53": "Developing electrical circuits and systems",
    "question-54": "Architect",
    "question-55": "Developing sustainable waste management systems",
    "question-56": "Environmental Engineering",
    "question-57": "Managing construction projects",
    "question-58": "Structural analysis and design",
    "question-59": "Mechanical Engineering",
    "question-60": "Designing mechanical systems",
    "question-61": "Psychologist",
    "question-62": "Social Worker",
    "question-63": "Historian",
    "question-64": "Studying human societies and cultures",
    "question-65": "Understanding and protecting the environment",
    "question-66": "Environmental Scientist",
    "question-67": "Renewable Energy Engineer",
    "question-68": "Environmental Policy Analyst",
    "question-69": "Developing strategies for sustainable practices",
    "question-70": "Organizing and overseeing events, conferences, and meetings",
    "question-71": "Event Planner",
    "question-72": "Travel Agent",
    "question-73": "Planning and coordinating events",
    "question-74": "Restaurant Manager",
    "question-75": "Enforcing laws, investigating crimes, and maintaining public order",
    "question-76": "Paralegal",
    "question-77": "Assisting lawyers with legal research and case preparation",
    "question-78": "Probation Officer",
    "question-79": "Lawyer/Attorney",
    "question-80": "240 m",
    "question-81": "21.6 m",
    "question-82": "Rs. 6400",
    "question-83": "16",
    "question-84": "700 apples",
    "question-85": "Friday",
    "question-86": "6.25",
    "question-87": "1200",
    "question-88": "2",
    "question-89": "4 years",
    "question-90": "756",
    "question-91": "4"
}


@app.route('/submit_form1', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form.get('userNameInput')
        email = request.form.get('userEmailInput')
        phone = request.form.get('phone')
        address = request.form.get('address')
        education = request.form.get('education')
        hobbies = request.form.get('hobbies')
        profile_data = { 
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'education': education,
            'hobbies': hobbies
        }
        profiles_collection.insert_one(profile_data)
        return jsonify({'message': 'Form data saved successfully'}), 200
    

def send_email1(accuracy, last_row_pred, next_steps, pdf_file_path, recipient_email,name):
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    msg = EmailMessage()
    msg['Subject'] = 'Data Prediction Outcome and Action Plan'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg.set_content(f'''
Dear {name},

I hope this message finds you well.

I am writing to share the results of our latest prediction for your case. Based on our analysis, the prediction is as follows:
Prediction: {last_row_pred}

Additionally, here are the next steps we recommend:
{next_steps}

Please let me know if you have any questions or need further information.

Best regards,
Vinayaka Kamath
nnm22mc116@nmamit.in
''')
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='octet-stream', filename=os.path.basename(pdf_file_path))


    server = None
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email:', e)
    finally:
        if server:
            server.quit()


@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    data = request.form.to_dict()
    if not all(question in data for question in correct_answers):
        return jsonify({"error": "All questions must be answered."}), 400

    answers = {}
    for i, (question, submitted_answer) in enumerate(data.items(), start=1):
        correct_answer = correct_answers.get(question, "")
        answers[f"Answer{i}"] = 1 if submitted_answer == correct_answer else 0
    answers["Career Option"] = "Design"

    collection.insert_one(answers)
    return redirect('/result_page')

def suggest_next_steps(current_status, interest):
    if current_status == "SSLC":
        if interest == "Technology":
            return ["PUC", "Engineering", "MTech", "Job Search"]
        elif interest == "Business":
            return ["PUC", "Business Management Course", "Job Search"]
        elif interest == "Healthcare":
            return ["PUC", "Medical Entrance Exam", "Medical School", "Residency", "Job Search"]
        elif interest == "Teaching":
            return ["PUC", "Bachelor's in Education", "Teaching Credential", "Job Search"]
        elif interest == "Design":
            return ["PUC", "Bachelor's in Design", "Internship", "Job Search"]
        elif interest == "Engineering":
            return ["PUC", "Engineering Degree", "Job Search"]
        elif interest == "Social":
            return ["PUC", "Bachelor's in Social Work", "Internship", "Job Search"]
        else:
            return ["PUC", f"Bachelor's in {interest}", "Job Search"]
    elif current_status == "PUC":
        if interest == "Technology":
            return ["Engineering", "MTech", "Job Search"]
        elif interest == "Business":
            return ["Business Management Course", "Job Search"]
        elif interest == "Healthcare":
            return ["Medical Entrance Exam", "Medical School", "Residency", "Job Search"]
        elif interest == "Teaching":
            return ["Bachelor's in Education", "Teaching Credential", "Job Search"]
        elif interest == "Design":
            return ["Bachelor's in Design", "Internship", "Job Search"]
        elif interest == "Engineering":
            return ["Engineering Degree", "Job Search"]
        elif interest == "Social":
            return ["Bachelor's in Social Work", "Internship", "Job Search"]
        else:
            return [f"Bachelor's in {interest}", "Job Search"]
    else:
        return ["Job search"]

@app.route('/result_page', methods=['GET'])
def result_page():
    latest_profile = profiles_collection.find().sort([('$natural', -1)]).limit(1)[0]
    recipient_email = latest_profile['email']
    current_status = latest_profile['education']
    name=latest_profile['name']
    cursor = collection.find({}, {'_id': 0})
    df = pd.DataFrame(list(cursor))
    df_encoded = pd.DataFrame()

    for i in tqdm(range(1, 91), desc="Encoding features"):
        column_name = f"Answer{i}"
        df_encoded = pd.concat([df_encoded, pd.get_dummies(df[column_name], prefix=column_name)], axis=1)

    df_encoded['Career Option'] = df['Career Option']
    df_encoded.dropna(subset=['Career Option'], inplace=True)

    X = df_encoded.drop("Career Option", axis=1)
    y = df_encoded["Career Option"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    svm_classifier = SVC(kernel='rbf', random_state=42)
    svm_classifier.fit(X_train, y_train)

    y_pred = svm_classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(accuracy)
    last_row = X.iloc[[-1]]
    last_row_pred = svm_classifier.predict(last_row)
    interest = last_row_pred[0]
    next_steps = suggest_next_steps(current_status, interest)
    
    if last_row_pred == "Technology":
        pdf_path = "PDF/Technology.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Business":
        pdf_path = "PDF/Business.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Healthcare":
        pdf_path = "PDF/Healthcare.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Teaching":
        pdf_path = "PDF/Teaching.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Design":
        pdf_path = "PDF/Design.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Engineering":
        pdf_path = "PDF/Engineering.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Social":
        pdf_path = "PDF/Social.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Hospital":
        pdf_path = "PDF/Hospital.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    elif last_row_pred == "Banking":
        pdf_path = "PDF/Banking.pdf"
        send_email1(accuracy, last_row_pred, next_steps, pdf_path, recipient_email,name)

    last_row_pred = last_row_pred.tolist() if isinstance(last_row_pred, np.ndarray) else last_row_pred

    return jsonify({
        'accuracy': accuracy,
        'last_row_prediction': last_row_pred,
        'next_steps': next_steps
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')

    text1 = "I need information related to Resume "
    text2 = "Please give me information related to Resume informations"

    payload = {
        "providers": "openai",
        "texts": [text1, text2],
        "question": question,
        "examples_context": "In 2017, U.S. life expectancy was 78.6 years.",
        "examples": [["What is human life expectancy in the United States?", "78 years."]],
        "fallback_providers": ""
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        answer = result['openai']['answers'][0]
    else:
        answer = "Sorry, something went wrong."

    return jsonify({'answer': answer})



@app.route('/job')
@login_required
def job():
    return render_template('job.html')


UPLOAD_FOLDER = '/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


skill_category_mapping = {
    'c++': 'Software',
    'java': 'Software',
    'python': 'Software',
    'html': 'Web',
    'javascript': 'Software',
    'sql': 'Data',
    'system': 'IT',
    'technical': 'IT',
    'english': 'Communication',
    'algorithms': 'Programming',
    'analysis': 'Analysis',
    'js': 'Software',
    'programming': 'Programming',
    'testing': 'Testing',
    'teaching': 'Teaching',
    'support': 'Support',
    'management': 'Management',
    'engineering': 'Engineering',
    'research': 'Research',
    'design': 'Design',
    'consulting': 'Consulting',
    'marketing': 'Marketing',
    'sales': 'Sales',
    'finance': 'Finance',
    'accounting': 'Accounting',
    'health': 'Health',
    'nursing': 'Nursing',
    'administration': 'Administration',
    'legal': 'Legal',
    'writing': 'Writing',
    'editing': 'Editing',
    'product': 'Product',
    'project': 'Project',
    'operations': 'Operations',
    'customer': 'Customer',
    'human resources': 'Human Resources',
    'it': 'IT',
    'software': 'Software',
    'hardware': 'Hardware',
    'network': 'Network',
    'security': 'Security',
    'data': 'Data',
    'business': 'Business',
    'logistics': 'Logistics',
    'supply chain': 'Supply Chain',
    'construction': 'Construction',
    'real estate': 'Real Estate',
    'manufacturing': 'Manufacturing',
    'quality': 'Quality',
    'training': 'Training',
    'education': 'Education',
    'media': 'Media',
    'communications': 'Communication',
    'assistant': 'Assistant',
    'trainee': 'Trainee',
    'communication': 'Teaching',
    'negotiation skills': 'Business',
    'leadership skills': 'Business',
    'cloud computing': 'IT',
    'machine learning': 'Data',
    'artificial intelligence': 'Data',
    'deep learning': 'Data',
    'big data': 'Data',
    'data analysis': 'Data',
    'data visualization': 'Data',
    'data science': 'Data',
    'data mining': 'Data',
    'business intelligence': 'Data',
    'statistical analysis': 'Analysis',
    'excel': 'Data',
    'tableau': 'Data',
    'power bi': 'Data',
    'sap': 'IT',
    'oracle': 'IT',
    'linux': 'IT',
    'windows': 'IT',
    'unix': 'IT',
    'aws': 'IT',
    'azure': 'IT',
    'gcp': 'IT',
    'docker': 'IT',
    'kubernetes': 'IT',
    'devops': 'IT',
    'agile': 'Project',
    'scrum': 'Project',
    'kanban': 'Project',
    'jira': 'Project',
    'confluence': 'Project',
    'project management': 'Project',
    'pmp': 'Project',
    'prince2': 'Project',
    'six sigma': 'Quality',
    'lean': 'Quality',
    'iso': 'Quality',
    'risk management': 'Project',
    'change management': 'Project',
    'stakeholder management': 'Project',
    'budgeting': 'Finance',
    'forecasting': 'Finance',
    'financial analysis': 'Finance',
    'financial modeling': 'Finance',
    'investment': 'Finance',
    'portfolio management': 'Finance',
    'accounting principles': 'Accounting',
    'taxation': 'Accounting',
    'auditing': 'Accounting',
    'payroll': 'Accounting',
    'bookkeeping': 'Accounting',
    'compliance': 'Legal',
    'contract law': 'Legal',
    'corporate law': 'Legal',
    'intellectual property': 'Legal',
    'litigation': 'Legal',
    'legal research': 'Legal',
    'legal writing': 'Legal',
    'case management': 'Legal',
    'mediation': 'Legal',
    'arbitration': 'Legal',
    'labor law': 'Legal',
    'employment law': 'Legal',
    'real estate law': 'Legal',
    'family law': 'Legal',
    'criminal law': 'Legal',
    'healthcare law': 'Legal',
    'environmental law': 'Legal',
    'international law': 'Legal',
    'writing skills': 'Writing',
    'creative writing': 'Writing',
    'technical writing': 'Writing',
    'copywriting': 'Writing',
    'content writing': 'Writing',
    'proofreading': 'Editing',
    'copy editing': 'Editing',
    'substantive editing': 'Editing',
    'developmental editing': 'Editing',
    'manuscript evaluation': 'Editing',
    'project planning': 'Project',
    'project scheduling': 'Project',
    'project coordination': 'Project',
    'task management': 'Project',
    'time management': 'Project',
    'resource management': 'Project',
    'vendor management': 'Project',
    'supply chain management': 'Supply Chain',
    'procurement': 'Supply Chain',
    'inventory management': 'Supply Chain',
    'warehouse management': 'Supply Chain',
    'logistics management': 'Supply Chain',
    'transportation': 'Supply Chain',
    'demand planning': 'Supply Chain',
    'order fulfillment': 'Supply Chain',
    'material handling': 'Supply Chain',
    'production planning': 'Manufacturing',
    'manufacturing processes': 'Manufacturing',
    'lean manufacturing': 'Manufacturing',
    'continuous improvement': 'Manufacturing',
    'quality control': 'Quality',
    'quality assurance': 'Quality',
    'inspection': 'Quality',
    'testing procedures': 'Quality',
    'problem solving': 'Quality',
    'root cause analysis': 'Quality',
    'corrective actions': 'Quality',
    'preventive actions': 'Quality',
    'training development': 'Training',
    'instructional design': 'Training',
    'elearning': 'Training',
    'curriculum development': 'Training',
    'classroom management': 'Teaching',
    'lesson planning': 'Teaching',
    'student assessment': 'Teaching',
    'education administration': 'Education',
    'academic advising': 'Education',
    'career counseling': 'Education',
    'library science': 'Education',
    'educational technology': 'Education',
    'digital marketing': 'Marketing',
    'social media marketing': 'Marketing',
    'content marketing': 'Marketing',
    'seo': 'Marketing',
    'sem': 'Marketing',
    'email marketing': 'Marketing',
    'affiliate marketing': 'Marketing',
    'product marketing': 'Marketing',
    'market research': 'Marketing',
    'brand management': 'Marketing',
    'public relations': 'Marketing',
    'advertising': 'Marketing',
    'salesforce': 'Sales',
    'crm': 'Sales',
    'lead generation': 'Sales',
    'prospecting': 'Sales',
    'negotiation': 'Sales',
    'closing deals': 'Sales',
    'account management': 'Sales',
    'customer relationship management': 'Sales',
    'customer service': 'Customer',
    'customer support': 'Customer',
    'help desk': 'Customer',
    'technical support': 'Support',
    'it support': 'Support',
    'desktop support': 'Support',
    'network support': 'Support',
    'user support': 'Support',
    'application support': 'Support',
    'technical troubleshooting': 'Support',
    'system administration': 'IT',
    'network administration': 'Network',
    'database administration': 'Data',
    'cloud administration': 'IT',
    'it operations': 'IT',
    'it management': 'IT',
    'it strategy': 'IT',
    'it governance': 'IT',
    'it auditing': 'IT',
    'it security': 'Security',
    'cybersecurity': 'Security',
    'information security': 'Security',
    'network security': 'Security',
    'application security': 'Security',
    'endpoint security': 'Security',
    'security compliance': 'Security',
    'penetration testing': 'Security',
    'ethical hacking': 'Security',
    'incident response': 'Security',
    'disaster recovery': 'IT',
    'business continuity': 'IT',
    'risk assessment': 'Security',
    'vulnerability management': 'Security',
    'firewall management': 'Security',
    'intrusion detection': 'Security',
    'security monitoring': 'Security',
    'forensics': 'Security',
    'encryption': 'Security',
    'cryptography': 'Security',
    'identity management': 'Security',
    'access control': 'Security',
    'policy development': 'Management',
    'procedure development': 'Management',
    'process improvement': 'Management',
    'strategic planning': 'Management',
    'operational planning': 'Operations',
    'resource planning': 'Operations',
    'capacity planning': 'Operations',
    'workforce planning': 'Operations',
    'organizational development': 'Human Resources',
    'talent management': 'Human Resources',
    'performance management': 'Human Resources',
    'succession planning': 'Human Resources',
    'compensation': 'Human Resources',
    'benefits administration': 'Human Resources',
    'employee relations': 'Human Resources',
    'recruitment': 'Human Resources',
    'onboarding': 'Human Resources',
    'offboarding': 'Human Resources',
    'training and development': 'Training',
    'employee engagement': 'Human Resources',
    'workplace diversity': 'Human Resources',
    'labor relations': 'Human Resources',
    'employee retention': 'Human Resources',
    'organizational behavior': 'Human Resources',
    'job analysis': 'Human Resources',
    'job design': 'Human Resources',
    'talent acquisition': 'Human Resources',
    'workforce analytics': 'Human Resources',
    'employee health': 'Health',
    'employee safety': 'Health',
    'occupational health': 'Health',
    'ergonomics': 'Health',
    'public health': 'Health',
    'epidemiology': 'Health',
    'biostatistics': 'Health',
    'health policy': 'Health',
    'health administration': 'Health',
    'clinical research': 'Research',
    'clinical trials': 'Research',
    'medical research': 'Research',
    'pharmaceutical research': 'Research',
    'biomedical research': 'Research',
    'genomics': 'Research',
    'proteomics': 'Research',
    'biotechnology': 'Research',
    'nanotechnology': 'Research',
    'bioinformatics': 'Data',
    'biometrics': 'Data',
    'molecular biology': 'Research',
    'cell biology': 'Research',
    'immunology': 'Research',
    'virology': 'Research',
    'microbiology': 'Research',
    'biochemistry': 'Research',
    'neuroscience': 'Research',
    'pharmacology': 'Research',
    'toxicology': 'Research',
    'pathology': 'Research',
    'physiology': 'Research',
    'anatomy': 'Research',
    'genetics': 'Research',
    'epigenetics': 'Research',
    'bioengineering': 'Engineering',
    'biomedical engineering': 'Engineering',
    'chemical engineering': 'Engineering',
    'civil engineering': 'Engineering',
    'electrical engineering': 'Engineering',
    'mechanical engineering': 'Engineering',
    'aerospace engineering': 'Engineering',
    'nuclear engineering': 'Engineering',
    'environmental engineering': 'Engineering',
    'materials science': 'Engineering',
    'metallurgy': 'Engineering',
    'nanomaterials': 'Engineering',
    'polymer science': 'Engineering',
    'structural engineering': 'Engineering',
    'transportation engineering': 'Engineering',
    'geotechnical engineering': 'Engineering',
    'hydraulic engineering': 'Engineering',
    'hydrology': 'Engineering',
    'water resources': 'Engineering',
    'sustainable engineering': 'Engineering',
    'renewable energy': 'Engineering',
    'energy systems': 'Engineering',
    'power systems': 'Engineering',
    'control systems': 'Engineering',
    'robotics': 'Engineering',
    'automation': 'Engineering',
    'mechatronics': 'Engineering',
    'embedded systems': 'Engineering',
    'vlsi': 'Engineering',
    'fpga': 'Engineering',
    'circuit design': 'Engineering',
    'pcb design': 'Engineering',
    'electronics': 'Engineering',
    'optoelectronics': 'Engineering',
    'photovoltaics': 'Engineering',
    'solar energy': 'Engineering',
    'wind energy': 'Engineering',
    'geothermal energy': 'Engineering',
    'hydropower': 'Engineering',
    'energy efficiency': 'Engineering',
    'smart grid': 'Engineering',
    'energy storage': 'Engineering',
    'batteries': 'Engineering',
    'fuel cells': 'Engineering',
    'power electronics': 'Engineering',
    'electric vehicles': 'Engineering',
    'hybrid vehicles': 'Engineering',
    'autonomous vehicles': 'Engineering',
    'aviation': 'Engineering',
    'space exploration': 'Engineering',
    'satellite technology': 'Engineering',
    'telecommunications': 'Engineering',
    'wireless communication': 'Engineering',
    'networking': 'Network',
    'internet of things': 'Engineering',
    'sensor networks': 'Engineering',
    'embedded systems programming': 'Engineering',
    'firmware development': 'Engineering',
    'real-time systems': 'Engineering',
    'digital signal processing': 'Engineering',
    'image processing': 'Engineering',
    'speech processing': 'Engineering',
    'computer vision': 'Engineering',
    'pattern recognition': 'Engineering',
    'augmented reality': 'Engineering',
    'virtual reality': 'Engineering',
    'haptics': 'Engineering',
    'human-computer interaction': 'Engineering',
    'user experience': 'Design',
    'user interface design': 'Design',
    'interaction design': 'Design',
    'information architecture': 'Design',
    'usability testing': 'Design',
    'graphic design': 'Design',
    'visual design': 'Design',
    'web design': 'Web',
    'mobile app design': 'Design',
    'print design': 'Design',
    'branding': 'Design',
    'typography': 'Design',
    'color theory': 'Design',
    'illustration': 'Design',
    'animation': 'Design',
    '3d modeling': 'Design',
    'motion graphics': 'Design',
    'video production': 'Media',
    'video editing': 'Media',
    'film production': 'Media',
    'post-production': 'Media',
    'audio production': 'Media',
    'sound design': 'Media',
    'music production': 'Media',
    'broadcasting': 'Media',
    'journalism': 'Media',
    'reporting': 'Media',
    'news writing': 'Media',
    'editing': 'Media',
    'photojournalism': 'Media',
    'social media': 'Media',
    'content creation': 'Media',
    'public speaking': 'Communication',
    'presentation skills': 'Communication',
    'interpersonal skills': 'Communication',
    'conflict resolution': 'Communication',
    'teamwork': 'Communication',
    'collaboration': 'Communication',
    'active listening': 'Communication',
    'feedback': 'Communication',
    'coaching': 'Communication',
    'mentoring': 'Communication',
    'motivation': 'Communication',
    'facilitation': 'Communication',
    'negotiation': 'Business',
    'influence': 'Business',
    'persuasion': 'Business',
    'networking': 'Business',
    'relationship building': 'Business',
    'customer relationship': 'Customer',
    'customer engagement': 'Customer',
    'customer loyalty': 'Customer',
    'customer retention': 'Customer',
    'customer satisfaction': 'Customer',
    'customer experience': 'Customer',
    'crm software': 'Customer',
    'customer analytics': 'Customer',
    'customer feedback': 'Customer',
    'customer insights': 'Customer',
    'customer journey mapping': 'Customer',
    'customer persona': 'Customer',
    'user research': 'Customer',
    'market analysis': 'Marketing',
    'competitive analysis': 'Marketing',
    'segmentation': 'Marketing',
    'targeting': 'Marketing',
    'positioning': 'Marketing',
    'branding strategy': 'Marketing',
    'value proposition': 'Marketing',
    'messaging': 'Marketing',
    'go-to-market strategy': 'Marketing',
    'campaign management': 'Marketing',
    'product launch': 'Marketing',
    'event planning': 'Marketing',
    'trade shows': 'Marketing',
    'public speaking': 'Marketing',
    'content strategy': 'Marketing',
    'content development': 'Marketing',
    'editorial calendar': 'Marketing',
    'content management': 'Marketing',
    'cms': 'Marketing',
    'wordpress': 'Web',
    'joomla': 'Web',
    'drupal': 'Web',
    'shopify': 'Web',
    'magento': 'Web',
    'wix': 'Web',
    'squarespace': 'Web',
    'web development': 'Web',
    'front-end development': 'Web',
    'back-end development': 'Web',
    'full-stack development': 'Web',
    'html5': 'Web',
    'css': 'Web',
    'css3': 'Web',
    'bootstrap': 'Web',
    'sass': 'Web',
    'less': 'Web',
    'javascript frameworks': 'Web',
    'angular': 'Web',
    'react': 'Web',
    'vue.js': 'Web',
    'ember.js': 'Web',
    'meteor': 'Web',
    'node.js': 'Web',
    'express': 'Web',
    'django': 'Web',
    'flask': 'Web',
    'ruby on rails': 'Web',
    'php': 'Web',
    'laravel': 'Web',
    'symfony': 'Web',
    'codeigniter': 'Web',
    'zend': 'Web',
    'java ee': 'Web',
    'spring': 'Web',
    'hibernate': 'Web',
    'grails': 'Web',
    'play': 'Web',
    'asp.net': 'Web',
    'dotnet': 'Web',
    'c#': 'Web',
    'vb.net': 'Web',
    'sql server': 'Data',
    'mysql': 'Data',
    'postgresql': 'Data',
    'mongodb': 'Data'
}

def preprocess_skills(skills):
    skills = skills.lower()
    skills = re.sub(r'[^a-z0-9\s\+\#]', '', skills)
    processed_skills = skills.split()
    return processed_skills

def match_skills_to_categories(processed_skills, skill_category_mapping):
    matched_categories = set()
    for skill in processed_skills:
        if skill in skill_category_mapping:
            matched_categories.add(skill_category_mapping[skill])
    print(matched_categories)
    return list(matched_categories)

def find_matching_rows(csv_file, matched_categories):
    matched_rows = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Keyword'] in matched_categories:
                if 'URL' in row and row['URL']:
                    url = row['URL']

                matched_rows.append(row)
    return matched_rows




@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        skills = skills_extractor(file_path)
        skills_string = ' '.join(skills)
        processed_skills = preprocess_skills(skills_string)
        print(processed_skills)
        matched_categories = match_skills_to_categories(processed_skills, skill_category_mapping)
        
        
        csv_file_path = 'updated_job_dataset2.csv'
        matched_rows = find_matching_rows(csv_file_path, matched_categories)

      
        return render_template('result.html', matched_rows=matched_rows)
if __name__ == '__main__':
    app.run(debug=True, port=5006)

