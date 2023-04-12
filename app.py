from flask import Flask, request
from model import Model
from flask_cors import CORS
from model import Model
import uuid
from utils import makeIMGfromURI, makeURIfromIMG, returnStatus


token = str(uuid.uuid1())
model = Model()
app = Flask(__name__)
CORS(app)

user_name = "ganaa"
user_pass = "1234"


@app.route('/')
def index():
    return returnStatus(status="Server online", code=200)


@app.get('/test')
def search():
    return returnStatus(status="Bad request", code=400)


@app.get('/admin')
def admin():
    user_token = request.args.get('token', None, type=str)
    if user_token:
        if user_token == token:
            return returnStatus(data="ok", code=200)
        return returnStatus(data="no", code=200)
    return returnStatus(status="Bad request", code=400)


@app.post('/admin-login')
def login():
    data = request.get_json(silent=True)
    try:
        name = data["name"]
        password = data["pass"]
        if (name == user_name and password == user_pass):
            return returnStatus(data={"status": "ok", "token": token}, code=200)
        else:
            return returnStatus(data={"status": "no"}, code=200)
    except KeyError:
        return returnStatus(status="Bad request", code=400)


@app.post("/detect")
def load():
    data = request.get_json(silent=True)
    try:
        img_uri = data['img_uri']
    except KeyError:
        return returnStatus(status="Bad request - key 'img_uri' value not provided", code=400)
    try:
        img = makeIMGfromURI(img_uri)
    except Exception:
        return returnStatus(status="Bad request - Invalid Image URI", code=400)
    names, boxes = model.detect(img)
    preds = [{"name": names[i], "box": boxes[i]} for i in range(len(names))]
    return returnStatus(data={"preds": preds})


@app.errorhandler(404)
def not_found(e):
    return returnStatus(status="Page Not Found", code=404)
