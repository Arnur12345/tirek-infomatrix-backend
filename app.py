from flask import Flask
from flask_cors import CORS
from models import Base, engine
from auth.auth import auth_bp
from schools import schools_bp
from events import events_bp
from students import students_bp
from face_encodings import face_encodings_bp

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(schools_bp)
app.register_blueprint(events_bp)
app.register_blueprint(students_bp)
app.register_blueprint(face_encodings_bp)

# Reflect existing tables in the database



if __name__ == '__main__':
    app.run(debug=True)
