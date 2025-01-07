from flask import Blueprint, jsonify, request
from models import Organization, SessionLocal
from auth.auth import token_required, role_required
from sqlalchemy.exc import SQLAlchemyError
import logging

schools_bp = Blueprint('schools', __name__)

# Helper function for session management
def get_session():
    return SessionLocal()

# Route to add a new school
from uuid import uuid4

@schools_bp.route('/schools', methods=['POST'])
@token_required
@role_required("ADMIN")
def add_school(current_user):
    session = get_session()
    data = request.get_json()

    try:
        # Check if required field 'org_name' is provided
        if not data or 'org_name' not in data:
            return jsonify({"message": "Invalid input. 'org_name' is required."}), 400

        # Check if a school with the same name already exists
        existing_school = session.query(Organization).filter_by(org_name=data['org_name']).first()
        if existing_school:
            return jsonify({"message": f"School with name '{data['org_name']}' already exists."}), 400

        # Create a new school with a UUID
        new_school = Organization(
            id=str(uuid4()),  # Generate a unique ID
            org_name=data['org_name']
        )
        session.add(new_school)
        session.commit()

        return jsonify({"message": "School added", "school_id": new_school.id}), 201

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error adding school: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        session.close()


# Route to retrieve the list of schools
@schools_bp.route('/schools', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_schools(current_user):
    session = get_session()
    schools = session.query(Organization).all()
    session.close()

    return jsonify([{
        "school_id": school.id,
        "org_name": school.org_name
    } for school in schools])

# Route to update a school's data
@schools_bp.route('/schools/<school_id>', methods=['PUT'])
@token_required
@role_required("ADMIN")
def update_school(current_user, school_id):
    session = get_session()
    data = request.get_json()
    
    # Find the school by ID
    school = session.query(Organization).filter_by(id=school_id).first()
    if not school:
        session.close()
        return jsonify({"message": "School not found"}), 404

    # Update the school's name
    school.org_name = data.get('org_name', school.org_name)
    session.commit()
    session.close()

    return jsonify({"message": "School updated"}), 200


@schools_bp.route('/schools/count', methods=['GET'])
@token_required
@role_required("STAFF", "ADMIN", "OWNER")
def count_schools(current_user):
    
    session = get_session()
    try:
        logging.info(f"Counting schools for organization_id={current_user.organization_id}")

        # Count the number of schools (organizations) for the current user's organization
        school_count = (
            session.query(Organization)
            .count()
        )

        logging.info(f"School count for organization_id={current_user.organization_id}: {school_count}")
        return jsonify({"school_count": school_count}), 200

    except Exception as e:
        logging.error(f"Error counting schools: {str(e)}")
        return jsonify({"error": "An error occurred while counting schools."}), 500

    finally:
        session.close()