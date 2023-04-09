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
    base64 = base64.b64encode(byte_img).decode('utf-8')
    return f"data:image/jpeg;base64,{base64}"
