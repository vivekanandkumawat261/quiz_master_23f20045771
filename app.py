from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Subject, Chapter, Quiz, Question, Scores, Answer
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')  # Required for server-side plotting
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.patches import Circle



app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vivek.sqlite'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)  # Attach to the Flask app
login_manager.login_view = 'user_login'  # Redirect unauthenticated users to login page

# User loader function (required for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user from database

@app.route("/")
def home():
    return redirect(url_for('first_page'))

@app.route('/first_page')
def first_page():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        full_name = request.form['full_name']
        qualification = request.form['qualification']

        new_user = User(username=username, email=email, password=password, full_name=full_name, qualification=qualification)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully! Please log in.')
        return redirect(url_for('user_login'))

    return render_template("register.html")

@app.route("/user_login", methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.role == 1:
            if user.blocked:
                flash("Your account is blocked. Please contact the administrator.", "danger")
                return redirect(url_for('user_login'))
            
            login_user(user)  # Flask-Login: Log in the user
            flash('Login successful!')
            return redirect(url_for('user_dashboard', name=username))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('user_login'))

    return render_template("user_login.html", role='User')

@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.role == 0:
            login_user(user)  # Flask-Login: Log in admin
            flash('Login successful!')
            return redirect(url_for('admin_dashboard', name=username))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')

# Logout Route (New)
@app.route("/logout")
@login_required
def logout():
    logout_user()  # Flask-Login: Log out user
    flash("You have been logged out.")
    return redirect(url_for('user_login'))  # Redirect to login page

# @app.route("/admin_dashboard/<string:username>")
# def admin_dashboard(username):
    
#     return render_template("admin_dashboard.html",username=username)


@app.route("/user_dashboard/<string:name>")
def user_dashboard(name):
    # chapters = Subject.query.get_or_404(subject_id)
    subjects=Subject.query.all()
    chapters=Chapter.query.all()
    quizzes=Quiz.query.all()
    questions=Question.query.all()
    return render_template("user_dashboard.html",subjects=subjects,chapters=chapters,quizzes=quizzes,questions=questions,name=name)



@app.route("/admin_dashboard/<string:name>")
def admin_dashboard(name):
    subjects=Subject.query.all()
    chapters=Chapter.query.all()
    users = User.query.all()
    # chapters = Subject.query.get_or_404(subject_id)
    return render_template("admin_dashboard.html",users=users,subjects=subjects,chapters=chapters,name=name)
 

@app.route("/new_subject/<string:name>",methods=["GET","POST"])
def new_subject(name):
    if request.method=="POST":
        name = request.form["name"]
        description = request.form["description"]
        
        
        new_subjs = Subject(name=name,description=description)
        
        db.session.add(new_subjs)
        db.session.commit()
        return redirect(url_for('admin_dashboard',name=name))
    return render_template("new_subject.html",name=name)

@app.route("/new_chapter/<int:subject_id>/<string:name>",methods=["GET","POST"])
def new_chapter(subject_id,name): 
    if request.method=="POST":
       
        name = request.form["chapter_name"]
        no_of_question = request.form["no_of_question"]

        description = request.form["description"]
        new_chapter = Chapter(name=name,no_of_question=no_of_question,description=description,subject_id=subject_id)
       
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin_dashboard',name=name))
    return render_template("new_chapter.html",subject_id=subject_id,name=name)

@app.route("/edit_subject/<int:id>/<string:name>" , methods=["GET","POST"])
def edit_subject(id,name):
    s=get_subject(id)
    if request.method=="POST":
        # sname = request.form["name"]
        # description=request.form["description"]

        s.name=request.form["name"]
        s.description=request.form["description"]
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("edit_subject.html",subject=s,name=name)

@app.route("/delete_subject/<int:id>/<string:name>" , methods=["GET","POST"])
def delete_subject(id,name):
    s=get_subject(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))

@app.route("/edit_chapter/<int:id>/<string:name>" , methods=["GET","POST"])
def edit_chapter(id,name):
    c=get_chapter(id)
    if request.method=="POST":
        # sname = request.form["name"]
        # description=request.form["description"]

        c.name=request.form["chapter_name"]
        c.no_of_question=request.form["no_of_question"]
        c.description=request.form["description"]
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("edit_chapter.html",chapter=c,name=name)

