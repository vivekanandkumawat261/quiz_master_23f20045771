# 🧠 Quiz Management System (Flask)

A full-stack web application built using **Flask** that allows administrators to create and manage subjects, chapters, quizzes, and questions, while users can register, attempt quizzes, and view their scores and performance analytics.

---

## 🚀 Project Overview

The **Quiz Management System** is designed to support online learning and assessment.  
It provides **role-based access** for **Admins** and **Users**, enabling structured quiz creation and performance tracking with visual analytics.

This project demonstrates:

- Backend development using Flask  
- Database modeling using SQLAlchemy  
- Authentication & authorization with Flask-Login  
- Data visualization using Matplotlib  
- MVC architecture with clean database relationships  

---

## ✨ Features

### 👤 User Features
- User registration & login
- Browse subjects, chapters, and quizzes
- Attempt quizzes with MCQ questions
- Automatic evaluation of answers
- View quiz scores and attempt history
- Search quizzes by name
- Performance analytics with charts

### 🛠 Admin Features
- Admin login
- Create, edit, and delete:
  - Subjects
  - Chapters
  - Quizzes
  - Questions
- Manage users (block / unblock)
- View subject-wise performance summaries
- Visual analytics using bar and circular charts

---

## 🧱 Tech Stack

- **Backend:** Flask 3.1.0  
- **Database:** SQLite  
- **ORM:** Flask-SQLAlchemy  
- **Authentication:** Flask-Login  
- **Frontend:** HTML, Jinja2, Bootstrap  
- **Visualization:** Matplotlib  

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/quiz-management-system.git
cd quiz-management-system



2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

requirements.txt
Flask==3.1.0
Werkzeug==3.1.3
flask-sqlalchemy==3.1.1
flask-login==0.6.3
matplotlib==3.10.1

4️⃣ Run the Application
python app.py


The application will run at:

http://localhost:10000

```
---

 
## 🔐 Default Admin Credentials

Created automatically on first run

- Username: admin

- Password: admin123

---

##  🗄 Database Schema Overview

### Main Entities

- User

- Subject

- Chapter

- Quiz

- Question

- Answer

- Scores

### Relationships

- One Subject → Many Chapters

- One Chapter → Many Quizzes

- One Quiz → Many Questions

- One User → Many Scores

## 🔌 API / Route Documentation (Core Routes)

### 🔐 Authentication Routes
 

 
| Route          | Method     | Description       |
| -------------- | ---------- | ----------------- |
| `/register`    | GET / POST | User registration |
| `/user_login`  | GET / POST | User login        |
| `/admin_login` | GET / POST | Admin login       |
| `/logout`      | GET        | Logout user       |


### 🛠 Admin Routes
| Route	         | Method     |	Description       |
| -------------- | -----------|	----------------  |
| `/admin_dashboard/<name>` | GET|	Admin dashboard  |
| `/new_subject/<name>` | POST|	Create subject  |
| `/new_chapter/<subject_id>/<name>` | POST|	Create chapter  |
| `/new_quiz/<chapter_id>` | POST|	Create quiz  |
| `/new_question/<subject_id>/<chapter_id>/<quiz_id>` | POST|	Add question  |
| `/block_user/<user_id>/<admin_name>` | POST|	Block user  |
| `/unblock_user/<user_id>/<admin_name>` | POST|	Unblock user  |		
 
	 
  
 
 	
 
### 👤 User Routes
| Route	         | Method     |	Description       |
| -------------- | -----------|	----------------  |
| `/user_dashboard/<name>` | GET|	User dashboard  |
| `/start_quiz/<quiz_id>` | GET|	Start quiz  | 
| `/post_start_quiz/<quiz_id>` | POST |	Submit quiz  | 	
| `/scores_dashboard/<username>` | GET	 |	View quiz scores  | 		
	

## 📊 Analytics & Visualization

- Subject-wise quiz attempts

- Subject-wise top scores

- User performance summary

- Charts generated using Matplotlib and rendered as images

## 📁 Project Structure
```bash
├── app.py
├── models.py
├── templates/
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── quiz_questions.html
│   └── ...
├── static/
├── requirements.txt
├── vivek.sqlite
└── README.md
```
 

## 🎯 Learning Outcomes

- Flask MVC architecture

- SQLAlchemy relationships and cascading deletes

- Authentication and session management using Flask-Login

- Role-based access control

- Server-side chart generation

- Clean CRUD-based application design

## 📌 Future Enhancements

- Timer-based quizzes

- Question randomization

- REST API implementation

- Deployment using Docker / Render / Railway

- JWT-based authentication

































 