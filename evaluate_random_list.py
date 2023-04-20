import json
import os
import cv2
import numpy as np

# read folder names from json random_id.json
with open("random_id.json", "r") as f:
    folder_names = json.load(f)

dataset_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"

# cikm20-web-page-segmentation-revisited-evaluation-framework-and-dataset %
# Rscript src/main/r/evaluate-segmentation.R
# --algorithm annotations.json
# --algorithm-segmentation my_algorithm
# --ground-truth ground-truth.json
# --size-function pixels
# --output 0.csv

with open("output.csv", "w") as f:
    f.write("id,presicion,recall,f1\n")

for id in folder_names:
    print("Processing: ", id)
    json_file = os.path.join(dataset_path, id, "annotations.json")
    ground_truth_file = os.path.join(dataset_path, id, "ground-truth.json")

    rscript = "Rscript"
    rscript_path = "/Users/hieu.huynh/Documents/Projects/web-segmentation/cikm20-web-page-segmentation-revisited-evaluation-framework-and-dataset/src/main/r/evaluate-segmentation.R"
    algorithm = json_file
    algorithm_segmentation = "my_algorithm"
    ground_truth = ground_truth_file
    size_function = "pixels"
    output = "/Users/hieu.huynh/Documents/Projects/web-segmentation/web-segment/temp.csv"

    cmd = f"{rscript} {rscript_path} \
            --algorithm \"{algorithm}\" \
            --algorithm-segmentation \"{algorithm_segmentation}\" \
            --ground-truth \"{ground_truth}\" \
            --size-function {size_function} \
            --output {output}"
    os.system(cmd)
    with open(output, "r") as f:
        output_csv = f.read()
    #parse output_csv
    output = output_csv.split("\n")[-2]
    output = output.split(",")[1:]

    presicion = output[0]
    recall = output[1]
    f1 = output[2]

    #write to csv
    with open("output.csv", "a") as f:
        f.write(f"{id},{presicion},{recall},{f1}\n")
    
    # input("Press any key to continue...")

#calculate average
with open("output.csv", "r") as f:
    output_csv = f.read()
output = output_csv.split("\n")[1:-1]
presicion = 0
recall = 0
f1 = 0
for line in output:
    line = line.split(",")
    presicion += float(line[1])
    recall += float(line[2])
    f1 += float(line[3])

presicion /= len(output)
recall /= len(output)
f1 /= len(output)

with open("output.csv", "a") as f:
    f.write(f"Average,{presicion},{recall},{f1}\n")