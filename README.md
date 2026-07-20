# Task Management API

A clean and functional Task Management REST API** built with FastAPI + SQLAlchemy for the Software Engineering Internship Take-Home Exercise.

## Features Implemented
- ✅ Full CRUD operations (Create, Read, Update, Delete tasks)
- ✅ Task fields: `id`, `title`, `description`, `status`, `priority`, `created_at`
- ✅ Filtering tasks by status and priority
- ✅ Input validation using Pydantic
- ✅ SQLite database 
- ✅ Automated tests with pytest
- ✅ Simple Shiny web dashboard

## AI Tools Used
- **Tools**: Grok (xAI) and  Gemini
- **Tasks helped with**: Project structure, test cases, validation logic, README writing, and debugging
- **Example Prompts**:
  - "Create FastAPI CRUD endpoints with SQLAlchemy for Task model including filtering"
  - "Write pytest for task create, filter by status, and update operations"
- **My Contribution**: Reviewed all AI-generated code, fixed bugs, improved error handling, organized folder structure, and ensured everything runs smoothly.

## How to Run Locally

# Prerequisites
- Python 3.8 or higher


# Steps
1. Clone the repository
   Bash
   git clone <your-repo-url>
   cd TASKMANAGER

2. Create Virtual Environment
Bash
python -m venv venv
venv\Scripts\activate     # On Windows

3. Install Dependencies
Bash
pip install -r requirements.txt

4. Run the API
Bash
cd app
uvicorn main:app --reload
API will start at: http://127.0.0.1:8000
Interactive Docs: http://127.0.0.1:8000/docs

5. Run Tests
Bash
cd ..
pytest tests/ -v



# Project Structure
Bash
TASKMANAGER/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── curd.py
│   └── routers/
├── tests/
│   └── test_main.py
├── README.md
├── requirements.txt
├── .gitignore
├── dashboard.py         
└── tasks_v2.db




# API Endpoints:
Method,Endpoint,Description
POST,/tasks/,Create new task
GET,/tasks/,Get all tasks (supports filters)
GET,/tasks/{id},Get single task
PUT,/tasks/{id},Update task
DELETE,/tasks/{id},Delete task