@app.route("/delete_chapter/<int:id>/<string:name>" , methods=["GET","POST"])
def delete_chapter(id,name):
    c=get_chapter(id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))
 
@app.route("/edit_question/<int:id>", methods=["GET","POST"])
def edit_question(id):
    q=get_question(id)
    if request.method=="POST":
        q.question_title=request.form["question_title"]
        q.question_statement=request.form["question_statement"]
        q.option1=request.form["question_1"]
        q.option2=request.form["question_2"]
        q.option3=request.form["question_3"]
        q.option4=request.form["question_4"]
        q.correct_option=request.form["correct_question"]
        db.session.commit()
        return redirect(url_for("quiz_manager"))
    return render_template("edit_question.html",question=q)

@app.route("/delete_question/<int:id>")
def delete_question(id):
    q=get_question(id)
    db.session.delete(q)
    db.session.commit()
    return redirect(url_for("quiz_manager"))

@app.route("/edit_quiz/<int:id>",methods=["GET","POST"])
def edit_quiz(id):
    quiz=get_quiz(id)
    if request.method=="POST":
       quiz.quiz_name=request.form["quiz_name"]
       quiz.no_of_question = int(request.form["no_of_question"]) 
       db.session.commit()
       return redirect(url_for("quiz_manager"))
      # ✅ Convert date from string to `datetime.date`
    #    quiz.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()

    #    if ":" in request.form["duration"]:
    #         hours, minutes = map(int, request.form["duration"].split(":"))
    #         quiz.duration = timedelta(hours=hours, minutes=minutes)
    #    else:
    #         flash("Invalid duration format. Please enter in HH:MM format.", "danger")
    #         return redirect(url_for("edit_quiz", id=id))
    #    quiz.duration = timedelta(hours=hours, minutes=minutes)  # Store as timedelta
    #    db.session.commit()
    #    return redirect(url_for("quiz_manager"))
    
    # if isinstance(quiz.duration, str):  
    #     hours, minutes = map(int, quiz.duration.split(":"))
    #     quiz.duration = timedelta(hours=hours, minutes=minutes)
    return render_template("edit_quiz.html",quiz=quiz)

@app.route("/delete_quiz/<int:id>")
def delete_quiz(id):
    quiz=get_quiz(id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for("quiz_manager"))

# @app.route("/new_question/<int: subject_id>/<int:chapter_id>/<int:quiz_id>",methods=["GET","POST"])
@app.route("/new_question/<int:subject_id>/<int:chapter_id>/<int:quiz_id>", methods=["GET", "POST"])
def new_question(subject_id,chapter_id,quiz_id):
    if request.method=="POST":
        question_title=request.form["question_title"]
        question_statement=request.form["question_statement"]
        question_1=request.form["question_1"]
        question_2=request.form["question_2"]
        question_3=request.form["question_3"]
        question_4=request.form["question_4"]
        correct_question=request.form["correct_question"]
        new_question=Question(subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id,question_title=question_title,question_statement=question_statement,option1=question_1,option2=question_2,option3=question_3,option4=question_4,correct_option=correct_question)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("quiz_manager"))
    return render_template("new_question.html",subject_id=subject_id,chapter_id=chapter_id,quiz_id=quiz_id)

 

@app.route("/new_quiz/<int:chapter_id>" , methods=["GET","POST"])
def new_quiz(chapter_id):
    if request.method=="POST":
       quiz_name=request.form["quiz_name"]
       no_of_question = int(request.form["no_of_question"])
    #    date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        
    #    if ":" in request.form["duration"]:
    #         duration_parts = request.form["duration"].split(":")
    #         duration = timedelta(hours=int(duration_parts[0]), minutes=int(duration_parts[1]))
    #    else:
    #         flash("Invalid duration format. Please enter in HH:MM format.", "danger")
    #         return redirect(url_for("new_quiz", chapter_id=chapter_id))
    #    hours, minutes = map(int, duration.split(":"))
    #    duration_timedelta = timedelta(hours=hours, minutes=minutes)
    #    duration_seconds = duration_timedelta.total_seconds()
 

       remarks=request.form["remarks"]
       new_q=Quiz(quiz_name=quiz_name,chapter_id=chapter_id,no_of_question=no_of_question,remarks=remarks)
       db.session.add(new_q)
       db.session.commit()
       return redirect(url_for("quiz_manager"))

    return render_template("new_quiz.html",chapter_id=chapter_id, quiz=None)

