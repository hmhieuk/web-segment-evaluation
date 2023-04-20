import json
import os
import cv2
import numpy as np

#get the list of all folder in the dataset
dataset_path = "/content/drive/MyDrive/dataset-websis/webis-webseg-20"
folder_names = os.listdir(dataset_path)

count = 0
folder_names = sorted(folder_names)

#randomly select 10% of the dataset
random_index = np.random.choice(len(folder_names), int(len(folder_names)*0.1), replace=False)
random_index.sort()

filter_folder_names = [folder_names[i] for i in random_index]

#inside each folder, there is a screenshot.png and a screenshot_with_bbox.png
#zip these file into a zip file

screenshot_files = [os.path.join(dataset_path, folder_name, "screenshot.png") for folder_name in filter_folder_names]
screenshot_with_bbox_files = [os.path.join(dataset_path, folder_name, "screenshot_with_bbox.png") for folder_name in filter_folder_names]

#zip the files
for i in range(len(screenshot_files)):
    screenshot_file = screenshot_files[i]
    screenshot_with_bbox_file = screenshot_with_bbox_files[i]
    folder_name = filter_folder_names[i]
    zip_file = os.path.join(dataset_path, folder_name + ".zip")
    command = "zip " + zip_file + " " + screenshot_file + " " + screenshot_with_bbox_file
    os.system(command)