# specify the path to the log file
import json


log_file = "/Users/hieu.huynh/Documents/Projects/web-segmentation/web-segment/log2023-04-20 01:02:34.021283.txt"

# specify the threshold for the not found rate
not_found_rate_threshold = 0.5

# read the log file and parse the lines
with open(log_file, "r") as f:
    lines = f.readlines()

# create a dictionary to store the found and not found counts for each id
counts = {}
for line in lines:
    # extract the id, found count, and not found count from the line
    # e.g. Success: 000010. Found: 23 not found: 7
    integers = [s for s in line.replace(".", "").split() if s.isdigit()]
    id = integers[0]
    found = int(integers[1])
    not_found = int(integers[2])

    # store the counts in the dictionary
    counts[id] = {"found": found, "not_found": not_found}

# filter the ids that have a not found rate above the threshold
filtered_ids = [id for id, count in counts.items() if count["not_found"] / (count["found"] + count["not_found"]) > not_found_rate_threshold]
with open("random_id.json", "r") as f:
    folder_names = json.load(f)
filtered_ids = [id for id in folder_names if id in filtered_ids]
# print the filtered ids
print(len(filtered_ids))

# write the filtered ids to a file
with open("filtered_error_ids.json", "w") as f:
    json.dump(filtered_ids, f)
