
from datetime import datetime
from urllib.parse import urlparse, parse_qs, quote_plus
import re

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from youtube_transcript_api import YouTubeTranscriptApi


# =====================================================
# 1. FLASK CONFIGURATION
# =====================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-secret-key-before-deployment"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learnsphere.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =====================================================
# 2. DATABASE MODELS
# =====================================================

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, unique=True, nullable=False)
    completed = db.Column(db.Boolean, default=True, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_slug = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)


# =====================================================
# 3. COURSE AND LESSON DATA
# =====================================================

COURSES = [
    {
        "slug": "cloud-computing",
        "title": "Cloud Computing",
        "description": "Learn cloud fundamentals, service models, and deployment models.",
        "icon": "☁️",
        "lessons": [
            {
                "id": 1,
                "title": "Introduction to Cloud Computing",
                "content": (
                    "Cloud computing provides computing resources such as "
                    "servers, storage, databases, and software over the internet. "
                    "Users can access resources when required without maintaining "
                    "all the physical infrastructure themselves."
                ),
                "takeaway": "Understand cloud computing and its main benefits.",
                "video_url": "https://youtu.be/RWgW-CgdIk0",
            },
            {
                "id": 2,
                "title": "Cloud Service Models",
                "content": (
                    "IaaS provides computing infrastructure. PaaS provides "
                    "a platform for application development. SaaS provides "
                    "ready-to-use software over the internet."
                ),
                "takeaway": "Differentiate IaaS, PaaS, and SaaS.",
                "video_url": "https://youtu.be/K6OiQ7woPw4",
            },
            {
                "id": 3,
                "title": "Cloud Deployment Models",
                "content": (
                    "Public cloud serves multiple customers. Private cloud "
                    "is dedicated to an organization. Hybrid cloud combines "
                    "public and private cloud environments."
                ),
                "takeaway": "Understand public, private, and hybrid clouds.",
                "video_url": "https://youtu.be/sdsZZyGv7DU",
            },
        ],
    },
    {
        "slug": "web-development",
        "title": "Web Development",
        "description": "Learn HTML, CSS, and JavaScript.",
        "icon": "💻",
        "lessons": [
            {
                "id": 4,
                "title": "Introduction to HTML",
                "content": (
                    "HTML stands for HyperText Markup Language. It defines "
                    "webpage structure using headings, paragraphs, links, "
                    "images, and forms."
                ),
                "takeaway": "Understand the structure of an HTML webpage.",
                "video_url": "https://youtu.be/FYErehuSuuw",
            },
            {
                "id": 5,
                "title": "Introduction to CSS",
                "content": (
                    "CSS stands for Cascading Style Sheets. It controls "
                    "webpage colors, fonts, spacing, layouts, and responsive "
                    "design."
                ),
                "takeaway": "Learn how CSS styles HTML webpages.",
                "video_url": "https://youtu.be/vfs1wBDoqBY",
            },
            {
                "id": 6,
                "title": "Introduction to JavaScript",
                "content": (
                    "JavaScript adds interactivity to webpages. It can respond "
                    "to user actions, validate forms, and update page content."
                ),
                "takeaway": "Understand how JavaScript makes webpages interactive.",
                "video_url": "https://youtu.be/poo0BXryffI",
            },
        ],
    },
    {
        "slug": "data-analytics",
        "title": "Data Analytics",
        "description": "Learn data analysis and visualization.",
        "icon": "📊",
        "lessons": [
            {
                "id": 7,
                "title": "Introduction to Data Analytics",
                "content": (
                    "Data analytics examines information to identify patterns, "
                    "answer questions, and support decision-making."
                ),
                "takeaway": "Understand the purpose of data analytics.",
                "video_url": "https://youtu.be/dzt0AKuoCqo",
            },
            {
                "id": 8,
                "title": "Data Analytics",
                "content": (
                    "Data analytics involves examining, transforming, and "
                    "interpreting data to discover useful information."
                ),
                "takeaway": "Understand the data analytics process.",
                "video_url": "https://youtu.be/gcF31GuwSEs",
            },
            {
                "id": 9,
                "title": "Data Visualization",
                "content": (
                    "Data visualization presents information through charts "
                    "and graphs. Bar charts compare categories, line charts "
                    "show changes over time, and scatter plots show relationships."
                ),
                "takeaway": "Learn how charts communicate data.",
                "video_url": "https://youtu.be/Bo61kls5ZHM",
            },
        ],
    },
    {
        "slug": "iot",
        "title": "Internet of Things (IoT)",
        "description": "Explore connected devices, sensors, and applications.",
        "icon": "📡",
        "lessons": [
            {
                "id": 10,
                "title": "Introduction to IoT",
                "content": (
                    "The Internet of Things connects physical objects that "
                    "collect and exchange data. Examples include smart watches "
                    "and connected home devices."
                ),
                "takeaway": "Define IoT and identify everyday examples.",
                "video_url": "https://youtu.be/Ld-Z7SNgdIM",
            },
            {
                "id": 11,
                "title": "IoT Sensors and Devices",
                "content": (
                    "Sensors measure conditions such as temperature, light, "
                    "motion, and humidity. IoT devices can transmit readings "
                    "to other systems."
                ),
                "takeaway": "Understand the role of sensors in IoT.",
                "video_url": "https://youtu.be/PDPulwzeKMo",
            },
            {
                "id": 12,
                "title": "IoT Applications",
                "content": (
                    "IoT is used in smart homes, healthcare, agriculture, "
                    "transportation, and manufacturing for monitoring and "
                    "automation."
                ),
                "takeaway": "Identify practical IoT applications.",
                "video_url": "https://youtu.be/FFWiKwm9A4I",
            },
        ],
    },
]


