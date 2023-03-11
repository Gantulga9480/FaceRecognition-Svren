import cv2
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import time
import math
import numpy as np
from face_alignment import FaceMaskDetection
import tensorflow
# ----tensorflow version check
if tensorflow.__version__.startswith('1.'):
    import tensorflow as tf
    from tensorflow.python.platform import gfile
else:
    import tensorflow.compat.v1 as tf
    import tensorflow.compat.v1.gfile as gfile
    tf.disable_v2_behavior()

print("Tensorflow version: ", tf.__version__)

img_format = {'png', 'PNG', 'jpg', 'JPG', 'JPEG', 'bmp', 'BMP'}


def model_restore_from_pb(pb_path, node_dict, GPU_ratio=None):
    tf_dict = dict()
    with tf.Graph().as_default():
        sess = tf.Session()
        with gfile.FastGFile(pb_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            sess.graph.as_default()
            for node in graph_def.node:
                if node.op == 'RefSwitch':
                    node.op = 'Switch'
                    for index in range(len(node.input)):
                        if 'moving_' in node.input[index]:
                            node.input[index] = node.input[index] + '/read'
                elif node.op == 'AssignSub':
                    node.op = 'Sub'
                    if 'use_locking' in node.attr:
                        del node.attr['use_locking']

            tf.import_graph_def(graph_def, name='')

        sess.run(tf.global_variables_initializer())
        for key, value in node_dict.items():
            try:
                node = sess.graph.get_tensor_by_name(value)
                tf_dict[key] = node
            except Exception:
                print("node:{} does not exist in the graph".format(key))
        return sess, tf_dict


def video_init(camera_source=0, resolution="480"):
    resolution_dict = {"480": [480, 640],
                       "720": [720, 1280], "1080": [1080, 1920]}

    # ----camera source connection
    cap = cv2.VideoCapture(camera_source)

    # ----resolution
    if resolution_dict.get(resolution) is not None:
        width = resolution_dict[resolution][1]
        height = resolution_dict[resolution][0]
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    else:
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # default 480
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # default 640
        print("video size is auto set")

    return cap, height, width


def stream(pb_path, node_dict, ref_dir, camera_source=0, resolution="480", to_write=False, save_dir=None):
    frame_count = 0
    FPS = "loading"
    face_mask_model_path = r'face_mask_detection.pb'
    margin = 40
    id2class = {0: 'Mask', 1: 'NoMask'}
    batch_size = 32
    threshold = 0.8
    display_mode = 0
    label_type = 0

    # ----Video streaming initialization
    cap, height, width = video_init(camera_source=camera_source, resolution=resolution)

    # ----face detection init
    fmd = FaceMaskDetection(face_mask_model_path, margin, GPU_ratio=None)

    # ----face recognition init
    sess, tf_dict = model_restore_from_pb(pb_path, node_dict, GPU_ratio=None)
    tf_input = tf_dict['input']
    tf_embeddings = tf_dict['embeddings']

    # ----get the model shape
    if tf_input.shape[1].value is None:
        model_shape = (None, 160, 160, 3)
    else:
        model_shape = (None, tf_input.shape[1].value, tf_input.shape[2].value, 3)
    print("The mode shape of face recognition:", model_shape)
    # ----set the feed_dict
    feed_dict = {}
    if 'keep_prob' in tf_dict.keys():
        feed_dict[tf_dict['keep_prob']] = 1.0
    if 'phase_train' in tf_dict.keys():
        feed_dict[tf_dict['phase_train']] = False

    # ----read images from the database
    d_t = time.time()
    paths = list()
    for dirname, subdirname, filenames in os.walk(ref_dir):
        if len(filenames) > 0:
            for filename in filenames:
                if filename.split(".")[-1] in img_format:
                    file_path = os.path.join(dirname, filename)
                    paths.append(file_path)
    len_ref_path = len(paths)
    if len_ref_path == 0:
        print("No images in ", ref_dir)
    else:
        ites = math.ceil(len_ref_path / batch_size)
        embeddings_ref = np.zeros([len_ref_path, tf_embeddings.shape[-1]], dtype=np.float32)

        for i in range(ites):
            num_start = i * batch_size
            num_end = np.minimum(num_start + batch_size, len_ref_path)

            batch_data_dim = [num_end - num_start]
            batch_data_dim.extend(model_shape[1:])
            batch_data = np.zeros(batch_data_dim, dtype=np.float32)

            for idx, path in enumerate(paths[num_start:num_end]):
                # img = cv2.imread(path)
                img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
                if img is None:
                    print("read failed:", path)
                else:
                    # print("model_shape:",model_shape[1:3])
                    img = cv2.resize(img, (model_shape[2], model_shape[1]))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # change the color format
                    batch_data[idx] = img
            batch_data /= 255
            feed_dict[tf_input] = batch_data

            embeddings_ref[num_start:num_end] = sess.run(tf_embeddings, feed_dict=feed_dict)

        d_t = time.time() - d_t
        print("ref embedding shape", embeddings_ref.shape)
        print("It takes {} secs to get {} embeddings".format(d_t, len_ref_path))
    # ----tf setting for calculating distance
    if len_ref_path > 0:
        with tf.Graph().as_default():
            tf_tar = tf.placeholder(dtype=tf.float32, shape=tf_embeddings.shape[-1])
            tf_ref = tf.placeholder(dtype=tf.float32, shape=tf_embeddings.shape)
            tf_dis = tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(tf_ref, tf_tar)), axis=1))
            sess_cal = tf.Session()
            sess_cal.run(tf.global_variables_initializer())
        feed_dict_2 = {tf_ref: embeddings_ref}
    # ----Get an image
    while(cap.isOpened()):
        # img is the original image with BGR format. It's used to be shown by opencv
        ret, img = cap.read()

        if ret is True:
            img_copy = img.copy()
            # ----image processing
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_rgb = img_rgb.astype(np.float32)
            img_rgb /= 255

            # ----face detection
            img_fd = cv2.resize(img_rgb, fmd.img_size)
            img_fd = np.expand_dims(img_fd, axis=0)

            bboxes, re_confidence, _, re_mask_id = fmd.inference(img_fd, height, width)
            if len(bboxes) > 0:
                for i, bbox in enumerate(bboxes):
                    confi = round(re_confidence[i], 2)
                    class_id = re_mask_id[i]
                    if class_id == 0:
                        color = (0, 255, 0)  # (B,G,R) --> Green(with masks)
                    else:
                        color = (0, 0, 255)  # (B,G,R) --> Red(without masks)
                    cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)
                    # ----face recognition
                    name = "unknown"
                    if len_ref_path > 0:
                        img_fr = img_rgb[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]  # crop
                        img_fr = cv2.resize(img_fr, (model_shape[2], model_shape[1]))  # resize
                        img_fr = np.expand_dims(img_fr, axis=0)  # make 4 dimensions
                        feed_dict[tf_input] = img_fr
                        embeddings_tar = sess.run(tf_embeddings, feed_dict=feed_dict)
                        feed_dict_2[tf_tar] = embeddings_tar[0]
                        distance = sess_cal.run(tf_dis, feed_dict=feed_dict_2)
                        # index of the smallest distance
                        arg = np.argmin(distance)

                        if distance[arg] < threshold:
                            # ----label type
                            if label_type == 1:
                                name = paths[arg].split("\\")[-2]
                            else:
                                name = paths[arg].split("\\")[-1].split(".")[0]
                            name = name.split("_")[0]
                            dis = round(distance[arg], 2)
                            dis = "_" + str(dis)
                            name += dis
                    # ----display results
                    if display_mode == 1:  # no score and lowest distance in lower position
                        display_msg = "{},{}".format(id2class[class_id], name)
                        result_coor = (bbox[0], bbox[1] + bbox[3] + 20)
                    elif display_mode == 2:  # with score and lowest distance in upper position
                        display_msg = "{}_{},{}".format(
                            id2class[class_id], confi, name)
                        result_coor = (bbox[0] + 2, bbox[1] - 2)
                    elif display_mode == 3:  # with score and lowest distance in lower position
                        display_msg = "{}_{},{}".format(
                            id2class[class_id], confi, name)
                        result_coor = (bbox[0], bbox[1] + bbox[3] + 20)
                    else:  # no score and lowest distance in upper position
                        display_msg = "{},{}".format(id2class[class_id], name)
                        result_coor = (bbox[0] + 2, bbox[1] - 2)

                    cv2.putText(img, display_msg, result_coor, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)

            # ----FPS calculation
            if frame_count == 0:
                t_start = time.time()
            frame_count += 1
            if frame_count >= 10:
                FPS = "FPS=%1f" % (10 / (time.time() - t_start))
                frame_count = 0

            # cv2.putText(img, text, coor, font, size, color, line thickness, line type)
            cv2.putText(img, FPS, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # ----image display
            cv2.imshow("Face recognition", img)

            # ----keys handle
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                if len(bboxes) > 0:
                    img_temp = img_copy[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]
                    save_path = "img_crop.jpg"
                    save_path = os.path.join(ref_dir, save_path)
                    cv2.imwrite(save_path, img_temp)
                    print("An image is saved to ", save_path)
            elif key == ord('d'):
                display_mode += 1
                if display_mode > 3:
                    display_mode = 0
            elif key == ord('l'):
                label_type += 1
                if label_type > 1:
                    label_type = 0

        else:
            print("get images failed")
            break

    # ----release
    print("Error:get image source failed")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    camera_source = 0  # usb camera or laptop camera ip hayag ntr bsan ch bolno

    # pb_path: pb file path
    pb_path = r"Facenet_masked_model.pb"

    node_dict = {'input': 'input:0',
                 'keep_prob': 'keep_prob:0',
                 'phase_train': 'phase_train:0',
                 'embeddings': 'embeddings:0',
                 }
    # Training images folder
    ref_dir = r"known_faces"

    stream(pb_path, node_dict, ref_dir, camera_source=camera_source,
           resolution="480", to_write=False, save_dir=None)
