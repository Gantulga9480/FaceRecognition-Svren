import cv2
from face_detection import FaceDetection
from face_recognition import FaceRecognition


class Model:

    def __init__(self) -> None:
        self.face_detect = FaceDetection(r'face_mask_detection.pb')
        self.face_recognition = FaceRecognition(r"Facenet_masked_model.pb", r"known_faces")

    def detect(self, img):
        names = []
        boxes = []
        bboxes, re_confidence, re_mask_id = self.face_detect.detect(img)
        if len(bboxes) > 0:
            for i, bbox in enumerate(bboxes):
                name = self.face_recognition.recognize(img, bbox)
                names.append(name)
                # ----display results
                # confi = round(re_confidence[i], 2)
                # class_id = re_mask_id[i]
                # color = (0, 255, 0) if class_id == 0 else (0, 0, 255)  # BGR
                # cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)
                boxes.append(bbox)
                # display_msg = "{},{},{}".format(self.face_detect.id2class[class_id], confi, name)
                # result_coor = (bbox[0] + 2, bbox[1] - 2)
                # cv2.putText(img, display_msg, result_coor, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)
        return names, boxes