# =====================================================
# 4. QUIZ QUESTIONS
# =====================================================

QUIZZES = {
    "cloud-computing": [
        {
            "question": "What does cloud computing provide?",
            "options": [
                "Only physical books",
                "Computing resources over a network",
                "Only offline games",
                "Only keyboards",
            ],
            "answer": 1,
        },
        {
            "question": "Which service model provides ready-to-use software?",
            "options": ["IaaS", "PaaS", "SaaS", "LAN"],
            "answer": 2,
        },
        {
            "question": "Which model combines public and private clouds?",
            "options": [
                "Hybrid cloud",
                "Offline cloud",
                "Local-only cloud",
                "Single-user cloud",
            ],
            "answer": 0,
        },
    ],
    "web-development": [
        {
            "question": "Which technology defines webpage structure?",
            "options": ["HTML", "SQL", "FTP", "CSV"],
            "answer": 0,
        },
        {
            "question": "Which technology styles webpages?",
            "options": ["CSS", "DNS", "HTTP", "CSV"],
            "answer": 0,
        },
        {
            "question": "Which language adds interactivity to webpages?",
            "options": ["JavaScript", "SQL", "CSV", "XML"],
            "answer": 0,
        },
    ],
    "data-analytics": [
        {
            "question": "What is a main goal of data analytics?",
            "options": [
                "Delete all data",
                "Find patterns and support decisions",
                "Turn off computers",
                "Replace every database",
            ],
            "answer": 1,
        },
        {
            "question": "What is data cleaning?",
            "options": [
                "Improving data quality",
                "Changing a screen",
                "Printing documents",
                "Installing a keyboard",
            ],
            "answer": 0,
        },
        {
            "question": "Which chart commonly shows changes over time?",
            "options": [
                "Line chart",
                "Folder icon",
                "Text paragraph",
                "File extension",
            ],
            "answer": 0,
        },
    ],
    "iot": [
        {
            "question": "What does IoT stand for?",
            "options": [
                "Internet of Things",
                "Input of Text",
                "Internal Online Transfer",
                "Internet of Tables",
            ],
            "answer": 0,
        },
        {
            "question": "What can an IoT sensor do?",
            "options": [
                "Measure conditions",
                "Replace the internet",
                "Print every document",
                "Guarantee unlimited storage",
            ],
            "answer": 0,
        },
        {
            "question": "Which is an IoT application?",
            "options": [
                "A connected temperature sensor",
                "An unconnected notebook",
                "A plain pencil",
                "A blank sheet of paper",
            ],
            "answer": 0,
        },
    ],
}


# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def get_all_lessons():
    lessons = []

    for course_item in COURSES:
        for lesson_item in course_item["lessons"]:
            lessons.append({
                **lesson_item,
                "course_slug": course_item["slug"],
                "course_title": course_item["title"],
            })

    return lessons


def find_course(slug):
    for course_item in COURSES:
        if course_item["slug"] == slug:
            return course_item

    return None


def find_lesson(lesson_id):
    for course_item in COURSES:
        for lesson_item in course_item["lessons"]:
            if lesson_item["id"] == lesson_id:
                return course_item, lesson_item

    return None, None


def get_youtube_embed_url(url):
    """Convert supported YouTube links into embed URLs."""

    if not url:
        return None

    try:
        parsed = urlparse(url.strip())
        hostname = (parsed.hostname or "").lower()
        video_id = None

        if hostname == "youtu.be":
            video_id = parsed.path.strip("/").split("/")[0]

        elif hostname in (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtube-nocookie.com",
            "www.youtube-nocookie.com",
        ):
            if parsed.path == "/watch":
                video_id = parse_qs(parsed.query).get("v", [None])[0]

            elif parsed.path.startswith(("/embed/", "/shorts/")):
                parts = parsed.path.strip("/").split("/")

                if len(parts) >= 2:
                    video_id = parts[1]

        if video_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return f"https://www.youtube.com/embed/{video_id}"

    except (ValueError, AttributeError):
        pass

    return None


# =====================================================
# 6. SHORT VIDEO PREVIEW FROM ACTUAL CAPTIONS
# =====================================================

# Avoid retrieving captions repeatedly during the same app run.
VIDEO_DESCRIPTION_CACHE = {}


def get_video_description(video_url):
    """
    Retrieve available YouTube captions and create a short excerpt.
    This is caption-based, not an AI-generated summary.
    """

    embed_url = get_youtube_embed_url(video_url)

    if not embed_url:
        return None

    video_id = embed_url.rsplit("/", 1)[-1]

    if video_id in VIDEO_DESCRIPTION_CACHE:
        return VIDEO_DESCRIPTION_CACHE[video_id]

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)

        caption_text = " ".join(
            snippet.text for snippet in transcript
        )

        caption_text = re.sub(r"\s+", " ", caption_text).strip()

        if not caption_text:
            VIDEO_DESCRIPTION_CACHE[video_id] = None
            return None

        # Use the opening 45 words from the actual captions.
        words = caption_text.split()
        preview = " ".join(words[:45])

        if len(words) > 45:
            preview += "..."

        VIDEO_DESCRIPTION_CACHE[video_id] = preview
        return preview

    except Exception as error:
        print(f"Captions unavailable for {video_id}: {error}")
        VIDEO_DESCRIPTION_CACHE[video_id] = None
        return None


def get_completed_lesson_ids():
    return {
        item.lesson_id
        for item in Progress.query.filter_by(completed=True).all()
    }


def calculate_average_score():
    results = QuizResult.query.all()

    total_score = sum(result.score for result in results)
    total_questions = sum(result.total for result in results)

    if total_questions == 0:
        return 0

    return round(total_score / total_questions * 100)


# =====================================================
# 7. GLOBAL TEMPLATE VARIABLES
# =====================================================

