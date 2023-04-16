from flask import Flask, request
from model import Model
from flask_cors import CORS
from model import Model
import uuid
import cv2
from utils import makeIMGfromURI, returnStatus, get_users, get_user, delete_user, save_user


token = str(uuid.uuid1())
model = Model()
app = Flask(__name__)
CORS(app)

user_name = "ganaa"
user_pass = "1234"


@app.route('/')
def index():
    return returnStatus(status="Server online", code=200)


@app.get('/admin')
def admin():
    admin_token = request.args.get("token", None, type=str)
    if admin_token:
        if admin_token == token:
            return returnStatus(status="ok", code=200)
        return returnStatus(status="Unauthorized", code=401)
    return returnStatus(status="Bad request", code=400)


@app.post('/admin-login')
def login():
    data = request.get_json(silent=True)
    try:
        name = data["name"]
        password = data["pass"]
        if (name == user_name and password == user_pass):
            return returnStatus(data={"token": token}, status="ok", code=200)
        else:
            return returnStatus(status="Unauthorized", code=401)
    except KeyError:
        return returnStatus(status="Bad request", code=400)


@app.post("/detect")
def detect():
    data = request.get_json(silent=True)
    try:
        img_uri = data['img_uri']
    except KeyError:
        return returnStatus(status="Bad request - key 'img_uri' value not provided", code=400)
    try:
        img = makeIMGfromURI(img_uri)
    except Exception:
        return returnStatus(status="Bad request - Invalid image URI", code=400)
    names, boxes = model.detect(img)
    preds = [{"name": names[i], "box": boxes[i]} for i in range(len(names))]
    return returnStatus(data={"preds": preds})


@app.get("/users")
def users():
    admin_token = request.args.get("token", None, type=str)
    if admin_token:
        if admin_token == token:
            users_info = get_users()
            return returnStatus(data=users_info, status="ok", code=200)
        return returnStatus(status="Unauthorized", code=401)
    return returnStatus(status="Bad request", code=400)


@app.get("/user")
def user():
    admin_token = request.args.get("token", None, type=str)
    user_id = request.args.get("id", None, type=str)
    user_name = request.args.get("name", None, type=str)
    if admin_token and user_name:
        if admin_token == token:
            user_info = get_user(user_id, user_name)
            return returnStatus(data=user_info, status="ok", code=200)
        return returnStatus(status="Unauthorized", code=401)
    return returnStatus(status="Bad request", code=400)


@app.delete("/user/<id>")
def user_delete(id):
    if id:
        if delete_user(id):
            model.refresh_face_dist()
            return returnStatus(status="ok", code=200)
        else:
            return returnStatus(status="Not found", code=404)
    return returnStatus(status="Bad request", code=400)


@app.post("/user/add")
def user_add():
    data = request.get_json(silent=True)
    try:
        name = data["name"]
        img_uri = data["img_uri"]
    except KeyError:
        return returnStatus(status="Bad request", code=400)
    try:
        img = makeIMGfromURI(img_uri)
    except Exception:
        return returnStatus(status="Bad request - Invalid image URI", code=400)
    face = model.crop_face(img)
    if face is not None:
        save_user(name, face)
        model.refresh_face_dist()
    else:
        return returnStatus(status="warn", code=200)
    return returnStatus(status="ok", code=200)


@app.errorhandler(404)
def not_found(e):
    return returnStatus(status="Page Not Found", code=404)
