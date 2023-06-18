import os
import cv2
import math
import numpy as np
import tensorflow  # noqa
# ----tensorflow version check
if tensorflow.__version__.startswith('1.'):
    import tensorflow as tf
    from tensorflow.python.platform import gfile
else:
    import tensorflow.compat.v1 as tf
    import tensorflow.compat.v1.gfile as gfile
    tf.disable_v2_behavior()


IMG_FORMAT = {'png', 'PNG', 'jpg', 'JPG', 'JPEG'}
BATCH_SIZE = 32
THRESHOLD = 0.8


class FaceRecognition:

    def __init__(self, path) -> None:
        self.path = path
        self.node_dict = {'input': 'input:0',
                          'keep_prob': 'keep_prob:0',
                          'phase_train': 'phase_train:0',
                          'embeddings': 'embeddings:0'}
        self.id2class = {0: 'Mask', 1: 'NoMask'}
        self.tf_dict = {}
        self.embedding_sess = self.import_model()
        self.tf_input = self.tf_dict['input']
        self.tf_embeddings = self.tf_dict['embeddings']
        self.model_shape = (None, self.tf_input.shape[1].value, self.tf_input.shape[2].value, 3)
        self.embedding_feed_dict = {}
        if 'keep_prob' in self.tf_dict.keys():
            self.embedding_feed_dict[self.tf_dict['keep_prob']] = 1.0
        if 'phase_train' in self.tf_dict.keys():
            self.embedding_feed_dict[self.tf_dict['phase_train']] = False
        self.ref_paths = []
        self.dist_feed_dict = None

    def inference(self, img_fr):
        if self.dist_feed_dict is not None:
            self.embedding_feed_dict[self.tf_input] = img_fr
            embeddings_tar = self.embedding_sess.run(self.tf_embeddings, feed_dict=self.embedding_feed_dict)
            self.dist_feed_dict[self.tf_tar] = embeddings_tar[0]
            distance = self.dist_sess.run(self.tf_dist_embedding, feed_dict=self.dist_feed_dict)
            arg = np.argmin(distance)
            name = "Unknown"
            if distance[arg] < THRESHOLD:
                r, f = os.path.split(self.ref_paths[arg])
                name = f.split('.')[0]
            return name, embeddings_tar[0]
        else:
            return "Unknown", None

    def recognize(self, img_raw, bbox):
        img_fr = self.preprocess(img_raw, bbox)
        return self.inference(img_fr)

    def preprocess(self, img, bbox):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb = img_rgb.astype(np.float32)
        img_rgb /= 255
        img_fr = img_rgb[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2], :]  # crop
        img_fr = cv2.resize(img_fr, (self.model_shape[2], self.model_shape[1]))    # resize
        img_fr = np.expand_dims(img_fr, axis=0)  # make 4 dimensions
        return img_fr

    def add_embed(self, embed, ref_dir):
        self.ref_paths.clear()
        for r, ds, fs in os.walk(ref_dir):
            for f in fs:
                if f.split(".")[-1] in IMG_FORMAT:
                    self.ref_paths.append(os.path.join(r, f))
        if len(self.ref_paths) == 0:
            self.dist_feed_dict = None
            print("No reference image for face recognition")
            return
        if self.dist_feed_dict is None:
            self.load_embed(ref_dir)
        else:
            embeddings_ref = np.zeros([len(self.ref_paths), self.tf_embeddings.shape[-1]], dtype=np.float32)
            embeddings_ref[:len(self.ref_paths) - 1] = self.dist_feed_dict[self.tf_ref]
            embeddings_ref[len(self.ref_paths) - 1] = embed
            with tf.Graph().as_default():
                self.tf_tar = tf.placeholder(dtype=tf.float32, shape=self.tf_embeddings.shape[-1])
                self.tf_ref = tf.placeholder(dtype=tf.float32, shape=self.tf_embeddings.shape)
                self.tf_dist_embedding = tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(self.tf_ref, self.tf_tar)), axis=1))
                self.dist_sess = tf.Session()
                self.dist_sess.run(tf.global_variables_initializer())
            self.dist_feed_dict = {self.tf_ref: embeddings_ref}

    def load_embed(self, ref_dir):
        self.ref_paths.clear()
        for r, ds, fs in os.walk(ref_dir):
            for f in fs:
                if f.split(".")[-1] in IMG_FORMAT:
                    self.ref_paths.append(os.path.join(r, f))
        if len(self.ref_paths) == 0:
            self.dist_feed_dict = None
            print("No reference image for face recognition")
            return

        ites = math.ceil(len(self.ref_paths) / BATCH_SIZE)
        embeddings_ref = np.zeros([len(self.ref_paths), self.tf_embeddings.shape[-1]], dtype=np.float32)

        for i in range(ites):
            num_start = i * BATCH_SIZE
            num_end = np.minimum(num_start + BATCH_SIZE, len(self.ref_paths))

            batch_data_dim = [num_end - num_start]
            batch_data_dim.extend(self.model_shape[1:])
            batch_data = np.zeros(batch_data_dim, dtype=np.float32)

            for idx, path in enumerate(self.ref_paths[num_start:num_end]):
                img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
                if img is None:
                    print("read failed:", path)
                else:
                    # print("model_shape:",model_shape[1:3])
                    img = cv2.resize(img, (self.model_shape[2], self.model_shape[1]))
                    img = img[:, :, ::-1]  # change the color format
                    batch_data[idx] = img
            batch_data /= 255
            self.embedding_feed_dict[self.tf_input] = batch_data

            embeddings_ref[num_start:num_end] = self.embedding_sess.run(self.tf_embeddings, feed_dict=self.embedding_feed_dict)

        with tf.Graph().as_default():
            self.tf_tar = tf.placeholder(dtype=tf.float32, shape=self.tf_embeddings.shape[-1])
            self.tf_ref = tf.placeholder(dtype=tf.float32, shape=self.tf_embeddings.shape)
            self.tf_dist_embedding = tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(self.tf_ref, self.tf_tar)), axis=1))
            self.dist_sess = tf.Session()
            self.dist_sess.run(tf.global_variables_initializer())
        self.dist_feed_dict = {self.tf_ref: embeddings_ref}

    def import_model(self):
        with tf.Graph().as_default():
            sess = tf.Session()
            with gfile.FastGFile(self.path, 'rb') as f:
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
            for key, value in self.node_dict.items():
                try:
                    node = sess.graph.get_tensor_by_name(value)
                    self.tf_dict[key] = node
                except Exception:
                    print("node:{} does not exist in the graph".format(key))
            return sess
