from flask import Blueprint, jsonify, request
from models import Event, EventType, UserAccount, Schedule, SessionLocal
from auth.auth import token_required, role_required
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
import logging
from uuid import uuid4

events_bp = Blueprint('events', __name__)

def get_session():
    return SessionLocal()

# Add an event (e.g., entrance or exit)
@events_bp.route('/events', methods=['POST'])
@token_required
@role_required("ADMIN")
def add_event(current_user):
    session = get_session()
    data = request.get_json()

    try:
        student = session.query(UserAccount).filter_by(id=data['student_id']).first()

        if not student or student.organization_id != current_user.organization_id:
            return jsonify({"message": "Student not found or not in this organization"}), 404

        event_type = data.get('event_type', '').upper()
        if event_type not in [et.name for et in EventType]:
            return jsonify({"message": "Invalid event type"}), 400

        new_event = Event(
            id=str(uuid4()),
            organization_id=current_user.organization_id,
            student_id=student.id,
            event_type=EventType[event_type],
            timestamp=data.get('timestamp', datetime.utcnow()),
            camera_id=data.get('camera_id'),
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )

        session.add(new_event)
        session.commit()
        return jsonify({"message": "Event added", "event_id": new_event.id}), 201

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error adding event: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

# Get all events
@events_bp.route('/events/all', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_all_events(current_user):
    session = get_session()
    try:
        events = session.query(
            Event.id.label("event_id"),
            Event.timestamp,
            Event.event_type,
            Event.camera_id,
            UserAccount.user_name.label("student_name")
        ).join(UserAccount, Event.student_id == UserAccount.id).filter(
            Event.organization_id == current_user.organization_id
        ).all()

        response = [{
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "camera_id": event.camera_id,
            "student_name": event.student_name
        } for event in events]

        return jsonify(response), 200
    finally:
        session.close()

# Get irrelevant logs (e.g., events outside of scheduled times)
@events_bp.route('/events/irrelevant', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_irrelevant_logs(current_user):
    session = get_session()
    try:
        schedule = session.query(Schedule).filter_by(organization_id=current_user.organization_id).first()
        if not schedule:
            return jsonify({"message": "No schedule found for the organization"}), 200

        events = session.query(
            Event.id.label("event_id"),
            Event.timestamp,
            Event.event_type,
            Event.camera_id,
            UserAccount.user_name.label("student_name")
        ).join(UserAccount, Event.student_id == UserAccount.id).filter(
            Event.organization_id == current_user.organization_id,
            Event.event_type == EventType.STUDENT_ENTRANCE
        ).all()

        # Filter events occurring after the schedule's end time
        irrelevant_events = [
            e for e in events if e.timestamp.time() > schedule.end_time.time()
        ]

        response = [{
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "camera_id": event.camera_id,
            "student_name": event.student_name
        } for event in irrelevant_events]

        return jsonify(response), 200
    finally:
        session.close()

# Get danger logs
@events_bp.route('/events/danger', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_danger_logs(current_user):
    session = get_session()
    try:
        events = session.query(
            Event.id.label("event_id"),
            Event.timestamp,
            Event.event_type,
            Event.camera_id,
            UserAccount.user_name.label("student_name")
        ).join(UserAccount, Event.student_id == UserAccount.id).filter(
            Event.organization_id == current_user.organization_id,
            Event.event_type.in_([EventType.FIGHTING, EventType.SMOKING, EventType.WEAPON])
        ).all()

        response = [{
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "camera_id": event.camera_id,
            "student_name": event.student_name
        } for event in events]

        return jsonify(response), 200
    finally:
        session.close()

# Get entrance logs
@events_bp.route('/events/entrance', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_entrance_logs(current_user):
    session = get_session()
    try:
        events = session.query(
            Event.id.label("event_id"),
            Event.timestamp,
            Event.event_type,
            Event.camera_id,
            UserAccount.user_name.label("student_name")
        ).join(UserAccount, Event.student_id == UserAccount.id).filter(
            Event.organization_id == current_user.organization_id,
            Event.event_type == EventType.STUDENT_ENTRANCE
        ).all()

        response = [{
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "camera_id": event.camera_id,
            "student_name": event.student_name
        } for event in events]

        return jsonify(response), 200
    finally:
        session.close()

@events_bp.route('/events/exit', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_exit_logs(current_user):
    session = get_session()
    try:
        events = session.query(
            Event.id.label("event_id"),
            Event.timestamp,
            Event.event_type,
            Event.camera_id,
            UserAccount.user_name.label("student_name")
        ).join(UserAccount, Event.student_id == UserAccount.id).filter(
            Event.organization_id == current_user.organization_id,
            Event.event_type == EventType.STUDENT_EXIT
        ).all()

        response = [{
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "camera_id": event.camera_id,
            "student_name": event.student_name
        } for event in events]

        return jsonify(response), 200
    finally:
        session.close()

#Lying man
@events_bp.route('/events/lying', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_lying_man(current_user):
    session = get_session()
    try:
        events = session.query(
            Event.id.label("event_id"),
            Event.timestamp,
            Event.event_type,
            Event.camera_id,
            UserAccount.user_name.label("student_name")
        ).join(UserAccount, Event.student_id == UserAccount.id).filter(
            Event.organization_id == current_user.organization_id,
            Event.event_type == EventType.LYING_MAN
        ).all()

        response = [{
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "camera_id": event.camera_id,
            "student_name": event.student_name
        } for event in events]

        return jsonify(response), 200
    finally:
        session.close()

# Count all events
@events_bp.route('/events/count', methods=['GET'])
@token_required
@role_required("ADMIN", "STAFF")
def events_count(current_user):
    session = get_session()
    try:
        count = session.query(Event).filter_by(
            organization_id=current_user.organization_id
        ).count()
        return jsonify({"event_count": count}), 200
    finally:
        session.close()

# Get weekly events grouped by day
@events_bp.route('/events/weekly', methods=['GET'])
@token_required
@role_required("ADMIN")
def get_weekly_events(current_user):
    session = get_session()
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=6)

        events = session.query(Event).filter(
            Event.organization_id == current_user.organization_id,
            Event.timestamp >= start_date,
            Event.timestamp <= end_date
        ).all()

        events_per_day = {day: 0 for day in range(7)}
        for event in events:
            weekday = event.timestamp.weekday()
            events_per_day[weekday] += 1

        ordered_events = [events_per_day[day] for day in range(7)]
        return jsonify(ordered_events), 200
    finally:
        session.close()
