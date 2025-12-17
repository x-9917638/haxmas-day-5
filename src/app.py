import uuid
from os import environ

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_uuid import FlaskUUID  # pyright: ignore[reportMissingTypeStubs]
from sqlalchemy import select
from sqlalchemy.sql.operators import eq
from werkzeug.security import check_password_hash, generate_password_hash

from .schema import construct_db

_ = load_dotenv("../.env")

if not (ADMIN_PASSWORD := environ.get("ADMIN_PASSWORD")):
    print("[WARN]: ADMIN_PASSWORD not found; Admin only routes unavailable.")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///default.db"

    return app


app = create_app()
_ = FlaskUUID(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

db = construct_db(app)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/form")
def form():
    return render_template("form.html")


@app.post("/submit")
@limiter.limit("50 per day")
def submit():
    if not request.is_json:
        return "415 Unsupported Media Type", 415

    data: dict[str, str] = request.get_json()  # pyright: ignore[reportAny]

    if not (text := data.get("text")):
        return "400 Bad Request (A message is required.)", 400
    if not (password := data.get("password")):
        return "400 Bad Request (A password is required.)", 400

    author = data.get("author")

    if len(text) > 10000:
        return "413 Content Too Large (Message must be < 10000 characters.)", 413

    if len(password) < 8:
        return "400 Bad Request (Password must be > 8 characters.)", 400

    password = generate_password_hash(password)

    id = uuid.uuid4()

    message = db.Message(id=id, text=text, author=author, password=password)  # pyright: ignore[reportAny]
    db.session.add(message)  # pyright: ignore[reportAny]
    try:
        db.session.commit()
    except Exception as e:
        return f"500 Internal Server Error {e}", 500

    return jsonify(id=message.id), 201  # pyright: ignore[reportAny]


@app.route("/edit/", methods=["PATCH", "GET"])
def edit():
    if request.method == "GET":
        return render_template("edit.html")

    if not request.is_json:
        return "415 Unsupported Media Type", 415

    data: dict[str, str] = request.get_json()  # pyright: ignore[reportAny]

    if not (password := data.get("password")):
        return "400 Bad Request", 400

    try:
        id = uuid.UUID(data.get("id"))
    except ValueError:
        id = None
    if not id:
        return "400 Bad Request", 400

    query = select(db.Message).where(eq(db.Message.id, id))  # pyright: ignore[reportAny, reportArgumentType]

    message = db.session.scalar(query)

    if not message:
        return "400 Bad Request", 400

    if not check_password_hash(message.password, password):  # pyright: ignore[reportAny]
        return "401 Unauthorized", 401  # :)

    text: str = message.text  # pyright: ignore[reportAny]

    new_text = data.get("text")
    if not new_text or new_text == text:
        return "200 OK", 200
    message.text = new_text
    db.session.add(message)  # pyright: ignore[reportAny]
    db.session.commit()
    return "200 OK", 200


@app.route("/all", methods=["POST", "GET"])
def all():
    if not ADMIN_PASSWORD:
        return "403 Forbidden", 403

    if not (password := request.args.get("password")):
        return render_template("all.html", auth=False)

    if password.strip() != ADMIN_PASSWORD:
        return render_template("all.html", auth=False)

    query = select(db.Message)
    messages = db.session.scalars(query)

    return render_template("all.html", auth=True, messages=messages)
