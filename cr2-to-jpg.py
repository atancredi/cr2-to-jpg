#!/usr/bin/env python3

# import what we need
import argparse
import numpy
import os
import glob
import time
import rawpy
from alive_progress import alive_bar
from PIL import Image
# params
parser = argparse.ArgumentParser(description='Convert CR2 to JPG')
parser.add_argument('-s', '--source', help='Source folder of CR2 files', required=True)
parser.add_argument('-d', '--destination', help='Destination folder for converted JPG files', required=True)
parser.add_argument('--recursive', help='Load files recursively from subdirs of Source Folder', required=False, default=False)
args = parser.parse_args()

# dirs and files
raw_file_type = ".cr2"
raw_dir = args.source + '/'

# sanity check
if not os.path.exists(args.destination):
    print("Destination directory does not exist\nExiting")
    exit(1)

if not os.path.isdir(args.destination):
    print("Destination is not a directory\nExiting")
    exit(1)

converted_dir = args.destination + '/'

# load images recursively if required
if args.recursive:
    raw_images = glob.glob(raw_dir + '/*/*' + raw_file_type)
else:
    raw_images = glob.glob(raw_dir + '*' + raw_file_type)

# exit if no image found in source
if len(raw_images) == 0:
    print("Nothing to do...\nExiting")
    exit(1)


# converter function which iterates through list of files
def convert_cr2_to_jpg(raw_images):
    print(f"Number of files to convert: {len(raw_images)}")
    with alive_bar(len(raw_images)) as bar:
        for raw_image in raw_images:
            #print(f"Converting the following raw image: {raw_image} to JPG")

            # file vars
            file_name = os.path.basename(raw_image)
            file_without_ext = os.path.splitext(file_name)[0]
            file_timestamp = os.path.getmtime(raw_image)

            # parse CR2 image
            raw_image_process = rawpy.imread(raw_image)
            print(raw_image_process)
            exit()
            #buffered_image = numpy.array(raw_image_process.to_buffer())

            # check orientation due to PIL image stretch issue
            if raw_image_process.metadata.orientation == 0:
                jpg_image_height = raw_image_process.metadata.height
                jpg_image_width = raw_image_process.metadata.width
            else:
                jpg_image_height = raw_image_process.metadata.width
                jpg_image_width = raw_image_process.metadata.height

            # prep JPG details
            jpg_image_location = converted_dir + file_without_ext + '.jpg'
            jpg_image = Image.frombytes('RGB', (jpg_image_width, jpg_image_height), buffered_image)
            jpg_image.save(jpg_image_location, format="jpeg")

            # update JPG file timestamp to match CR2
            os.utime(jpg_image_location, (file_timestamp,file_timestamp))

            # close to prevent too many open files error
            jpg_image.close()
            raw_image_process.close()
            bar()

# call function
if __name__ == "__main__":
    convert_cr2_to_jpg(raw_images)
