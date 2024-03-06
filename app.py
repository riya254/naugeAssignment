from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


# this is configuration of database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:%40root@Rinki:3306/assignment'
db = SQLAlchemy(app)

# here i am creating for database field
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)
    present = db.Column(db.Boolean)
    submitted_by = db.Column(db.String(50))
    
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50))
    department_id = db.Column(db.Integer)
    semester_id = db.Column(db.Integer)
    class_name = db.Column(db.String(50))
    lecture_hours = db.Column(db.Integer)
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20))
    full_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(50))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50))
    department_id = db.Column(db.Integer)
    class_name = db.Column(db.String(50))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime)

# required API for attendance system
    
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            access_token = create_access_token(identity={'username': username, 'user_type': user.user_type})
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/attendance', methods=['POST'])
def add_attendance():
    data = request.get_json()
    new_attendance = Attendance(**data)
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance added successfully'}), 201



@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    course_list = []
    for course in courses:
        course_dict = {
            'id': course.id,
            'course_name': course.course_name,
            'department_id': course.department_id,
            'semester_id': course.semester_id,
            'class_name': course.class_name,
            'lecture_hours': course.lecture_hours,
            'submitted_by': course.submitted_by,
            'updated_at': course.updated_at
        }
        course_list.append(course_dict)
    return jsonify({'courses': course_list})


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        raise InvalidUsage(str(e), status_code=400)



@app.route('/attendance/student/<int:student_id>', methods=['GET'])
def get_student_attendance(student_id):
    try:
        student_attendance = Attendance.query.filter_by(student_id=student_id).all()

        if not student_attendance:
            return jsonify({'message': 'No attendance records found for the student'}), 404

        attendance_list = []
        for attendance in student_attendance:
            attendance_dict = {
                'id': attendance.id,
                'student_id': attendance.student_id,
                'course_id': attendance.course_id,
                'present': attendance.present,
                'submitted_by': attendance.submitted_by
            }
            attendance_list.append(attendance_dict)

        return jsonify({'attendance_records': attendance_list}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500



@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            access_token = create_access_token(identity={'username': username, 'user_type': user.user_type})
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200



@app.route('/students', methods=['POST'])
def create_student():
    try:
        data = request.get_json()
        new_student = Student(**data)
        db.session.add(new_student)
        db.session.commit()
        return jsonify({'message': 'Student created successfully'}), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        students = Student.query.all()
        student_list = [
            {
                'id': student.id,
                'full_name': student.full_name,
                'department_id': student.department_id,
                'class_name': student.class_name,
                'submitted_by': student.submitted_by,
                'updated_at': student.updated_at
            } for student in students
        ]
        return jsonify({'students': student_list}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student_by_id(student_id):
    try:
        student = Student.query.get(student_id)

        if not student:
            return jsonify({'message': 'Student not found'}), 404

        student_data = {
            'id': student.id,
            'full_name': student.full_name,
            'department_id': student.department_id,
            'class_name': student.class_name,
            'submitted_by': student.submitted_by,
            'updated_at': student.updated_at
        }

        return jsonify({'student': student_data}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.get_json()
        student = Student.query.get(student_id)

        if not student:
            return jsonify({'message': 'Student not found'}), 404

        student.full_name = data.get('full_name', student.full_name)
        student.department_id = data.get('department_id', student.department_id)
        student.class_name = data.get('class_name', student.class_name)
        student.submitted_by = data.get('submitted_by', student.submitted_by)
        student.updated_at = data.get('updated_at', student.updated_at)

        db.session.commit()

        return jsonify({'message': 'Student updated successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 400

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        student = Student.query.get(student_id)

        if not student:
            return jsonify({'message': 'Student not found'}), 404

        db.session.delete(student)
        db.session.commit()

        return jsonify({'message': 'Student deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
