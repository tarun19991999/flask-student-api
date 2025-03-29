from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to reduce overhead
db = SQLAlchemy(app)

# Student model
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)  # You could change this to DateTime for better handling of dates
    amount_due = db.Column(db.Float, nullable=False)

# Initialize the database and create tables
def init_db():
    with app.app_context():
        db.create_all()

# Homepage route
@app.route('/')
def index():
    return " Flask API is running! You can use Postman or visit /form to test."

# Route for HTML form
@app.route('/form')
def form():
    return render_template('form.html')  # Ensure form.html exists in the templates folder

# Create a student (POST)
@app.route('/student', methods=['POST'])
def create_student():
    data = request.get_json() if request.is_json else request.form

    # Input validation
    required_fields = ['student_id', 'first_name', 'last_name', 'dob', 'amount_due']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing field: {field}'}), 400

    try:
        student = Student(
            student_id=int(data['student_id']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            dob=data['dob'],
            amount_due=float(data['amount_due'])
        )
        db.session.add(student)
        db.session.commit()
        return jsonify({'message': 'Student added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Get a student by ID (GET)
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({
        'student_id': student.student_id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'dob': student.dob,
        'amount_due': student.amount_due
    })

# Get all students (GET)
@app.route('/students', methods=['GET'])
def get_all_students():
    students = Student.query.all()
    return jsonify([
        {
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'dob': student.dob,
            'amount_due': student.amount_due
        } for student in students
    ])

# Update a student by ID (PUT)
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()

    # Update the fields if provided in the request
    for field, value in data.items():
        if hasattr(student, field):
            setattr(student, field, value)

    try:
        db.session.commit()
        return jsonify({'message': 'Student updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Delete a student by ID (DELETE)
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    try:
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Run the app
if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    print(" Database ready.")
    print(" Flask app running at http://127.0.0.1:5000/")
    app.run(debug=True)

