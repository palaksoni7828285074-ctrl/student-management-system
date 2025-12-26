from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    student_class = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'student_class': self.student_class,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    search = request.args.get('search', '')
    class_filter = request.args.get('class_filter', '')
    sort_by = request.args.get('sort_by', 'name')
    
    query = Student.query
    
    if search:
        query = query.filter(
            (Student.name.contains(search)) | 
            (Student.email.contains(search)) |
            (Student.phone.contains(search))
        )
    
    if class_filter:
        query = query.filter(Student.student_class == class_filter)
    
    if sort_by == 'name':
        query = query.order_by(Student.name)
    elif sort_by == 'age':
        query = query.order_by(Student.age)
    elif sort_by == 'class':
        query = query.order_by(Student.student_class)
    
    students = query.all()
    classes = db.session.query(Student.student_class).distinct().all()
    classes = [c[0] for c in classes]
    
    return render_template('index.html', students=students, classes=classes)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        student_class = request.form.get('student_class')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Validation
        if not all([name, age, student_class, email, phone]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_student'))
        
        # Check if email already exists
        if Student.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_student'))
        
        new_student = Student(
            name=name,
            age=int(age),
            student_class=student_class,
            email=email,
            phone=phone
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_student.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.age = int(request.form.get('age'))
        student.student_class = request.form.get('student_class')
        student.email = request.form.get('email')
        student.phone = request.form.get('phone')
        
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_student.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/api/students')
def api_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

@app.route('/api/student/<int:id>')
def api_student(id):
    student = Student.query.get_or_404(id)
    return jsonify(student.to_dict())

if __name__ == '__main__':
    app.run(debug=True)