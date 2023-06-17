import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import cv2
import time
from face_detection import FaceDetection
from face_recognition import FaceRecognition
from tqdm import tqdm


def stream(video_path):
    FPS = "loading"
    frame_count = 0
    save_count = 0

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_time = total_frames / frame_rate

    fd = FaceDetection(r'face_mask_detection.pb')
    fr = FaceRecognition(r"Facenet_masked_model.pb", r"unique_person")

    pbar = tqdm(total=total_frames, desc='Processing frames', unit='frame')

    start_time = time.time()
    while(cap.isOpened()):
        ret, img = cap.read()
        if ret is True:
            img_copy = img.copy()

            # Frame rate control
            if frame_count % (int(frame_rate) // 2) == 0:  # Process only 2 frames from every 1 second
                bboxes, re_confidence, re_mask_id = fd.detect(img)

                if len(bboxes) > 0:
                    for i, bbox in enumerate(bboxes):
                        name, embed = fr.recognize(img, bbox)

                        # ----display results
                        confi = round(re_confidence[i], 2)
                        class_id = re_mask_id[i]
                        color = (0, 255, 0) if class_id == 0 else (0, 0, 255)  # BGR
                        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)
                        display_msg = "{},{},{}".format(fd.id2class[class_id], confi, name)
                        result_coor = (bbox[0] + 2, bbox[1] - 2)
                        cv2.putText(img, display_msg, result_coor, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)

                        # ----Save unknown person images
                        if name == "Unknown":
                            save_count += 1
                            img_temp = img_copy[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                            time_seconds = cap.get(cv2.CAP_PROP_POS_MSEC) // 1000
                            save_path = f"unknown_{time_seconds}s_{save_count}.jpg"
                            save_path = os.path.join(r"unique_person", save_path)
                            cv2.imwrite(save_path, img_temp)
                            print("An unknown person image is saved to", save_path)
                            fr.save_embed(embed)

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
            pbar.update(1)

            # ----keys handle
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        else:
            break

    pbar.close()
    end_time = time.time()
    total_processing_time = end_time - start_time

    cap.release()
    cv2.destroyAllWindows()

    print("Total video processing time:", total_processing_time, "seconds")


video_path = "1.mp4"  # Replace with the actual path to your video file
stream(video_path)
