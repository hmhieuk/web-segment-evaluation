import json
import os
import threading
import cv2
import numpy as np

from PIL import Image, ImageDraw

def collage2images(img1, img2, name):
    # Define the width of the black line
    line_width = 10

    width = img1.width + img2.width + line_width
    height = max(img1.height, img2.height)

    new_img = Image.new('RGB', (width, height))

    new_img.paste(img1, (0, 0))

    new_img.paste(img2, (img1.width + line_width, 0))
    draw = ImageDraw.Draw(new_img)
    draw.rectangle((img1.width, 0, img1.width +
                   line_width, height), fill='black')
    try:
        new_img.save(name)
    except:
        print('Error saving image: ' + name)

def draw_image_id(folder_name, dataset_path):
    print("Processing: ", folder_name)
    json_file = os.path.join(dataset_path, folder_name, "annotations.json")
    screenshot_file = os.path.join(dataset_path, folder_name, "screenshot.png")
    outfile = os.path.join(dataset_path, folder_name, "screenshot_with_my_bbox.png")
    out_folder = "/Users/hieu.huynh/Documents/Projects/web-segmentation/web-segment/segmentation-results"
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
                #crop image in the segment
                x, y, w, h = cv2.boundingRect(np.array(s))
                crop_img = image[y:y+h, x:x+w]
                save_path = os.path.join(out_folder, folder_name, "segment_images")
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                cv2.imwrite(os.path.join(save_path, f"segment_{count}.png"), crop_img)


    cv2.imwrite(outfile, image)

    combined_file = os.path.join(out_folder, f"combined_{folder_name}.png")
    collage2images(Image.open(os.path.join(dataset_path, folder_name,"screenshot_with_bbox.png")), Image.open(outfile), combined_file)

def main():

#read folder names from json random_id.json
    with open("random_id.json", "r") as f:
        folder_names = json.load(f)

    dataset_path = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"

    folder_names = sorted(folder_names)

    threads = []
    batch_size = 10
    for i in range(0, len(folder_names), batch_size):
        batch = folder_names[i:i+batch_size]
        for folder_name in batch:
            t = threading.Thread(target=draw_image_id, args=(folder_name, dataset_path))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        threads = []
        # input("Done " + str(i) + "/" + str(len(folder_names)) + ". Press enter to continue")
        print("Done " + str(i) + "/" + str(len(folder_names)))

if __name__ == "__main__":
    main()