@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    # Assuming duration is stored in minutes, multiply by 60 to convert to seconds
    # duration_in_seconds = quiz.duration * 60
    
    return render_template('quiz_questions.html', quiz=quiz, questions=quiz.questions)

@app.route("/quiz_manager",methods=["GET"])
def quiz_manager():
    subjects=Subject.query.all()
    chapters=Chapter.query.all()
    quizzes = Quiz.query.all()
    questions=Question.query.all()
    return render_template("quiz_manager.html",subjects=subjects,chapters=chapters,quizzes=quizzes,questions=questions)

@app.route("/view_quiz/<string:subject_name>/<string:chapter_name>/<int:id>")
def view_quiz(subject_name,chapter_name,id):
    quiz_id=get_quiz_id(id)

    subject_name=get_subject_name(subject_name)
    chapter_name=get_chapter_name(chapter_name)
   
    return render_template("view_quiz.html",quiz_id=quiz_id,subject_name=subject_name,chapter_name=chapter_name)

@app.route('/start_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def start_quiz(quiz_id): 
    quiz=get_quiz_id(quiz_id)
    
    return render_template("quiz_questions.html",quiz=quiz)

@app.route('/post_start_quiz/<int:quiz_id>', methods=['POST'])
@login_required  # Ensure user is logged in
def post_start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user = current_user  # Assuming Flask-Login is used

    if request.method == 'POST':
        answers = request.form
        score = 0
        list=[]
        for question in quiz.questions:
            user_answer = answers.get(f"answers_{question.id}")  # Correct way to fetch answers
        
            list.append(user_answer)
            if user_answer and str(user_answer) == str(question.correct_option):
                score += 1  # Increment score if the answer is correct

            # Save answer to Answer table (if needed)
            new_answer = Answer(question_id=1, user_id=2, answer_text="Some answer", selected_answer=user_answer)  # ✅ Now works
            db.session.add(new_answer)

        # Check if a score entry already exists for this user and quiz
        existing_score = Scores.query.filter_by(quiz_id=quiz.id, user_id=user.id).first()

        if existing_score:
            existing_score.total_scored = score  # Update the existing score
        else:
            new_score = Scores(quiz_id=quiz.id, user_id=user.id, total_scored=score)
            db.session.add(new_score)

        db.session.commit()

        return render_template("submit.html",quiz=quiz,list=list,score=score)
        # given_option = request.form["answers"]  # Get the selected answer
        
        # if not given_option:
        #     flash("Please select an answer!", "danger")
        #     return redirect(url_for('post_start_quiz', quiz_id=quiz_id))

        
        # new_ans = Answer( selected_answer=given_option)  # Fixed model usage
        # db.session.add(new_ans)
        # db.session.commit()
        
        # return render_template("submit.html",selected_answer=given_option,quiz=quiz)
 
@app.route("/again_user_dashboard>")
def again_user_dashboard():
    # chapters = Subject.query.get_or_404(subject_id)
    subjects=Subject.query.all()
    chapters=Chapter.query.all()
    quizzes=Quiz.query.all()
    questions=Question.query.all()
    return render_template("user_dashboard.html",subjects=subjects,chapters=chapters,quizzes=quizzes,questions=questions)

@app.route("/again_admin_dashboard")
def again_admin_dashboard():
    subjects=Subject.query.all()
    chapters=Chapter.query.all()
    users = User.query.all()
    # chapters = Subject.query.get_or_404(subject_id)
    return render_template("admin_dashboard.html",users=users,subjects=subjects,chapters=chapters)
 


@app.route("/quiz_summary/<int:quiz_id>")
def quiz_summary(quiz_id):
    # Retrieve the quiz and results here
    quiz = Quiz.query.get_or_404(quiz_id)
    # You can also calculate and display the score here based on user answers

    return render_template("quiz_summary.html", quiz=quiz)

@app.route("/block_user/<int:user_id>/<string:admin_name>", methods=["POST"])
def block_user(user_id, admin_name):
    user = User.query.get_or_404(user_id)
    user.blocked = True
    db.session.commit()
    flash(f"User '{user.username}' has been blocked.", "success")
    return redirect(url_for('admin_dashboard', name=admin_name))

@app.route("/unblock_user/<int:user_id>/<string:admin_name>", methods=["POST"])
def unblock_user(user_id, admin_name):
    user = User.query.get_or_404(user_id)
    user.blocked = False
    db.session.commit()
    flash(f"User '{user.username}' has been unblocked.", "success")
    return redirect(url_for('admin_dashboard', name=admin_name))


@app.route("/summary_chart/<string:username>")
@login_required
def summary_chart(username):
    # Get subject-wise quiz counts
    subject_quiz_counts = db.session.query(
        Subject.name,
        db.func.count(Quiz.id).label('quiz_count')
    ).join(
        Chapter, Subject.id == Chapter.subject_id
    ).join(
        Quiz, Chapter.id == Quiz.chapter_id
    ).join(
        Scores, Quiz.id == Scores.quiz_id
    ).filter(
        Scores.user_id == current_user.id
    ).group_by(
        Subject.name
    ).all()

    # Convert to format needed for chart
    subjects = [sq[0] for sq in subject_quiz_counts]
    quiz_counts = [sq[1] for sq in subject_quiz_counts]

    # Get month-wise attempted quiz counts
    month_quiz_counts = db.session.query(
        db.func.count(Scores.id).label('attempt_count')
    ).filter(
        Scores.user_id == current_user.id
    ).group_by(
        # If you have the time_stamp_of_attempt field uncommented, use:
        # db.func.strftime('%m', Scores.time_stamp_of_attempt)
        Scores.id  # Temporary grouping, replace with actual month when timestamp is added
    ).all()

    # Convert to format needed for chart
    month_counts = [count[0] for count in month_quiz_counts]

    return render_template(
        "summary_chart.html",
        username=username,
        subjects=subjects,
        quiz_counts=quiz_counts,
        month_counts=month_counts
    )
#summary for admin

@app.route("/admin_summary/<string:username>")
@login_required
def admin_summary(username):
    if current_user.role != 0:  # Check if user is admin
        flash("Access denied. Admin privileges required.")
        return redirect(url_for('user_dashboard', name=username))

    # Get subject-wise top scores
    subject_scores = db.session.query(
        Subject.name,
        db.func.max(Scores.total_scored).label('top_score')
    ).join(
        Chapter, Subject.id == Chapter.subject_id
    ).join(
        Quiz, Chapter.id == Quiz.chapter_id
    ).join(
        Scores, Quiz.id == Scores.quiz_id
    ).group_by(
        Subject.name
    ).all()

    # Get subject-wise attempt counts
    subject_attempts = db.session.query(
        Subject.name,
        db.func.count(Scores.id).label('attempt_count')
    ).join(
        Chapter, Subject.id == Chapter.subject_id
    ).join(
        Quiz, Chapter.id == Quiz.chapter_id
    ).join(
        Scores, Quiz.id == Scores.quiz_id
    ).group_by(
        Subject.name
    ).all()

    # Create bar chart
    plt.figure(figsize=(10, 5))
    subjects = [s[0] for s in subject_scores]
    scores = [s[1] for s in subject_scores]
    colors = ['skyblue', 'red', 'green', 'yellow', 'pink']
    plt.bar(subjects, scores, color=colors)
    plt.title('Subject-wise Top Scores')
    plt.xlabel('Subjects')
    plt.ylabel('Scores')
    
    # Save bar chart to string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    bar_chart = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    # Create circular chart for attempts
    plt.figure(figsize=(8, 8))
    circle1 = plt.Circle((0.5, 0.5), 0.4, color='yellow', fill=False)
    circle2 = plt.Circle((0.5, 0.5), 0.3, color='blue', fill=False)
    circle3 = plt.Circle((0.5, 0.5), 0.2, color='red', fill=False)
    
    fig, ax = plt.subplots()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_artist(circle1)
    ax.add_artist(circle2)
    ax.add_artist(circle3)
    ax.axis('off')
    plt.title('Subject-wise User Attempts')
    
    # Save circular chart to string buffer
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', bbox_inches='tight')
    buf2.seek(0)
    circle_chart = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close()

    return render_template(
        'admin_summary_chart.html',
        username=username,
        bar_chart=bar_chart,
        circle_chart=circle_chart
    )

@app.route("/search/<name>",methods=["GET","POST"])
def search(name):
    if request.method=="POST":
       search_txt=request.form.get("search_txt")
       by_subject=search_by_subject(search_txt)
       b_chapter=search_by_chapter(search_txt)
       print(b_chapter)
       if by_subject:
           return render_template("admin_dashboard.html",name=name,subjects=by_subject)
       elif b_chapter:
           return render_template("admin_dashboard.html",name=name,subjects=b_chapter)

    return redirect(url_for("admin_dashboard",name=name))

@app.route("/scores_dashboard/<string:username>")
@login_required
def scores_dashboard(username):
    # Get the current user's scores
    user_scores = db.session.query(
        Scores.id,
        Quiz.quiz_name,
        Quiz.no_of_question,
        Scores.total_scored
    ).join(
        Quiz, Scores.quiz_id == Quiz.id
    ).filter(
        Scores.user_id == current_user.id
    ).all()
    
    return render_template("scores_dashboard.html", scores=user_scores, username=username)

@app.route("/search_scores", methods=["POST"])
@login_required
def search_scores():
    search_query = request.form.get("search_query", "")
    
    # Search in quiz names and scores
    user_scores = db.session.query(
        Scores.id,
        Quiz.quiz_name,
        Quiz.no_of_question,
        Scores.total_scored
    ).join(
        Quiz, Scores.quiz_id == Quiz.id
    ).filter(
        Scores.user_id == current_user.id,
        Quiz.quiz_name.ilike(f"%{search_query}%")
    ).all()
    
    return render_template("scores_dashboard.html", scores=user_scores, username=current_user.username)

def get_user_quiz_scores(user_id):
    """Get all quiz scores for a specific user"""
    return Scores.query.filter_by(user_id=user_id).all()

def get_quiz_summary(quiz_id, user_id):
    """Get summary of a specific quiz for a user"""
    return Scores.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()

def func():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            email='admin@gmail.com',
            full_name='full_name',
            qualification='qualification',
            role=0
        )
        db.session.add(admin)
        db.session.commit()
        return  'success'
    pass

