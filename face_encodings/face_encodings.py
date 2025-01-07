from flask import Blueprint, jsonify, request
from models import FaceEncoding, UserAccount, SessionLocal
from auth.auth import token_required, role_required
from sqlalchemy.exc import SQLAlchemyError
import logging
from uuid import uuid4

face_encodings_bp = Blueprint('face_encodings', __name__)

def get_session():
    return SessionLocal()

# Get all users with face encodings for the current organization
@face_encodings_bp.route('/face_encodings', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_users_with_encodings(current_user):
    session = get_session()
    try:
        # Join FaceEncoding with UserAccount to fetch usernames of users with encodings
        users_with_encodings = session.query(UserAccount.user_name).join(FaceEncoding).filter(
            UserAccount.organization_id == current_user.organization_id
        ).all()

        if not users_with_encodings:
            return jsonify({"message": "No users with encodings found for this organization"}), 404

        # Return only usernames
        response_data = [user.user_name for user in users_with_encodings]
        return jsonify(response_data), 200

    except SQLAlchemyError as e:
        logging.error(f"Error fetching users with encodings: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

# Add a new face encoding for a user
@face_encodings_bp.route('/face_encodings', methods=['POST'])
@token_required
@role_required("ADMIN")
def add_encoding(current_user):
    session = get_session()
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID not provided"}), 400

    try:
        # Ensure the user belongs to the current organization
        user = session.query(UserAccount).filter_by(id=user_id).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        if user.organization_id != current_user.organization_id:
            return jsonify({"message": "User does not belong to this organization"}), 403

        # Load the image and generate face encodings
        import face_recognition
        image = face_recognition.load_image_file(file)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return jsonify({"error": "No faces detected in the image"}), 400

        # Take the first face encoding (assume single face)
        face_encoding = face_encodings[0]
        binary_data = face_encoding.tobytes()

        # Save the encoding in the database
        new_encoding = FaceEncoding(
            id=str(uuid4()),
            user_id=user.id,
            face_encoding=binary_data
        )
        session.add(new_encoding)
        session.commit()

        return jsonify({"message": "Face encoding added successfully"}), 201

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error adding face encoding: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()
