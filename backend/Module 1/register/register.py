import base64
import io
import firebase_admin
import pyrebase
import requests
from firebase_admin import credentials, firestore, auth
from flask import Flask, request, jsonify, json
from flask_cors import CORS

# App configuration
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Connect to firebase
cred = credentials.Certificate('sdpproject-b53f8-firebase-adminsdk-rmwnq-781363c1c6.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('config.json')))

# Initialize Firestore
db = firestore.client()


# API route for user registration
@app.route('/register/email', methods=['POST'])
def register_user():
    # Get user details from JSON request
    user_data = request.get_json()
    username = user_data.get('username')
    fname = user_data.get('fname')
    lname = user_data.get('lname')
    email = user_data.get('email')
    password = user_data.get('password')
    gender = user_data.get('gender')
    dob = user_data.get('dob')
    city = user_data.get('city')
    country = user_data.get('country')
    profile_pic = user_data.get('profile_pic')
    security_questions = user_data.get('security_questions')

    try:
        # Create admin user in Firebase Authentication
        if email.lower() == 'admin@firebase.com' and username.lower() == 'admin':
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            auth.set_custom_user_claims(user.uid, {'admin': True})
        else:
            # Create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            auth.set_custom_user_claims(user.uid, {'admin': False})

        # Create user document in Firestore
        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'uid': user.uid,
            'username': username,
            'email': email,
            'gender': gender,
            'fname': fname,
            'lname': lname,
            'dob': dob,
            'city': city,
            'country': country,
            'profile_pic': profile_pic,
            'claim': 'user'
        })

        # Prepare security questions and answers
        security_question_items = []
        for sq in security_questions:
            question = sq['question']
            answer = sq['answer']
            security_question_items.append({
                'M': {
                    'question': {'S': question},
                    'answer': {'S': answer}
                }
            })

        lambda_url = "https://prjap4iaq7.execute-api.us-east-1.amazonaws.com/prod/storesecurityquestions"
        payload = {'uid': user.uid, 'security_questions': security_question_items}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(lambda_url, data=json.dumps(payload), headers=headers)
        return response.json(), 200

    except Exception as e:
        errormessage = str(e)
        if 'EMAIL_EXISTS' in errormessage:
            return jsonify({"status": False, "response": 'Email already exists.'}), 400
        return jsonify({"status": False, 'error': str(e)}), 400


@app.route('/register/thirdparty', methods=['POST'])
def register_user_google():
    # Get user details from JSON request
    user_data = request.get_json()
    username = user_data.get('username')
    email = user_data.get('email')
    gender = user_data.get('gender')
    fname = user_data.get('fname')
    lname = user_data.get('lname')
    dob = user_data.get('dob')
    city = user_data.get('city')
    country = user_data.get('country')
    profile_pic = user_data.get('profile_pic')
    uid = user_data.get('uid')

    response = requests.get(profile_pic)

    # Read the response content as bytes
    image_bytes = response.content

    # Create an in-memory binary stream
    stream = io.BytesIO(image_bytes)

    # Read the stream as a base64-encoded string
    base64_data = base64.b64encode(stream.read()).decode('utf-8')

    # Create the data URI string with the appropriate MIME type
    data_uri = f"data:image/png;base64,{base64_data}"

    try:
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            'uid': uid,
            'username': username,
            'email': email,
            'fname': fname,
            'lname': lname,
            'gender': gender,
            'dob': dob,
            'city': city,
            'country': country,
            'profile_pic': data_uri
        })

        return jsonify({"status": True, "response": 'User registered successfully.'}), 200
    except Exception as e:
        return jsonify({"status": False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run()
