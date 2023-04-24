# import json
# import os
# import cv2
# import numpy as np

# #get the list of all folder in the dataset
# dataset_path = "/content/drive/MyDrive/dataset-websis/webis-webseg-20"
# folder_names = os.listdir(dataset_path)

# count = 0
# folder_names = sorted(folder_names)

# #randomly select 10% of the dataset
# random_index = np.random.choice(len(folder_names), int(len(folder_names)*0.1), replace=False)
# random_index.sort()

# filter_folder_names = [folder_names[i] for i in random_index]

# #inside each folder, there is a screenshot.png and a screenshot_with_bbox.png
# #zip these file into a zip file

# screenshot_files = [os.path.join(dataset_path, folder_name, "screenshot.png") for folder_name in filter_folder_names]
# screenshot_with_bbox_files = [os.path.join(dataset_path, folder_name, "screenshot_with_bbox.png") for folder_name in filter_folder_names]

# #zip the files
# for i in range(len(screenshot_files)):
#     screenshot_file = screenshot_files[i]
#     screenshot_with_bbox_file = screenshot_with_bbox_files[i]
#     folder_name = filter_folder_names[i]
#     zip_file = os.path.join(dataset_path, folder_name + ".zip")
#     command = "zip " + zip_file + " " + screenshot_file + " " + screenshot_with_bbox_file
#     os.system(command)

# def bbox_coverage_ratio(bbox1, bbox2):
#     # the bbox is a list of 4 values, the first is the x, the second is the y, the third is the width and the fourth is the height
#     if 'x' not in bbox1 or 'y' not in bbox1 or 'width' not in bbox1 or 'height' not in bbox1:
#         return 0
#     if 'x' not in bbox2 or 'y' not in bbox2 or 'width' not in bbox2 or 'height' not in bbox2:
#         return 0
#     x1, y1, w1, h1 = bbox1['x'], bbox1['y'], bbox1['width'], bbox1['height']
#     x2, y2, w2, h2 = bbox2['x'], bbox2['y'], bbox2['width'], bbox2['height']
#     x = min(x1, x2)
#     y = min(y1, y2)
#     w = max(x1+w1, x2+w2) - x
#     h = max(y1+h1, y2+h2) - y

#     return (w*h)/(w1*h1)

def bbox_coverage_ratio(bbox1, bbox2):
    """
    Calculates the coverage of bbox1 over bbox2, in percentage.
    """
    x1 = bbox1['x']
    y1 = bbox1['y']
    w1 = bbox1['width']
    h1 = bbox1['height']

    x2 = bbox2['x']
    y2 = bbox2['y']
    w2 = bbox2['width']
    h2 = bbox2['height']

    # Calculate intersection area
    dx = min(x1 + w1, x2 + w2) - max(x1, x2)
    dy = min(y1 + h1, y2 + h2) - max(y1, y2)
    if dx < 0 or dy < 0:
        intersection_area = 0
    else:
        intersection_area = dx * dy

    # Calculate bbox1 area
    bbox1_area = w1 * h1

    # Calculate coverage percentage
    coverage = intersection_area / bbox1_area * 100

    return coverage


#test the bbox_coverage_ratio function
bbox1 = {'x': 10, 'y': 20, 'width': 30, 'height': 40}
bbox2 = {'x': 20, 'y': 30, 'width': 40, 'height': 50}
print(bbox_coverage_ratio(bbox1, bbox2))  # output: 55.55555555555556
# print(bbox_coverage_ratio(bbox1, bbox2))