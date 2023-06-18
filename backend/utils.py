import os
import base64
import numpy as np
import cv2
from flask import jsonify
import uuid
import shutil


IMG_ROOT = r'users'
MAX_IMG_PER_USER = 100


def returnStatus(data: str = None, status: str = "Successful", code: int = 200):
    res = jsonify({
        "data": data,
        "status": status,
        "code": code
    })
    res.status_code = code
    res.headers.add('Content-Type', 'application/json')
    return res


def saveVIDEOfromURI(uri: str, path: str):
    with open(path, 'wb') as f:
        f.write(base64.b64decode(uri.split(',')[1]))


def makeIMGfromURI(uri: str):
    encoded_data = uri.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img_raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img_raw


def makeURIfromIMG(img) -> str:
    byte_img = np.array(cv2.imencode('.jpg', img)[1]).tobytes()
    img64 = base64.b64encode(byte_img).decode('utf-8')
    return f"data:image/jpeg;base64,{img64}"


def get_user_info(id: str, name: str):
    files = []
    for r, ds, fs in os.walk(os.path.join(IMG_ROOT, f"{id}.{name}")):
        for f in fs:
            if f.endswith(('png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG')):
                files.append(os.path.join(r, f))
    images = []
    image_ids = []
    for file in files:
        root, f = os.path.split(file)
        img_id = f.split('.')[-2]
        raw_img = cv2.imread(file)
        uri = makeURIfromIMG(raw_img)
        images.append(uri)
        image_ids.append(img_id)
    return {"id": id, "name": name, "image_info": {"image_ids": image_ids, "images": images}}


def get_users_info():
    users_info = []
    for id, name in saved_users():
        users_info.append(get_user_info(id, name))
    return users_info


def add_user(name, face):
    new_user_id = uuid.uuid1()
    save_path = os.path.join(IMG_ROOT, f"{new_user_id}.{name}")
    try:
        os.makedirs(save_path)
    except FileExistsError:
        shutil.rmtree(save_path)
        os.makedirs(save_path)
    cv2.imwrite(os.path.join(save_path, f'{name}.0.jpg'), face)


def add_user_img(id, name, face):
    counts = []
    save_path = os.path.join(IMG_ROOT, f"{id}.{name}")
    for r, ds, fs in os.walk(save_path):
        for f in fs:
            counts.append(f.split('.')[1])
    new_count = 0
    while True:
        new_count = np.random.randint(MAX_IMG_PER_USER)
        if new_count not in counts:
            break
    cv2.imwrite(os.path.join(save_path, f'{name}.{new_count}.jpg'), face)


def delete_user(user_id):
    for id, name in saved_users():
        if id == user_id:
            try:
                shutil.rmtree(os.path.join(IMG_ROOT, f"{id}.{name}"))
                return True
            except FileNotFoundError:
                break
    return False


def delete_user_img(user_id, count):
    for id, name in saved_users():
        if id == user_id:
            for r, ds, fs in os.walk(os.path.join(IMG_ROOT, f"{id}.{name}")):
                if fs.__len__() == 1:
                    try:
                        shutil.rmtree(os.path.join(IMG_ROOT, f"{id}.{name}"))
                        return True
                    except FileNotFoundError:
                        return False
                break
            path = os.path.join(IMG_ROOT, f"{id}.{name}", f"{name}.{count}.jpg")
            try:
                os.remove(path)
                return True
            except FileNotFoundError:
                return False
    return False


def saved_users():
    users = []
    for r, ds, fs in os.walk(IMG_ROOT):
        if ds.__len__() > 0:
            for d in ds:
                id_name = d.split('.')
                if id_name.__len__() == 2:
                    users.append((id_name[0], id_name[1]))
    return users
