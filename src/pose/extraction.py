#
# extraction.py
# dabnet
# Pose Feature Extraction
#

import tensorflow as tf
import posenet

## Constants
POSENET_MODEL_DIR = "models/posenet"
POSENET_SCALE_FACTOR = 1.0
POSENET_MODEL_ID = 101

# Lazy loads posenet model
# Returns model_cfg, model_outputs for loaded model and session in which model is loaded
_posenet_model = None # lazy load cached model
_session = None
def load_model():
    global _posenet_model, _session

    if not _posenet_model:
        # Create new session and load model into graph of new session
        _session = tf.Session()
        _posenet_model = posenet.load_model(POSENET_MODEL_ID, _session,
                                  model_dir=POSENET_MODEL_DIR)

    model_cfg, model_outputs = _posenet_model
    return model_cfg, model_outputs, _session


# Extract human pose features for the image at the given path
# Returns human pose features pose_scores, keypoint_scores, keypoint_scores 
def extract_pose(img_path):
    model_cfg, model_outputs, sess = load_model()
    output_stride = model_cfg['output_stride']

    # read and preproess image 
    input_image, draw_image, output_scale = posenet.read_imgfile(
        img_path, scale_factor=POSENET_SCALE_FACTOR, output_stride=output_stride)

    # evaluate image using posenet model
    heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
        model_outputs,
        feed_dict={'image:0': input_image}
        )
    
    # extract pose features from model outputs
    pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multiple_poses(
        heatmaps_result.squeeze(axis=0),
        offsets_result.squeeze(axis=0),
        displacement_fwd_result.squeeze(axis=0),
        displacement_bwd_result.squeeze(axis=0),
        output_stride=output_stride,
        max_pose_detections=10,
        min_pose_score=0.25)


    return pose_scores, keypoint_scores, keypoint_coords


if __name__ == "__main__":
    pose_scores, keypoint_scores, keypoint_coords = extract_pose("images/frisbee.jpg")
    print("extracted features:")
    print("pose_scores:", pose_scores.shape)
    print("keypoint_scores:", keypoint_scores.shape)
    print("keypoint_coords:", keypoint_coords.shape)
