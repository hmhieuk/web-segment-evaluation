# specify the path to the log file
import json


log_file = "log2023-04-24 10:07:12.822462.txt"

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
    try:
        found = int(integers[1])
        not_found = int(integers[2])
    except:
        continue

    # store the counts in the dictionary
    counts[id] = {"found": found, "not_found": not_found}

# filter the ids that have a not found rate above the threshold
filtered_ids = list(counts.keys())

# write the filtered ids to a file
with open("filtered_success_ids.json", "w") as f:
    json.dump(filtered_ids, f)
