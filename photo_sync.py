import os
import shutil
from datetime import datetime
import time
import exiftool

ET = exiftool.ExifToolHelper()

def get_file_iterator(root: str):
    for root, _, files in os.walk(root):
        for file in files:
            yield os.path.abspath(os.path.join(root, file)), file

def get_create_date(path: str):
    metadata = ET.get_metadata(path)
    if metadata[0]["File:MIMEType"].startswith("video"):
        key = "QuickTime:CreateDate"
    else:
        key = "EXIF:DateTimeOriginal"
    if key not in metadata[0]:
        if os.getenv("ASSUME_CURRENT_DAY"):
            print(f"Assuming current day for {path}")
            return datetime.now()
        else:
            return None
    return datetime.strptime(metadata[0][key], '%Y:%m:%d %H:%M:%S')

if __name__ == "__main__":
    while True:
        source_root = os.getenv("SOURCE_ROOT")
        if not source_root:
            raise RuntimeError("Environment Variable SOURCE_ROOT must be set")

        target_root = os.getenv("TARGET_ROOT")
        if not source_root:
            raise RuntimeError("Environment Variable SOURCE_ROOT must be set")
        
        for absolute_path, filename in get_file_iterator(source_root):
            create_date = get_create_date(absolute_path)
            if not create_date:
                print(f"Could not determine create date for {absolute_path}...")
                if os.getenv("DUMPING_GROUND"):
                    shutil.move(absolute_path, os.path.join(os.getenv("DUMPING_GROUND"), filename))
                continue
            target_path = os.path.join(
                target_root, str(create_date.year),
                "{:02d}".format(create_date.month),
                "{:02d}".format(create_date.day),
                filename)
            if absolute_path == target_path:
                print(f"{absolute_path} seems to be at the right place already...")
            else:
                print(f"Moving {absolute_path} to {target_path}")
                if not os.getenv("DRYRUN"):
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.move(absolute_path, target_path)
        if os.getenv("RUN_ONCE"):
            exit(0)
        print(f"Current Time: {datetime.now()}, Going to sleep...")
        time.sleep(int(12*60*60))