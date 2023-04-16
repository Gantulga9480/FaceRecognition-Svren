import os
import base64
import numpy as np
import cv2
from flask import jsonify


def returnStatus(data: str = None, status: str = "Successful", code: int = 200):
    res = jsonify({
        "data": data,
        "status": status,
        "code": code
    })
    res.status_code = code
    res.headers.add('Content-Type', 'application/json')
    return res


def makeIMGfromURI(uri: str):
    encoded_data = uri.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img_raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img_raw


def makeURIfromIMG(img) -> str:
    byte_img = np.array(cv2.imencode('.png', img)[1]).tobytes()
    img64 = base64.b64encode(byte_img).decode('utf-8')
    return f"data:image/jpeg;base64,{img64}"


def get_user(id, name: str):
    try:
        raw_img = cv2.imread(f"users/{id}.{name}.jpg")
        uri = makeURIfromIMG(raw_img)
        return {"id": id, "name": name, "img_uri": uri}
    except FileNotFoundError:
        return {"id": id, "name": name, "img_uri": None}


def get_users():
    users = []
    for id, name in saved_users():
        users.append(get_user(id, name))
    return users


def delete_user(user_id):
    for id, name in saved_users():
        if id == user_id:
            try:
                os.remove(f"users/{id}.{name}.jpg")
                return True
            except FileNotFoundError:
                return False
    return False


def save_user(name, face):
    new_user_id = len(saved_users()) + 1
    cv2.imwrite(f"users/{new_user_id}.{name}.jpg", face)


def saved_users():
    users = []
    for _, _, files in os.walk("users"):
        if files.__len__() > 0:
            for file in files:
                if file.endswith(".jpg"):
                    id_name_ext = file.split('.')
                    user_id = id_name_ext.pop(0)
                    name = id_name_ext.pop(0)
                    users.append((user_id, name))
    users = sorted(users, key=lambda x: int(x[0]))
    return users
