from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    # dob = db.Column(db.DateTime,nullable=True)  # Date of birth
    role = db.Column(db.Integer, default=1)  # User role
    blocked = db.Column(db.Boolean, default=False)  # Blocked status
    scores = db.relationship('Scores', backref='user', lazy=True)  # Relationship with scores
    
    def is_active(self):
         return not self.blocked  # Users are active unless blocked

    def get_id(self):
         return str(self.id)  # Flask-Login requires a string ID

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    chapters = db.relationship('Chapter', cascade="delete,all", backref='subject', lazy=True)
    questions = db.relationship('Question', backref='subject', lazy=True)
    

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    no_of_question = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    quizzes = db.relationship('Quiz', cascade="delete,all", backref='chapter', lazy=True)
    questions = db.relationship('Question', cascade="delete,all", backref='chapter', lazy=True)
class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(40), nullable=False)  # Removed primary_key=True
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    no_of_question = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    # date = db.Column(db.DateTime, nullable=True)
    # duration = db.Column(db.String(5), nullable=True)  # Format HH:MM
    questions = db.relationship('Question',cascade="delete,all", backref='quiz', lazy=True)  # Updated backref to 'quiz'
    scores = db.relationship('Scores', cascade="delete,all", backref='quiz', lazy=True)  # Renamed from 'quizs'

    
class Question(db.Model):
    __tablename__ = 'questions'  # Ensuring it's named properly as questions
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)  # Fix quiz table name if needed
    question_title = db.Column(db.Text, nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(10), nullable=False)  # Store correct option as '1', '2', '3', '4', etc.
    answers = db.relationship('Answer', backref='question', lazy='dynamic')  # this is where the conflict may happen

 

class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False, default=0)


class Answer(db.Model):
    __tablename__ = 'answers'  # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)  # ✅ Fix reference
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ Fix reference
    answer_text = db.Column(db.Text, nullable=False)
    selected_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=True)

    # selected_answer is not a database column, so it should not be in __init__
    def __init__(self, question_id, user_id, answer_text,selected_answer, is_correct=False):
        self.question_id = question_id
        self.user_id = user_id
        self.answer_text = answer_text
        self.selected_answer=selected_answer
        self.is_correct = is_correct
        