@app.context_processor
def inject_template_variables():
    total_lessons = len(get_all_lessons())

    try:
        total_done = Progress.query.filter_by(completed=True).count()
    except Exception:
        total_done = 0

    percentage = (
        round(total_done / total_lessons * 100)
        if total_lessons
        else 0
    )

    return {
        "current_learner": "Learner",
        "total_done": total_done,
        "total_lessons": total_lessons,
        "progress_percentage": percentage,
    }


# =====================================================
# 8. HOME PAGE
# =====================================================

@app.route("/")
def index():
    total_done = Progress.query.filter_by(completed=True).count()
    total_lessons = len(get_all_lessons())

    percentage = (
        round(total_done / total_lessons * 100)
        if total_lessons
        else 0
    )

    completed_ids = get_completed_lesson_ids()
    display_courses = []

    for course_item in COURSES:
        course_data = dict(course_item)
        lesson_list = course_item["lessons"]

        completed_count = sum(
            1
            for item in lesson_list
            if item["id"] in completed_ids
        )

        course_data["progress"] = (
            round(completed_count / len(lesson_list) * 100)
            if lesson_list
            else 0
        )

        course_data["category"] = course_item["title"]
        course_data["emoji"] = course_item["icon"]
        course_data["level"] = "Beginner"
        course_data["duration"] = f"{len(lesson_list)} lessons"

        course_data["color"] = {
            "cloud-computing": "lilac",
            "web-development": "mint",
            "data-analytics": "peach",
            "iot": "blue",
        }.get(course_item["slug"], "lilac")

        display_courses.append(course_data)

    return render_template(
        "index.html",
        courses=display_courses,
        total_done=total_done,
        total_lessons=total_lessons,
        progress_percentage=percentage,
        avg_score=calculate_average_score(),
    )


# =====================================================
# 9. COURSES PAGE
# =====================================================

@app.route("/courses")
def courses():
    return render_template("courses.html", courses=COURSES)


# =====================================================
# 10. COURSE DETAILS
# =====================================================

@app.route("/course/<slug>")
def course(slug):
    selected_course = find_course(slug)

    if selected_course is None:
        flash("Course not found.", "error")
        return redirect(url_for("courses"))

    return render_template(
        "course.html",
        course=selected_course,
        completed_ids=get_completed_lesson_ids(),
    )


# =====================================================
# 11. LESSON PAGE
# =====================================================

@app.route("/lesson/<int:lesson_id>")
def lesson(lesson_id):
    selected_course, selected_lesson = find_lesson(lesson_id)

    if selected_lesson is None:
        flash("Lesson not found.", "error")
        return redirect(url_for("courses"))

    lesson_data = dict(selected_lesson)

    lesson_data["youtube_embed_url"] = get_youtube_embed_url(
        selected_lesson.get("video_url", "")
    )

    lesson_data["youtube_search_url"] = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(selected_lesson["title"])
    )

    # Caption-based preview from the selected video's content.
    lesson_data["video_description"] = get_video_description(
        selected_lesson.get("video_url", "")
    )

    completed = Progress.query.filter_by(
        lesson_id=lesson_id,
        completed=True,
    ).first() is not None

    return render_template(
        "lesson.html",
        lesson=lesson_data,
        course=selected_course,
        completed=completed,
    )


# =====================================================
# 12. MARK LESSON AS COMPLETED
# =====================================================

@app.route("/lesson/<int:lesson_id>/complete", methods=["POST"])
def complete_lesson(lesson_id):
    selected_course, selected_lesson = find_lesson(lesson_id)

    if selected_lesson is None:
        flash("Lesson not found.", "error")
        return redirect(url_for("courses"))

    progress = Progress.query.filter_by(
        lesson_id=lesson_id
    ).first()

    if progress is None:
        progress = Progress(
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow(),
        )
        db.session.add(progress)
    else:
        progress.completed = True
        progress.completed_at = datetime.utcnow()

    db.session.commit()

    flash("Lesson marked as completed!", "success")
    return redirect(url_for("lesson", lesson_id=lesson_id))


