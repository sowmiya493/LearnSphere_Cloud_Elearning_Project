# LearnSphere — AI-Powered Cloud E-Learning Prototype

A beginner-friendly Flask web application inspired by the paper **“E-Learning-Based Cloud Computing Environment: A Systematic Review, Challenges, and Opportunities”** (IEEE Access, 2023/2024).

## Features
- Responsive dashboard with course progress and quiz summaries
- Course catalogue and lesson pages
- Mark lessons complete; progress is saved in SQLite
- Multiple-choice quizzes with score feedback
- Topic-based study assistant (demo responses; not a live LLM)
- Editable demo learner profile
- Health endpoint at `/health`
- Ready for a later cloud deployment

## 1. Install prerequisites
Install Python 3.11 or 3.12 and Visual Studio Code. In VS Code, install the official Python extension.

## 2. Open the project
Extract the ZIP, then open the `learnsphere_cloud_elearning` folder in VS Code.

## 3. Create a virtual environment (Windows PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Run the app
```powershell
python app.py
```
Open **http://127.0.0.1:5000** in your browser. Keep the terminal open while using the site. Stop the server with `Ctrl+C`.

## 5. Try the features
1. Open Courses and select a course.
2. Open lessons and click **Mark lesson complete**.
3. Take a course quiz and check the score.
4. Open Study Assistant and ask about SaaS, PaaS, IaaS, architecture or security.
5. Open Profile to change the demo learner name.
6. Visit `http://127.0.0.1:5000/health` to check the app status.

Data is stored locally in a SQLite database. This is a learning prototype, not a production system: it does not yet implement secure login, teacher/admin roles, video hosting, a real AI API, or cloud object storage.

## 6. Suggested cloud deployment path
1. Push the project to a private/public GitHub repository (do not commit secrets or a production database).
2. For a beginner-friendly deployment, use a managed Python web service that supports Flask and a persistent database.
3. For AWS, a practical learning route is: Elastic Beanstalk or App Runner for the web service, RDS for a managed relational database, and S3 for course files. Configure environment variables and HTTPS.
4. Do not use SQLite on ephemeral production storage; move to a managed database. Set a strong `SECRET_KEY`, disable debug mode, configure backups and access controls, and test authorization.
5. Add a live AI provider only after choosing an API, storing its key in environment variables, and adding input/privacy safeguards.

Cloud resources may incur charges. Review the provider's pricing and budget alerts before deploying.

## Research alignment
The paper highlights layered architecture, SaaS/PaaS/IaaS, learning management, analytics/recommenders, public/private/hybrid deployment, performance, security, bandwidth and vendor lock-in. This prototype demonstrates a small layered LMS-style application locally. The AI assistant is rule-based and the cloud deployment is a next step, not a claim that cloud services are already connected.
# LearnSphere_Cloud_Elearning_Project
