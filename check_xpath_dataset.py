import csv
import json
import os
from bs4 import BeautifulSoup
from lxml import etree
def nodes_file_to_json(nodes_file):
    with open(nodes_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        coordinates = {}
        for row in reader:
            xpath = row['xpath']
            left = int(row['left'])
            bottom = int(row['bottom'])
            right = int(row['right'])
            top = int(row['top'])
            coordinates[xpath] = {'x': left, 'y': top,
                                  'width': right - left, 'height': bottom - top}
        return coordinates

ids_json = "/Users/hieu.huynh/Documents/Projects/web-segmentation/web-segment/random_id.json"
with open(ids_json, "r") as f:
    ids = json.load(f)

for id in ids:
    print("ID: " + id)
    dataset_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"
        
    html_file_name = os.path.join(dataset_path, id, "dom.html")
    nodes_file = os.path.join(dataset_path, id, "nodes.csv")
    with open(html_file_name, 'r', encoding="utf-8", errors="ignore") as f:
        html_file = f.read()

    nodes_dict = nodes_file_to_json(nodes_file)
    try:
        # soup = BeautifulSoup(html_file, 'html.parser')
        htmlparser = etree.HTMLParser()
        tree = etree.fromstring(html_file, htmlparser)
        count_not_found = 0
        count_found = 0
        for key in nodes_dict:
            if "()" not in key:
                # print(key.lower())
                # print(tree.xpath(key.lower()))
                if len(tree.xpath(key.lower())) == 0:
                    count_not_found += 1
                else:
                    count_found += 1
        print("Found: " + str(count_found))
        print("Not found: " + str(count_not_found))
    except Exception as e:
        print(e)
        print("Failed to parse " + id)
