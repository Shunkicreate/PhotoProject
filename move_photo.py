import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import os

def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()

def get_date_time(exif):
    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "DateTimeOriginal":
            return value
    return None

def get_month_folder_path(base_folder, year, month):
    folder_path = os.path.join(base_folder, year, month)
    return folder_path

def create_month_folder(base_folder, year, month, index):
    month_folder = f"{month}_{index:02d}"
    month_folder_path = get_month_folder_path(base_folder, year, month_folder)
    os.makedirs(month_folder_path, exist_ok=True)
    return month_folder_path

def move_file_to_nas(file_path, nas_base_folder, file_count):
    exif = get_exif(file_path)
    date_time = get_date_time(exif) if exif else None
    if date_time:
        date_obj = datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
    else:
        date_obj = datetime.fromtimestamp(os.path.getmtime(file_path))
        
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")
    time = date_obj.strftime("%H-%M-%S")
    
    base_folder = os.path.join(nas_base_folder, year)
    os.makedirs(base_folder, exist_ok=True)
    
    month_folder = create_month_folder(base_folder, year, month, file_count // 100)
    new_name = f"{month}-{day}_{time}_{os.path.basename(file_path)}"
    dest_path = os.path.join(month_folder, new_name)
    
    shutil.copy2(file_path, dest_path)
    print(f"Moved {file_path} to {dest_path}")

def process_folder(source_folder, nas_base_folder):
    file_count = 0
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.json')):
                file_path = os.path.join(root, file)
                move_file_to_nas(file_path, nas_base_folder, file_count)
                file_count += 1

source_folder = os.environ.get('SOURCE_FOLDER')
nas_base_folder = os.environ.get('NAS_BASE_FOLDER')

process_folder(source_folder, nas_base_folder)

process_folder(source_folder, nas_base_folder)
