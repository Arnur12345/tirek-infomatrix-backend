from flask import Blueprint, jsonify, request
from models import UserAccount, UserRole, SessionLocal, engine, Organization, FaceEncoding, Subscription
from auth.auth import token_required, role_required
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

students_bp = Blueprint('students', __name__)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_session():
    return SessionLocal()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

@students_bp.route('/students', methods=['POST'])
@token_required
@role_required("ADMIN")
def add_student(current_user):
    session = get_session()  # Create a new session
    data = request.get_json()

    # Ensure organization_id exists in the database
    organization_id = data.get("organization_id", "").strip()  # Strip whitespace
    if not organization_id:
        session.close()
        return jsonify({"message": "Organization ID is required"}), 400

    organization = session.query(Organization).filter_by(id=organization_id).first()
    if not organization:
        session.close()
        return jsonify({"message": "Invalid Organization ID"}), 400

    # Ensure student_name is provided
    student_name = data.get("student_name")
    if not student_name:
        session.close()
        return jsonify({"message": "Student name is required"}), 400

    # Prepare the new student record
    new_student = UserAccount(
        id=str(uuid4()),
        user_name=student_name,
        user_role=UserRole.STUDENT,
        organization_id=organization_id,
        user_login=student_name,  # Assuming student_name is used for login
        password_hash="default_password"  # Placeholder for the password hash
    )

    try:
        session.add(new_student)
        session.commit()
        return jsonify({"message": "Student added successfully", "student_id": new_student.id, "student_name" : str(student_name)}), 201
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error adding student: {str(e)}")
        return jsonify({"error": "An error occurred while adding the student"}), 500
    finally:
        session.close()



@students_bp.route('/students', methods=['GET'])
@token_required
@role_required("STAFF","ADMIN","OWNER")
def get_students(current_user):
    session = get_session()

    logging.info(f"Fetching students for organization: {current_user.organization_id}")

    # Получаем всех студентов, принадлежащих организации администратора
    students = session.query(UserAccount).filter_by(
        organization_id=current_user.organization_id,
        user_role=UserRole.STUDENT
    ).all()

    session.close()

    return jsonify([{
        "student_id": student.id,
        "student_name": student.user_name
    } for student in students])

@students_bp.route('/students/count', methods=['GET'])
@token_required
@role_required("STAFF","ADMIN","OWNER")
def students_number(current_user):
    session = get_session()
    try:
        logging.info(f"Counting students for organization: {current_user.organization_id}")

        # Get the number of students for the admin's organization
        student_count = session.query(UserAccount).filter_by(
            organization_id=current_user.organization_id,
            user_role=UserRole.STUDENT
        ).count()

        return jsonify({"student_count": student_count}), 200
    finally:
        session.close()

@students_bp.route('/students/<string:student_id>', methods=['DELETE'])
@token_required
@role_required("ADMIN")
def delete_student(current_user, student_id):
    session = get_session()
    try:
        logging.info(f"Attempting to delete student with ID: {student_id} by user: {current_user.id}")

        # Fetch the student to be deleted
        student = session.query(UserAccount).filter_by(
            id=student_id,
            organization_id=current_user.organization_id,  # Ensure student belongs to the same organization
            user_role=UserRole.STUDENT
        ).first()

        if not student:
            logging.warning(f"Student with ID: {student_id} not found or unauthorized access attempted.")
            return jsonify({"message": "Student not found or access denied"}), 404

        # Delete related records in dependent tables
        session.query(FaceEncoding).filter_by(user_id=student_id).delete()
        session.query(Subscription).filter_by(user_id=student_id).delete()

        # Delete the student record
        session.delete(student)
        session.commit()

        logging.info(f"Successfully deleted student with ID: {student_id}")
        return jsonify({"message": "Student deleted successfully"}), 200

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error deleting student: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the student"}), 500

    finally:
        session.close()

