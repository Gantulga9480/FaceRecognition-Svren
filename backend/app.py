import os
from flask import Flask, request
from flask_cors import CORS
import cv2
import uuid
from model import Model, FIND_PERSON_REF_PATH, FIND_ALL_REF_PATH, DEFAULT_REF_PATH
from utils import (makeIMGfromURI, makeURIfromIMG, returnStatus, get_users_info,
                   get_user_info, delete_user, delete_user_img, add_user,
                   saved_users, add_user_img, saveVIDEOfromURI)


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
    if admin_token is not None:
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
    names, bboxes = model.detect(img)
    preds = [{"name": names[i], "box": bboxes[i]} for i in range(len(names))]
    return returnStatus(data={"preds": preds})


@app.post("/detect-annot")
def detect_annot():
    data = request.get_json(silent=True)
    try:
        img_uri = data['img_uri']
    except KeyError:
        return returnStatus(status="Bad request - key 'img_uri' value not provided", code=400)
    try:
        img = makeIMGfromURI(img_uri)
    except Exception:
        return returnStatus(status="Bad request - Invalid image URI", code=400)
    org_img = img.copy()
    names, bboxes = model.detect(img)
    for i, bbox in enumerate(bboxes):
        color = (0, 255, 0) if names[i] != "Unknown" else (0, 0, 255)
        cv2.rectangle(org_img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)
        display_msg = "{}".format(names[i])
        result_coor = (bbox[0] + 2, bbox[1] - 3)
        cv2.putText(org_img, display_msg, result_coor, cv2.FONT_HERSHEY_DUPLEX, 1, color)
    img_uri = makeURIfromIMG(org_img)
    height, width, _ = org_img.shape
    return returnStatus(data={'img_uri': img_uri, 'width': width, 'height': height})


@app.post("/find-person-start")
def find_person_start():
    data = request.get_json(silent=True)
    try:
        video_uri = data['video']
    except KeyError:
        return returnStatus(status="Bad request - key 'video' not provided", code=400)
    try:
        ref_imgs = data['imgs']
    except KeyError:
        return returnStatus(status="Bad request - key 'imgs' not provided", code=400)

    if len(ref_imgs) > 0:
        for r, ds, fs in os.walk(FIND_PERSON_REF_PATH):
            for f in fs:
                os.remove(os.path.join(r, f))
        imgs = []
        for i, img in enumerate(ref_imgs):
            img = makeIMGfromURI(img)
            _, bboxes = model.detect(img)
            if len(bboxes) > 1 or len(bboxes) == 0:
                return returnStatus(status="Bad request - Invalid image provided", code=400)
            face = img[bboxes[0][1]:bboxes[0][1] + bboxes[0][3], bboxes[0][0]:bboxes[0][0] + bboxes[0][2], :]
            imgs.append(face)
        for i, img in enumerate(imgs):
            cv2.imwrite(os.path.join(FIND_PERSON_REF_PATH, f'{i}.jpg'), img)

        model.change_ref(FIND_PERSON_REF_PATH)
    else:
        for r, ds, fs in os.walk(FIND_ALL_REF_PATH):
            for f in fs:
                os.remove(os.path.join(r, f))
        model.change_ref(FIND_ALL_REF_PATH)

    saveVIDEOfromURI(video_uri, 'temp.mp4')
    del video_uri
    del ref_imgs

    model.cap_init('temp.mp4')

    return returnStatus(data='1')


@app.get("/find-person-forward")
def find_person_forward():
    if model.cap is None:
        return returnStatus(status="Bad request", code=400)
    percent, frame = model.cap_forward()
    if frame is not None:
        img_uri = makeURIfromIMG(frame)
    else:
        img_uri = None

    return returnStatus(data={
        'percent': percent,
        'frame': img_uri
    })


@app.get("/find-person-stop")
def find_person_stop():
    if model.cap is None:
        return returnStatus(status="Bad request", code=400)
    info = []
    for ts, img in list(zip(model.cap_timestamp_buffer, model.cap_frame_buffer)):
        info.append({
            'timestamp': ts,
            'image': makeURIfromIMG(img)
        })
    model.change_ref(DEFAULT_REF_PATH)
    model.cap_deinit()
    return returnStatus(data=info)


@app.get("/users-info")
def users_info():
    admin_token = request.args.get("token", None, type=str)
    if admin_token is not None:
        if admin_token == token:
            data = saved_users()
            users_info = []
            for id, name in data:
                users_info.append({'id': id, 'name': name})
            return returnStatus(data=users_info, status="ok", code=200)
        return returnStatus(status="Unauthorized", code=401)
    return returnStatus(status="Bad request", code=400)


@app.get("/users")
def users():
    admin_token = request.args.get("token", None, type=str)
    if admin_token is not None:
        if admin_token == token:
            users_info = get_users_info()
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
            user_info = get_user_info(user_id, user_name)
            return returnStatus(data=user_info, status="ok", code=200)
        return returnStatus(status="Unauthorized", code=401)
    return returnStatus(status="Bad request", code=400)


@app.delete("/user/<id>")
def user_delete(id):
    if id:
        if delete_user(id):
            model.change_ref(DEFAULT_REF_PATH)
            return returnStatus(status="ok", code=200)
        else:
            return returnStatus(status="Not found", code=404)
    return returnStatus(status="Bad request", code=400)


@app.delete("/user/<id>/<count>")
def user_delete_img(id, count):
    if id and count:
        if delete_user_img(id, count):
            model.change_ref(DEFAULT_REF_PATH)
            return returnStatus(status="ok", code=200)
        else:
            return returnStatus(status="Not found", code=404)
    return returnStatus(status="Bad request", code=400)


@app.post("/user/add-img")
def user_add_img():
    data = request.get_json(silent=True)
    try:
        admin_token = data["token"]
        if admin_token != token:
            return returnStatus(status="Unauthorized", code=401)
    except KeyError:
        return returnStatus(status="Bad request", code=400)

    try:
        id = data["id"]
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
        add_user_img(id, name, face)
        model.change_ref(DEFAULT_REF_PATH)
    else:
        return returnStatus(status="Bad request - Invalid image URI", code=400)
    return returnStatus(status="ok", code=200)


@app.post("/user/add")
def user_add():
    data = request.get_json(silent=True)
    try:
        admin_token = data["token"]
        if admin_token != token:
            return returnStatus(status="Unauthorized", code=401)
    except KeyError:
        return returnStatus(status="Bad request", code=400)

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
        add_user(name, face)
        model.change_ref(DEFAULT_REF_PATH)
    else:
        return returnStatus(status="Bad request - Invalid image URI", code=400)
    return returnStatus(status="ok", code=200)


@app.errorhandler(404)
def not_found(e):
    return returnStatus(status="Page Not Found", code=404)
