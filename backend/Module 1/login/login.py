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


@app.route('/login/email', methods=['POST'])
def login_user_with_email():
    # Get email and password from request
    userdata = request.get_json()
    email = userdata.get('email')
    password = userdata.get('password')

    try:
        # Sign in user with email and password
        user = pb.auth().sign_in_with_email_and_password(email, password)
        token = user['idToken']

        # check if user is admin
        claims = auth.verify_id_token(token)
        if claims['admin']:
            claim = 'admin'
        else:
            claim = 'user'
        # Return user ID and email as response
        response = {
            'uid': user['localId'],
            'email': user['email'],
            'token': user['idToken'],
            'claim': claim
        }

        return jsonify(response), 200

    except Exception as e:
        error_data = json.loads(e.args[1])

        # Retrieve the "message" value
        message_value = error_data["error"]["message"]

        if message_value == 'INVALID_PASSWORD':
            return jsonify({'error': 'Invalid password.'}), 401
        elif message_value == 'EMAIL_NOT_FOUND':
            return jsonify({'error': 'Email not found.'}), 401
        elif message_value == 'USER_DISABLED':
            return jsonify({'error': 'User disabled.'}), 401
        else:
            return jsonify({'error': message_value}), 401


@app.route('/check/claim', methods=['POST'])
def check_claim():
    # Get uid from request
    token = request.get_json().get('token')

    try:
        # Check if user is admin
        claims = auth.verify_id_token(token)
        if claims['admin']:
            claim = 'admin'
        else:
            claim = 'user'
        return jsonify({'claim': claim}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 401


@app.route('/logout', methods=['POST'])
def logout_user_with_email():
    # Get id token from request
    userdata = request.get_json()
    id_token = userdata.get('token')
    try:
        user_ref = db.collection('blacklistedtokens').document(id_token)
        user_ref.set({'id_token': id_token})
        return jsonify({"status": True, "response": "User logged out successfully."}), 200

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500


@app.route('/checkanswer', methods=['POST'])
def check_answer():
    request_data = request.get_json()
    uid = request_data.get('uid')
    question = request_data.get('question')
    answer = request_data.get('answer')

    try:
        # Query user document in Firestore based on email
        users_ref = db.collection('users')
        query = users_ref.where('uid', '==', uid).get()

        user_details = {}
        for user in query:
            user_details['user_id'] = user.id

        # CALL LAMBDA FUNCTION AND GIVE USER_DETAILS['USER_ID'], QUESTION AND ANSWER AS PARAMETERS
        # IF ANSWER IS CORRECT, RETURN TRUE
        lambda_url = "https://prjap4iaq7.execute-api.us-east-1.amazonaws.com/prod/checkanswer"
        payload = {'uid': user_details['user_id'], 'question': question, 'answer': answer}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(lambda_url, data=json.dumps(payload), headers=headers)
        print("Response:", response.text)

        return response.json(), 200

    except Exception as e:
        print('Error:', str(e))
        return jsonify({'status': False, 'response': str(e)}), 400


@app.route('/get/question', methods=['POST'])
def get_question():
    # Get email from request
    uid = request.get_json().get('uid')
    try:
        # Query user document in Firestore based on email
        users_ref = db.collection('users')
        query = users_ref.where('uid', '==', uid).get()

        user_details = {}
        # Get user ID from query result
        for user in query:
            user_details['user_id'] = user.id

        # CALL LAMBDA FUNCTION AND GIVE USER_DETAILS['USER_ID'] AS PARAMETER
        # IF ANSWER IS CORRECT, RETURN TRUE
        lambda_url = 'https://prjap4iaq7.execute-api.us-east-1.amazonaws.com/prod/get/question'
        payload = {'user_details': {'user_id': user_details['user_id']}}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(lambda_url, data=json.dumps(payload), headers=headers)
        print("Response:", response.text)

        return response.json(), 200

    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 400


# API route for resetting password
@app.route('/resetpassword', methods=['POST'])
def reset_password():
    # Get email from request
    uid = request.json.get('uid')
    email = request.json.get('email')

    # Check if email exists in database
    users_ref = db.collection('users')
    query = users_ref.where('uid', '==', uid).get()
    if len(query) == 0:
        return jsonify({'status': False, 'response': 'Email not found.'}), 404

    # Send password reset link to email
    try:
        # Generate password reset link
        pb.auth().send_password_reset_email(email)

        return jsonify({'status': True, 'response': 'Password reset link sent successful.'}), 200

    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 400


@app.route('/verifytoken', methods=['POST'])
def verify_token():
    # Get token from request
    token = request.json.get('token')

    # Verify token
    try:
        # Check if the token exists in the blacklistedtokens collection
        blacklisted_token_ref = db.collection('blacklistedtokens').document(token).get()
        if blacklisted_token_ref.exists:
            return jsonify({"status": False, "error": "Invalid token."}), 401

        token_status = auth.verify_id_token(token)

        if token_status['uid']:
            return jsonify({'status': True, 'response': 'Token is valid.', 'uid': token_status['uid']}), 200

    except Exception:
        return jsonify({'status': False, 'response': 'Token is invalid.'}), 401


if __name__ == '__main__':
    app.run(port=5100, debug=True)
