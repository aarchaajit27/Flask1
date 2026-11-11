import json
import os
import re
 
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import generate_password_hash

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
 
_client = None
 
def get_collection():
    """Connect to MongoDB Atlas (once) and return the users collection."""
    global _client
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI is not set. Check your .env file.")
    if _client is None:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    users = _client[os.getenv("DB_NAME", "signup_db")]["users"]
    users.create_index("email", unique=True)   # no duplicate emails
    return users
@app.route("/api")
def api():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)                    # returns a JSON list
    except FileNotFoundError:
        return jsonify(error="data.json not found"), 500
    except json.JSONDecodeError:
        return jsonify(error="data.json is not valid JSON"), 500


# ---------- Task 2: form -> MongoDB Atlas ----------
@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", error=None, form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    form = {"name": name, "email": email}       # keep typed values on error

    # validation
    if not name:
        return render_template("signup.html", error="Name is required.", form=form), 400
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return render_template("signup.html", error="Enter a valid email.", form=form), 400
    if len(password) < 8:
        return render_template("signup.html", error="Password must be 8+ characters.", form=form), 400

    # insert into MongoDB Atlas
    try:
        get_collection().insert_one({
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
        })
    except DuplicateKeyError:
        return render_template("signup.html", error="Email already registered.", form=form), 409
    except (PyMongoError, RuntimeError) as e:
        return render_template("signup.html", error=f"Database error: {e}", form=form), 503

    # success: redirect to another page
    return redirect(url_for("success"))


@app.route("/success")
def success():
    return render_template("success.html", message="Data submitted successfully")

@app.route('/todo')
def todo():
    return render_template('todo.html')

if __name__ == '__main__':
    app.run(debug=True)

# import json
# import os
# from flask import Flask, jsonify

import json
import os
from flask import Flask, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")


# import json
# import os
# from flask import Flask, jsonify

# app = Flask(__name__)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_FILE = os.path.join(BASE_DIR, "data.json")


# @app.route("/api")
# def api():
#     try:
#         with open(DATA_FILE, "r") as f:
#             data = json.load(f)         
#         return jsonify(data)
#     except FileNotFoundError:
#         return jsonify(error="data.json not found"), 500
#     except json.JSONDecodeError:
#         return jsonify(error="data.json is not valid JSON"), 500


# if __name__ == "__main__":
#     app.run(debug=True)