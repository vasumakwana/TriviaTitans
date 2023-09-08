import firebase_admin
from firebase_admin import credentials, firestore
from flask import jsonify

cred = credentials.Certificate('sdpproject-b53f8-firebase-adminsdk-rmwnq-781363c1c6.json')
firebase = firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()


def get_user_details_by_uid(request):

    

    # get email from request
    uid = request.get_json().get('uid')
    try:
        # Query user document in Firestore based on email
        users_ref = db.collection('users')
        query = users_ref.where('uid', '==', uid).get()

        user_details = {}
        for user in query:
            user_details['user_id'] = user.id
            user_details['username'] = user.get('username')
            user_details['email'] = user.get('email')
            user_details['gender'] = user.get('gender')
            user_details['dob'] = user.get('dob')
            user_details['city'] = user.get('city')
            user_details['country'] = user.get('country')
            user_details['profile_pic'] = user.get('profile_pic')

        if not user_details:
            return jsonify({"status": False, "response": 'User not found.'}), 404

        return jsonify(user_details), 200

    except Exception as e:
        print('Error:', str(e))
