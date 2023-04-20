import os
import shutil

# specify the paths to the source and destination folders
src_folder = "/Users/hieu.huynh/Downloads/webis-webseg-20"
dest_folder = "/Users/hieu.huynh/Downloads/webis-webseg-20 2"

# specify the patterns of files to keep
file_patterns = [".json"]

# loop through each subdirectory in the source folder
for subdir, dirs, files in os.walk(src_folder):
    # create the corresponding subdirectory in the destination folder
    print(subdir)
    # input()
    dest_subdir = subdir.replace(src_folder, dest_folder)
    os.makedirs(dest_subdir, exist_ok=True)
    # loop through each file in the subdirectory
    for file in files:
        # check if the file matches any of the patterns
        if any(file.endswith(pattern) for pattern in file_patterns):
            # copy the file to the corresponding subdirectory in the destination folder
            # input("copying " + file + " to " + dest_subdir + " ...")
            src_file = os.path.join(subdir, file)
            dest_file = os.path.join(dest_subdir, file)
            shutil.copy2(src_file, dest_file)
            # input("copied " + file + " to " + dest_subdir + " ...")
