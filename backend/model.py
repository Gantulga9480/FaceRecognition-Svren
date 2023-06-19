import cv2
import os
from face_detection import FaceDetection
from face_recognition import FaceRecognition
from utils import IMG_ROOT


DEFAULT_REF_PATH = IMG_ROOT
FIND_PERSON_REF_PATH = r'person'
FIND_ALL_REF_PATH = r'people'


class Model:

    def __init__(self) -> None:
        self.face_detect = FaceDetection(r'face_mask_detection.pb')
        self.face_recognition = FaceRecognition(r"Facenet_masked_model.pb")
        self.face_recognition.load_embed(DEFAULT_REF_PATH)
        self.current_ref = DEFAULT_REF_PATH
        self.cap = None
        self.cap_frame_count = 0
        self.cap_frame_rate = 0
        self.cap_frame_counter = 0
        self.cap_frame_buffer = []
        self.cap_timestamp_buffer = []
        self.cap_save_count = 0
        try:
            os.mkdir(DEFAULT_REF_PATH)
        except FileExistsError:
            pass
        try:
            os.mkdir(FIND_PERSON_REF_PATH)
        except FileExistsError:
            pass
        try:
            os.mkdir(FIND_ALL_REF_PATH)
        except FileExistsError:
            pass

    def change_ref(self, ref_path):
        self.current_ref = ref_path
        self.face_recognition.load_embed(ref_path)

    def crop_face(self, img):
        bboxes, re_confidence, re_mask_id = self.face_detect.detect(img)
        face = None
        if len(bboxes) == 1:
            for i, bbox in enumerate(bboxes):
                face = img[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                break
        return face

    def cap_forward(self):
        current_batch_count = 0
        frame_copy = None
        while current_batch_count < 30:
            ret, frame = self.cap.read()
            if ret:
                frame_copy = frame.copy()
                if self.cap_frame_counter % (self.cap_frame_rate // 2) == 0:
                    bboxes, re_confidence, re_mask_id = self.face_detect.detect(frame)
                    for i, bbox in enumerate(bboxes):
                        name, embed = self.face_recognition.recognize(frame, bbox)
                        if name != "Unknown" and self.current_ref == FIND_PERSON_REF_PATH:
                            img_temp = frame_copy[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                            time_seconds = int(self.cap.get(cv2.CAP_PROP_POS_MSEC) // 1000)
                            self.cap_frame_buffer.append(img_temp)
                            self.cap_timestamp_buffer.append(time_seconds)
                            print("Person found at {}".format(time_seconds))
                        elif name == "Unknown" and self.current_ref == FIND_ALL_REF_PATH:
                            img_temp = frame_copy[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                            time_seconds = int(self.cap.get(cv2.CAP_PROP_POS_MSEC) // 1000)
                            self.cap_frame_buffer.append(img_temp)
                            self.cap_timestamp_buffer.append(time_seconds)
                            print("An unknown person found at {}".format(time_seconds))
                            save_path = f"person_{time_seconds}_{self.cap_save_count}.jpg"
                            save_path = os.path.join(FIND_ALL_REF_PATH, save_path)
                            cv2.imwrite(save_path, img_temp)
                            self.cap_save_count += 1
                            self.face_recognition.add_embed(embed, FIND_ALL_REF_PATH)
                self.cap_frame_counter += 1
                current_batch_count += 1
            else:
                return 100, frame_copy
        return int((self.cap_frame_counter / self.cap_frame_count) * 100), frame_copy

    def cap_init(self, video_path: str):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(video_path)
        self.cap_frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.cap_frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.cap_save_count = 0
        self.cap_frame_counter = 0
        self.cap_frame_buffer.clear()
        self.cap_timestamp_buffer.clear()

    def cap_deinit(self):
        if self.cap is not None:
            self.cap.release()
        self.cap_frame_counter = 0
        self.cap_frame_buffer.clear()
        self.cap_timestamp_buffer.clear()

    def detect(self, img):
        names = []
        bboxes, re_confidence, re_mask_id = self.face_detect.detect(img)
        if len(bboxes) > 0:
            for i, bbox in enumerate(bboxes):
                name, _ = self.face_recognition.recognize(img, bbox)
                names.append(name)
        return names, bboxes