def search_by_subject(search_txt):
    subjects=Subject.query.filter(Subject.name.ilike(f"%{search_txt}%")).all()
    return subjects

def search_by_chapter(search_txt):
    # chapters=Chapter.query.filter(Chapter.name.ilike(f"%{search_txt}%"))
    chapters=Chapter.query.filter(Chapter.name.ilike(f"%{search_txt}%")).all()
    return chapters

def get_subject(id):
    subject=Subject.query.filter_by(id=id).first()
    return subject

def get_chapter(id):
    chapter=Chapter.query.filter_by(id=id).first()
    return chapter
def get_question(id):
    question=Question.query.filter_by(id=id).first()
    return question

def get_quiz(id):
    quiz=Quiz.query.filter_by(id=id).first()
    return quiz

def get_quiz_id(id):
    quiz_id=Quiz.query.filter_by(id=id).first()
    return quiz_id
    
def get_subject_name(name):
    subject_name=Subject.query.filter_by(name=name).first()
    return subject_name

def get_chapter_name(name):
    chapter_name=Chapter.query.filter_by(name=name).first()
    return chapter_name

def convert_duration_to_seconds(duration):
    # Convert HH:MM to total seconds
    time_obj = datetime.strptime(duration, "%H:%M")
    return time_obj.hour * 3600 + time_obj.minute * 60


# Define the custom filter
@app.template_filter('time_format')
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"
 
#Initialize the database
with app.app_context():
    db.create_all()
    func()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=10000)