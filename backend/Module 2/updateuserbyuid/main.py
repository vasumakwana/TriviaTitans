import firebase_admin
from firebase_admin import credentials, firestore
from flask import jsonify

# Initialize Firebase Admin SDK with the provided service account credentials
cred = credentials.Certificate('sdpproject-b53f8-firebase-adminsdk-rmwnq-781363c1c6.json')
firebase = firebase_admin.initialize_app(cred)

# Initialize Firestore database client
db = firestore.client()

def update_user_details_by_uid(request):
    """
    Endpoint to update user details in Firestore based on the provided user ID (UID).

    Args:
        request (flask.Request): The incoming HTTP request containing user details to update.

    Returns:
        flask.Response: A JSON response indicating the status of the operation.

    Example Usage:
        Request:
            POST /update_user_details
            {
                "uid": "user123",
                "username": "JohnDoe",
                "email": "johndoe@example.com",
                "gender": "male",
                "dob": "1990-01-01",
                "city": "New York",
                "country": "USA",
                "profile_pic": "https://example.com/profile.jpg"
            }

        Response:
            {
                "status": True,
                "response": "User details updated successfully."
            }
    """
    try:
        # Extract user details from the request
        request_data = request.get_json()
        uid = request_data.get('uid')
        username = request_data.get('username')
        email = request_data.get('email')
        gender = request_data.get('gender')
        dob = request_data.get('dob')
        city = request_data.get('city')
        country = request_data.get('country')
        profile_pic = request_data.get('profile_pic')

        # Update user document in Firestore with the provided details
        user_ref = db.collection('users').document(uid)
        user_ref.update({
            'username': username,
            'email': email,
            'gender': gender,
            'dob': dob,
            'city': city,
            'country': country,
            'profile_pic': profile_pic
        })

        # Return success response
        return jsonify({"status": True, "response": 'User details updated successfully.'}), 200

    except Exception as e:
        # Return error response if any exception occurs during the update
        return jsonify({"status": False, 'error': str(e)}), 400
