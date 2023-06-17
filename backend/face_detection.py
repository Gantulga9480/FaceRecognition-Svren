import numpy as np
import cv2
import tensorflow
# ----tensorflow version check
if tensorflow.__version__.startswith('1.'):
    import tensorflow as tf
    from tensorflow.python.platform import gfile
else:
    import tensorflow.compat.v1 as tf
    import tensorflow.compat.v1.gfile as gfile
    tf.disable_v2_behavior()


class FaceDetection:

    def __init__(self, path) -> None:
        self.path = path
        self.node_dict = {'input': 'data_1:0',
                          'detection_bboxes': 'loc_branch_concat_1/concat:0',
                          'detection_scores': 'cls_branch_concat_1/concat:0'
                          }
        # ====anchors config
        self.anchors_exp = np.expand_dims(self.generate_anchors(), axis=0)
        self.sess = self.import_model()
        self.tf_input = self.node_dict['input']
        self.model_shape = self.tf_input.shape  # [N,H,W,C]
        self.img_size = (self.tf_input.shape[2].value, self.tf_input.shape[1].value)
        self.detection_bboxes = self.node_dict['detection_bboxes']
        self.detection_scores = self.node_dict['detection_scores']
        self.id2class = {0: 'Mask', 1: 'NoMask'}
        self.margin = 40
        self.conf_thresh = 0.8
        self.iou_thresh = 0.5

    def detect(self, img_raw):
        height, width, _ = img_raw.shape
        img_fd = self.preprocess(img_raw)
        return self.inference(img_fd, height, width)

    def preprocess(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb = img_rgb.astype(np.float32)
        img_rgb /= 255
        img_fd = cv2.resize(img_rgb, self.img_size)
        img_fd = np.expand_dims(img_fd, axis=0)
        return img_fd

    def inference(self, img_4d, height, width):
        ori_height = height
        ori_width = width
        re_boxes = []
        re_confidence = []
        re_class_id = []

        y_bboxes_output, y_cls_output = self.sess.run([self.detection_bboxes, self.detection_scores],
                                                      feed_dict={self.tf_input: img_4d})
        # remove the batch dimension, for batch is always 1 for inference.
        y_bboxes = self.decode_bbox(self.anchors_exp, y_bboxes_output)[0]
        y_cls = y_cls_output[0]
        # To speed up, do single class NMS, not multiple classes NMS.
        bbox_max_scores = np.max(y_cls, axis=1)
        bbox_max_score_classes = np.argmax(y_cls, axis=1)

        # keep_idx is the alive bounding box after nms.
        keep_idxs = self.single_class_non_max_suppression(y_bboxes, bbox_max_scores, conf_thresh=self.conf_thresh, iou_thresh=self.iou_thresh)
        # ====draw bounding box
        for idx in keep_idxs:
            conf = float(bbox_max_scores[idx])
            class_id = bbox_max_score_classes[idx]
            bbox = y_bboxes[idx]
            xmin = np.maximum(0, bbox[0] * ori_width - self.margin / 2)
            ymin = np.maximum(0, bbox[1] * ori_height - self.margin / 2)
            xmax = np.minimum(bbox[2] * ori_width + self.margin / 2, ori_width)
            ymax = np.minimum(bbox[3] * ori_height + self.margin / 2, ori_height)
            re_boxes.append([int(xmin), int(ymin), int(xmax - xmin), int(ymax - ymin)])
            re_confidence.append(conf)
            re_class_id.append(class_id)
        return re_boxes, re_confidence, re_class_id

    def import_model(self):
        with tf.Graph().as_default():
            sess = tf.Session()
            with gfile.FastGFile(self.path, 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                sess.graph.as_default()
                # import the calculation graph
                tf.import_graph_def(graph_def, name='')
            sess.run(tf.global_variables_initializer())
            for key, value in self.node_dict.items():
                node = sess.graph.get_tensor_by_name(value)
                self.node_dict[key] = node
        return sess

    def generate_anchors(self):
        feature_map_sizes = [[33, 33], [17, 17], [9, 9], [5, 5], [3, 3]]
        anchor_sizes = [[0.04, 0.056], [0.08, 0.11],
                        [0.16, 0.22], [0.32, 0.45], [0.64, 0.72]]
        anchor_ratios = [[1, 0.62, 0.42]] * 5
        anchor_bboxes = []
        for idx, feature_size in enumerate(feature_map_sizes):
            cx = (np.linspace(
                0, feature_size[0] - 1, feature_size[0]) + 0.5) / feature_size[0]
            cy = (np.linspace(
                0, feature_size[1] - 1, feature_size[1]) + 0.5) / feature_size[1]
            cx_grid, cy_grid = np.meshgrid(cx, cy)
            cx_grid_expend = np.expand_dims(cx_grid, axis=-1)
            cy_grid_expend = np.expand_dims(cy_grid, axis=-1)
            center = np.concatenate((cx_grid_expend, cy_grid_expend), axis=-1)

            num_anchors = len(anchor_sizes[idx]) + len(anchor_ratios[idx]) - 1
            center_tiled = np.tile(center, (1, 1, 2 * num_anchors))
            anchor_width_heights = []

            # different scales with the first aspect ratio
            for scale in anchor_sizes[idx]:
                ratio = anchor_ratios[idx][0]  # select the first ratio
                width = scale * np.sqrt(ratio)
                height = scale / np.sqrt(ratio)
                anchor_width_heights.extend(
                    [-width / 2.0, -height / 2.0, width / 2.0, height / 2.0])

            # the first scale, with different aspect ratios (except the first one)
            for ratio in anchor_ratios[idx][1:]:
                s1 = anchor_sizes[idx][0]  # select the first scale
                width = s1 * np.sqrt(ratio)
                height = s1 / np.sqrt(ratio)
                anchor_width_heights.extend(
                    [-width / 2.0, -height / 2.0, width / 2.0, height / 2.0])

            bbox_coords = center_tiled + np.array(anchor_width_heights)
            bbox_coords_reshape = bbox_coords.reshape((-1, 4))
            anchor_bboxes.append(bbox_coords_reshape)
        anchor_bboxes = np.concatenate(anchor_bboxes, axis=0)
        return anchor_bboxes

    def decode_bbox(self, anchors, raw_outputs, variances=[0.1, 0.1, 0.2, 0.2]):
        '''
        Decode the actual bbox according to the anchors.
        the anchor value order is:[xmin,ymin, xmax, ymax]
        :param anchors: numpy array with shape [batch, num_anchors, 4]
        :param raw_outputs: numpy array with the same shape with anchors
        :param variances: list of float, default=[0.1, 0.1, 0.2, 0.2]
        :return:
        '''
        anchor_centers_x = (anchors[:, :, 0:1] + anchors[:, :, 2:3]) / 2
        anchor_centers_y = (anchors[:, :, 1:2] + anchors[:, :, 3:]) / 2
        anchors_w = anchors[:, :, 2:3] - anchors[:, :, 0:1]
        anchors_h = anchors[:, :, 3:] - anchors[:, :, 1:2]
        raw_outputs_rescale = raw_outputs * np.array(variances)
        predict_center_x = raw_outputs_rescale[:, :, 0:1] * anchors_w + anchor_centers_x
        predict_center_y = raw_outputs_rescale[:, :, 1:2] * anchors_h + anchor_centers_y
        predict_w = np.exp(raw_outputs_rescale[:, :, 2:3]) * anchors_w
        predict_h = np.exp(raw_outputs_rescale[:, :, 3:]) * anchors_h
        predict_xmin = predict_center_x - predict_w / 2
        predict_ymin = predict_center_y - predict_h / 2
        predict_xmax = predict_center_x + predict_w / 2
        predict_ymax = predict_center_y + predict_h / 2
        predict_bbox = np.concatenate([predict_xmin, predict_ymin, predict_xmax, predict_ymax], axis=-1)
        return predict_bbox

    def single_class_non_max_suppression(self, bboxes, confidences, conf_thresh=0.2, iou_thresh=0.5, keep_top_k=-1):
        '''
        do nms on single class.
        Hint: for the specific class, given the bbox and its confidence,
        1) sort the bbox according to the confidence from top to down, we call this a set
        2) select the bbox with the highest confidence, remove it from set, and do IOU calculate with the rest bbox
        3) remove the bbox whose IOU is higher than the iou_thresh from the set,
        4) loop step 2 and 3, util the set is empty.
        :param bboxes: numpy array of 2D, [num_bboxes, 4]
        :param confidences: numpy array of 1D. [num_bboxes]
        :param conf_thresh:
        :param iou_thresh:
        :param keep_top_k:
        :return:
        '''
        if len(bboxes) == 0:
            return []

        conf_keep_idx = np.where(confidences > conf_thresh)[0]

        bboxes = bboxes[conf_keep_idx]
        confidences = confidences[conf_keep_idx]

        pick = []
        xmin = bboxes[:, 0]
        ymin = bboxes[:, 1]
        xmax = bboxes[:, 2]
        ymax = bboxes[:, 3]

        area = (xmax - xmin + 1e-3) * (ymax - ymin + 1e-3)
        idxs = np.argsort(confidences)

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            # keep top k
            if keep_top_k != -1:
                if len(pick) >= keep_top_k:
                    break

            overlap_xmin = np.maximum(xmin[i], xmin[idxs[:last]])
            overlap_ymin = np.maximum(ymin[i], ymin[idxs[:last]])
            overlap_xmax = np.minimum(xmax[i], xmax[idxs[:last]])
            overlap_ymax = np.minimum(ymax[i], ymax[idxs[:last]])
            overlap_w = np.maximum(0, overlap_xmax - overlap_xmin)
            overlap_h = np.maximum(0, overlap_ymax - overlap_ymin)
            overlap_area = overlap_w * overlap_h
            overlap_ratio = overlap_area / (area[idxs[:last]] + area[i] - overlap_area)

            need_to_be_deleted_idx = np.concatenate(([last], np.where(overlap_ratio > iou_thresh)[0]))
            idxs = np.delete(idxs, need_to_be_deleted_idx)

        # if the number of final bboxes is less than keep_top_k, we need to pad it.
        # TODO
        return conf_keep_idx[pick]
