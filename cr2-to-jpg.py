#!/usr/bin/env python3

# import what we need
from argparse import ArgumentParser
from rawpy import imread

from tqdm import tqdm
from PIL import Image

from os import getcwd, walk, utime, mkdir
from os.path import join, splitext, getmtime, basename, exists

# params
parser = ArgumentParser(description='Convert CR2 to JPG')
parser.add_argument('--recursive', help='Load files recursively from subdirs of Source Folder', required=False, default=False, type=bool)
parser.add_argument('--use-camera-wb', help='Use camera white balance', required=False, default=True, type=bool)
args = parser.parse_args()

def get_raw_images(raw_dir, raw_file_types, recursive=False):
    raw_files = []
    for root, dirs, files in walk(raw_dir):
        # find raw files
        for file in files:
            # ### probably not the best
            for raw_file_type in raw_file_types:
                if file.endswith(raw_file_type):
                    raw_files.append(join(root, file))
                    break

        # if recursive find in subfolders
        if recursive:
            for dir in dirs:
                subfolder_raw_files = get_raw_images(join(root, dir), raw_file_types, recursive)
                raw_files.extend(subfolder_raw_files)

    return raw_files


# converter function which iterates through list of files
def convert_cr2_to_jpg(raw_images, converted_dir, use_camera_wb=True):
    
    # exit if no image found in source
    if len(raw_images) == 0:
        print("No raw images found...\nExiting")
        exit(1)
        
    # create converted dir if it doesn't exist
    if not exists(converted_dir):
        mkdir(converted_dir)

    tq = tqdm(raw_images)
    for raw_image in tq:
        tq.set_description_str(f"Converting the following raw image: {raw_image} to JPG")

        # file vars
        file_name = basename(raw_image)
        file_without_ext = splitext(file_name)[0]
        file_timestamp = getmtime(raw_image)

        # parse CR2 image
        with imread(raw_image) as raw_image_process:
            # Postprocess
            rgb = raw_image_process.postprocess(use_camera_wb=use_camera_wb)

            # Save image
            with Image.fromarray(rgb) as jpg_image:
                jpg_image_location = converted_dir + file_without_ext + '.jpg'
                jpg_image.save(jpg_image_location, format="jpeg", optimize=True)

                # update JPG file timestamp to match CR2
                utime(jpg_image_location, (file_timestamp,file_timestamp))


# call function
if __name__ == "__main__":

    # dirs and files
    raw_file_types = [".cr2",".CR2"]
    raw_dir = getcwd()

    # get raw images
    print("Recursive mode:",args.recursive)
    raw_images = get_raw_images(raw_dir, raw_file_types, args.recursive)

    # set converted dir
    converted_dir = join(raw_dir, 'converted/')
    
    use_camera_wb = args.use_camera_wb
    print("Use camera white balance:",use_camera_wb)
    convert_cr2_to_jpg(raw_images, converted_dir, use_camera_wb)
