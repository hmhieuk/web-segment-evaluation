import json
import os
import cv2
import numpy as np

#read folder names from json random_id.json
with open("random_id.json", "r") as f:
    folder_names = json.load(f)

dataset_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"

count = 0
folder_names = sorted(folder_names)
for folder_name in folder_names:
    print("Processing: ", folder_name)
    json_file = os.path.join(dataset_path, folder_name, "annotations.json")
    screenshot_file = os.path.join(dataset_path, folder_name, "screenshot.png")
    outfile = os.path.join(dataset_path, folder_name, "screenshot_with_my_bbox.png")
    #check if 2 files exist
    if not os.path.exists(json_file) or not os.path.exists(screenshot_file):
        print(f"{folder_name} does not exist")
        # continue

    with open(json_file, "r") as f:
        json_data = json.load(f)

    segments = json_data["segmentations"]["my_algorithm"]
    # each segment is a list of vertices, each vertex is a list of 2 numbers. The first vertex is the same as the last vertex
    # draw the segment on the image
    image = cv2.imread(screenshot_file)
    print("Number of segments: ", len(segments))
    count = 0
    for listSeg in segments:
        for segment in listSeg:
            for s in segment:
                count += 1
                print(count)
                for i in range(len(s) - 1):
                    cv2.line(image, (s[i][0], s[i][1]), (s[i+1][0], s[i+1][1]), (0, 0, 255), 2)

    cv2.imwrite(outfile, image)
    # input("Write to file: " + outfile + ". Press any key to continue...")