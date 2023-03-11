import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import cv2
import time
from face_detection import FaceDetection
from face_recognition import FaceRecognition


def stream(camera_source=0):
    FPS = "loading"
    frame_count = 0
    save_count = 0

    cap = cv2.VideoCapture(camera_source)

    fd = FaceDetection(r'face_mask_detection.pb')
    fr = FaceRecognition(r"Facenet_masked_model.pb", r"known_faces")

    while(cap.isOpened()):
        ret, img = cap.read()
        if ret is True:
            img_copy = img.copy()
            bboxes, re_confidence, re_mask_id = fd.detect(img)
            if len(bboxes) > 0:
                for i, bbox in enumerate(bboxes):
                    name = fr.recognize(img, bbox)

                    # ----display results
                    confi = round(re_confidence[i], 2)
                    class_id = re_mask_id[i]
                    color = (0, 255, 0) if class_id == 0 else (0, 0, 255)  # BGR
                    cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)
                    display_msg = "{},{},{}".format(fd.id2class[class_id], confi, name)
                    result_coor = (bbox[0] + 2, bbox[1] - 2)
                    cv2.putText(img, display_msg, result_coor, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)

            # ----FPS calculation
            if frame_count == 0:
                t_start = time.time()
            frame_count += 1
            if frame_count >= 10:
                FPS = "FPS=%1f" % (10 / (time.time() - t_start))
                frame_count = 0

            cv2.putText(img, FPS, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # ----image display
            cv2.imshow("Face recognition", img)

            # ----keys handle
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                if len(bboxes) > 0:
                    save_count += 1
                    img_temp = img_copy[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                    save_path = f"__name__{save_count}.jpg"
                    save_path = os.path.join(r"known_faces", save_path)
                    cv2.imwrite(save_path, img_temp)
                    print("An image is saved to ", save_path)

    cap.release()
    cv2.destroyAllWindows()


stream()
