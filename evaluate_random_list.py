import json
import os
import threading
import time
import cv2
import numpy as np

def evaluate_file_id(id, dataset_path, evaluation_file):
    # cikm20-web-page-segmentation-revisited-evaluation-framework-and-dataset %
    # Rscript src/main/r/evaluate-segmentation.R
    # --algorithm annotations.json
    # --algorithm-segmentation my_algorithm
    # --ground-truth ground-truth.json
    # --size-function pixels
    # --output 0.csv

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
    with open(evaluation_file, "a") as f:
        f.write(f"{id},{presicion},{recall},{f1}\n")

def main():

# read folder names from json random_id.json
    with open("random_id.json", "r") as f:
        folder_names = json.load(f)

    dataset_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"

    evaluation_file = f"evaluation_{time.time()}.csv"
    with open(evaluation_file, "w") as f:
        f.write("id,presicion,recall,f1\n")

    threads = []
    batch_size = 10
    for i in range(0, len(folder_names), batch_size):
        batch = folder_names[i:i+batch_size]
        for folder_name in batch:
            t = threading.Thread(target=evaluate_file_id, args=(folder_name, dataset_path, evaluation_file))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        threads = []
        # input("Done " + str(i) + "/" + str(len(folder_names)) + ". Press enter to continue")
        print("Done " + str(i) + "/" + str(len(folder_names)))

    #calculate average
    with open(evaluation_file, "r") as f:
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

    with open(evaluation_file, "a") as f:
        f.write(f"Average,{presicion},{recall},{f1}\n")

if __name__ == "__main__":
    main()