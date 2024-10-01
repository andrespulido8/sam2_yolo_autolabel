import numpy as np

def get_bounding_box(segmentation):
    rows = np.any(segmentation, axis=1)
    cols = np.any(segmentation, axis=0)
    y_min = np.min(np.where(rows))
    y_max = np.max(np.where(rows))
    x_min = np.min(np.where(cols))
    x_max = np.max(np.where(cols))
    return x_min, y_min, x_max, y_max

def save_bboxes_to_yolo_format(image_width, image_height, bboxes, label_ids, output_file):
    if len(bboxes) != len(label_ids):
        print("Length of bboxes and labels must be equal")
        return

    with open(output_file, 'w') as f:
        for i in range(len(bboxes)):
            x_min, y_min, x_max, y_max = bboxes[i]
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            x_center_norm = x_center / image_width
            y_center_norm = y_center / image_height
            width_norm = (x_max - x_min) / image_width
            height_norm = (y_max - y_min) / image_height

            yolo_format_string = f"{label_ids[i]} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"
            f.write(yolo_format_string + '\n')

def from_yolo_to_bbox(yolo_bbox, image_width, image_height):
    x_center_norm, y_center_norm, width_norm, height_norm = yolo_bbox
    x_center = x_center_norm * image_width
    y_center = y_center_norm * image_height
    width = width_norm * image_width
    height = height_norm * image_height

    x_min = int(x_center - width / 2)
    y_min = int(y_center - height / 2)
    x_max = int(x_center + width / 2)
    y_max = int(y_center + height / 2)

    return x_min, y_min, x_max, y_max

def read_yolo_labels(file_path, image_width, image_height):
    """ Reads all the labels from a yolo file 
        An example of a yolo file is:
        2 0.326042 0.211719 0.052083 0.042188
        2 0.528125 0.243750 0.060417 0.053125
        1 0.545833 0.187500 0.116667 0.050000
        
        The first number is the label id, the next four numbers are the bounding box in yolo format
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    labels = []
    for line in lines:
        label = line.strip().split(' ')
        label_id = int(label[0])
        bbox = from_yolo_to_bbox([float(x) for x in label[1:]], image_width, image_height)
        labels.append((label_id, bbox))
    
    return labels