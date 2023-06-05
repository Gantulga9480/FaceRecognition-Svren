import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        print('growth set failed -------------------')
from face_detection import FaceDetection
from face_recognition import FaceRecognition


class Model:

    def __init__(self) -> None:
        self.face_detect = FaceDetection(r'face_mask_detection.pb')
        self.face_recognition = FaceRecognition(r"Facenet_masked_model.pb", r"users")

    def refresh_face_dist(self):
        self.face_recognition.load_dist()

    def crop_face(self, img):
        bboxes, re_confidence, re_mask_id = self.face_detect.detect(img)
        face = None
        if len(bboxes) > 0:
            for i, bbox in enumerate(bboxes):
                face = img[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                break
        return face

    def detect(self, img):
        names = []
        bboxes, re_confidence, re_mask_id = self.face_detect.detect(img)
        if len(bboxes) > 0:
            for i, bbox in enumerate(bboxes):
                name = self.face_recognition.recognize(img, bbox)
                names.append(name)
                # ----display results
                # confi = round(re_confidence[i], 2)
                # class_id = re_mask_id[i]
                # color = (0, 255, 0) if class_id == 0 else (0, 0, 255)  # BGR
        return names, bboxes