# =====================================================
# 13. COURSE QUIZ
# =====================================================

@app.route("/quiz/<slug>", methods=["GET", "POST"])
def quiz(slug):
    selected_course = find_course(slug)

    if selected_course is None:
        flash("Course not found.", "error")
        return redirect(url_for("courses"))

    questions = QUIZZES.get(slug, [])
    score = None

    if request.method == "POST":
        score = 0

        for index, question_item in enumerate(questions):
            selected_answer = request.form.get(f"question_{index}")

            if selected_answer is not None:
                try:
                    if int(selected_answer) == question_item["answer"]:
                        score += 1
                except (ValueError, TypeError):
                    pass

        result = QuizResult(
            course_slug=slug,
            score=score,
            total=len(questions),
        )

        db.session.add(result)
        db.session.commit()

        flash(
            f"Quiz submitted! Your score is {score}/{len(questions)}.",
            "success",
        )

    return render_template(
        "quiz.html",
        course=selected_course,
        questions=questions,
        score=score,
        total=len(questions),
    )


# =====================================================
# 14. BASIC LEARNING ASSISTANT
# =====================================================

@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    answer = None
    question = ""

    if request.method == "POST":
        question = request.form.get("question", "").strip()

        if question:
            answer = (
                "This is the basic LearnSphere assistant. "
                "It is not connected to a real AI model yet."
            )
        else:
            answer = "Please enter a question."

    return render_template(
        "assistant.html",
        answer=answer,
        question=question,
    )


# =====================================================
# 15. LEARNER PROFILE
# =====================================================

@app.route("/profile")
def profile():
    completed_lessons = Progress.query.filter_by(
        completed=True
    ).count()

    total_lessons = len(get_all_lessons())

    quiz_results = QuizResult.query.order_by(
        QuizResult.attempted_at.desc()
    ).all()

    return render_template(
        "profile.html",
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        quiz_results=quiz_results,
    )


# =====================================================
# 16. HEALTH CHECK
# =====================================================

@app.route("/health")
def health():
    return {
        "status": "ok",
        "application": "LearnSphere",
    }


# =====================================================
# 17. DATABASE INITIALIZATION
# =====================================================

def initialize_database():
    db.create_all()

    inspector = inspect(db.engine)

    if "progress" in inspector.get_table_names():
        columns = {
            column["name"]
            for column in inspector.get_columns("progress")
        }

        with db.engine.begin() as connection:
            if "completed" not in columns:
                connection.execute(text(
                    "ALTER TABLE progress "
                    "ADD COLUMN completed BOOLEAN NOT NULL DEFAULT 1"
                ))

            if "completed_at" not in columns:
                connection.execute(text(
                    "ALTER TABLE progress ADD COLUMN completed_at DATETIME"
                ))

    inspector = inspect(db.engine)

    if "quiz_result" in inspector.get_table_names():
        columns = {
            column["name"]
            for column in inspector.get_columns("quiz_result")
        }

        with db.engine.begin() as connection:
            if "course_slug" not in columns:
                connection.execute(text(
                    "ALTER TABLE quiz_result "
                    "ADD COLUMN course_slug VARCHAR(100) NOT NULL DEFAULT ''"
                ))

            if "score" not in columns:
                connection.execute(text(
                    "ALTER TABLE quiz_result "
                    "ADD COLUMN score INTEGER NOT NULL DEFAULT 0"
                ))

            if "total" not in columns:
                connection.execute(text(
                    "ALTER TABLE quiz_result "
                    "ADD COLUMN total INTEGER NOT NULL DEFAULT 0"
                ))

            if "attempted_at" not in columns:
                connection.execute(text(
                    "ALTER TABLE quiz_result ADD COLUMN attempted_at DATETIME"
                ))


with app.app_context():
    initialize_database()


# =====================================================
# 18. START THE SERVER
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)