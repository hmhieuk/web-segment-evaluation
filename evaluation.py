# read json 000000/ground-truth.json

import csv
import datetime
import json
import os
import threading

import cv2

# from DOMParser import DOMParser
from segment import Segment


class Annotations:
    def __init__(self, id, height, width, segmentations, algorithm):
        self.id = id
        self.height = height
        self.width = width
        self.segmentations = segmentations
        self.algorithm = algorithm

    def append_segmentation(self, segmentation):
        self.segmentations.append([[segmentation]])

    def to_dict(self):
        segmentations = {}
        segmentations[self.algorithm] = self.segmentations

        return {
            "id": self.id,
            "height": self.height,
            "width": self.width,
            "segmentations": segmentations
        }

    def to_json(self):
        return json.dumps(self.to_dict())


def get_width_height_from_image(image_path):
    img = cv2.imread(image_path)
    return img.shape[1], img.shape[0]

def get_width_height_from_ground_truth(ground_truth_file):
    with open(ground_truth_file, "r") as f:
        ground_truth = json.load(f)
        return ground_truth["width"], ground_truth["height"]
    
    

def segment_dom(id, domfile, output_file, log_file, nodes_file, screenshot_file, base_dir, ground_truth_file, nodes_text_file):
    width, height = get_width_height_from_ground_truth(ground_truth_file)
    # domfile = "file://" + domfile
    coordinates = nodes_file_to_json(nodes_file, nodes_text_file)

    spliter = Segment(domfile)
    found, not_found = spliter.segment(
        url=domfile, output_folder=os.path.join(base_dir, id), nodes_dict= coordinates)
    annotations = Annotations(
        id, height, width, [], "my_algorithm")
    filtered_segments = []
    sum_area = 0
    # sort spliter.json_data["segments"] by level
    spliter.json_data["segments"].sort(key=lambda x: x["level"])
    for segment in spliter.json_data["segments"]:
        isNotChild = True
        for filtered_segment in filtered_segments:
            if segment["xpath"].startswith(filtered_segment["xpath"]):
                isNotChild = False
                break

        if not isNotChild:
            continue
        bb1 = segment["bounding_box"]
        cor1 = (bb1['x'], bb1['y'], bb1['x'] +
                bb1['width'], bb1['y'] + bb1['height'])

        cor1 = (int(max(0, cor1[0])), int(max(0, cor1[1])), int(
            min(width, cor1[2])), int(min(height, cor1[3])))

        area = (cor1[2] - cor1[0]) * (cor1[3] - cor1[1])
        sum_area += area
        ratio = area / (height * width)
        if ratio > 0.5:
            continue
        filtered_segments.append(segment)

        segmentation = []
        segmentation.append([cor1[0], cor1[1]])
        segmentation.append([cor1[2], cor1[1]])
        segmentation.append([cor1[2], cor1[3]])
        segmentation.append([cor1[0], cor1[3]])
        segmentation.append([cor1[0], cor1[1]])

        annotations.append_segmentation(segmentation)
    print("found: " + str(found))
    print("not found: " + str(not_found))
    with open(output_file, "w") as f:
        f.write(annotations.to_json())
    return found, not_found


def nodes_file_to_json(nodes_file, nodes_text_file):
    coordinates = {}
    with open(nodes_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            xpath = row['xpath']
            left = int(row['left'])
            bottom = int(row['bottom'])
            right = int(row['right'])
            top = int(row['top'])
            coordinates[xpath] = [{'x': left, 'y': top,
                                  'width': right - left, 'height': bottom - top}, ""]
    with open(nodes_text_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            xpath = row['xpath']
            text = row['text']
            if xpath in coordinates:
                coordinates[xpath][1]=text
            else:
                coordinates[xpath] = []
                coordinates[xpath].append({})
                coordinates[xpath].append(text)
    return coordinates


def normalize_xpath(xpath):
    # input(xpath)
    tags = xpath.split("/")[1:]
    for i, tag in enumerate(tags):
        if "[" in tag:
            tag_name, index = tag.split("[")
            tags[i] = tag_name.upper() + "[" + index
        else:
            tags[i] = tag.upper() + "[1]"
    result = "/" + "/".join(tags)
    #return result to upper case
    return result.upper()
    
def segment_file(dataset_path, ground_truth_path, folder_name, log_file):
    try:
        domfile = os.path.join(dataset_path, folder_name, "dom.html")
        output_file = os.path.join(
            dataset_path, folder_name, "annotations.json")
        # log_file = os.path.join(dataset_path, folder_name, "log.txt")
        nodes_file = os.path.join(dataset_path, folder_name, "nodes.csv")
        nodes_text_file = os.path.join(dataset_path, folder_name, "nodes-texts.csv")
        screenshot_file = os.path.join(
            dataset_path, folder_name, "screenshot.png")
        
        ground_truth_file = os.path.join(
            ground_truth_path, folder_name, "ground-truth.json")
        found, notfound = segment_dom(folder_name, domfile, output_file, log_file, nodes_file, screenshot_file, dataset_path, ground_truth_file, nodes_text_file)
        #write log file
        with open(log_file, "a") as f:
            f.write("Success: " + folder_name + ". Found: " + str(found) + " not found: " + str(notfound))
            f.write("\n")
    except Exception as e:
        print(e)
        with open(log_file, "a") as f:
            f.write("Failed to segment " + folder_name + " with error: " + str(e))
            f.write("\n")

def main():
    dataset_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"
    ground_truth_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"

    log_file = "log" + str(datetime.datetime.now()) + ".txt"

    folder_names = os.listdir(dataset_path)
    # with open("random_id.json", "r") as f:
    #     folder_names = json.load(f)
    #     folder_names.sort()
    # ignore .DS_Store,
    folder_names = [
        folder_name for folder_name in folder_names if folder_name[0] != "."]
    
    threads = []
    batch_size = 20
    for i in range(0, len(folder_names), batch_size):
        batch = folder_names[i:i+batch_size]
        for folder_name in batch:
            t = threading.Thread(target=segment_file, args=(dataset_path, ground_truth_path, folder_name, log_file))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        threads = []
        # input("Done " + str(i) + "/" + str(len(folder_names)) + ". Press enter to continue")
        print("Done " + str(i) + "/" + str(len(folder_names)))

if __name__ == "__main__":
    main()
