import os
import shutil
import re
import argparse
import tarfile
from datetime import datetime, timedelta

def archive_and_move_folder(source_path, target_directory, folder_type):
    """ Creates a tar.gz archive of the folder and moves it to the respective target subdirectory. """
    folder_name = os.path.basename(source_path)
    archive_name = f"{folder_name}.tar.gz"
    
    category_path = os.path.join(target_directory, folder_type)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
        print(f"[DEBUG] Created target subdirectory: {category_path}")

    archive_path = os.path.join(category_path, archive_name)

    print(f"[DEBUG] Archiving folder: {source_path} -> {archive_path}")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source_path, arcname=folder_name)

    shutil.rmtree(source_path)  # Remove original folder after archiving
    print(f"[DEBUG] Deleted original folder after archiving: {source_path}")

def move_old_folders(base_directory, target_directory):
    """ Finds 'exposures' and 'timelapse' folders **in any subdirectory**, extracts the date from folder names,
        archives them if older than 7 days, and moves them to the respective target subdirectory. """

    date_pattern = re.compile(r'\d{8}')  # YYYYMMDD format
    threshold_date = datetime.now() - timedelta(days=7)
    print(f"[DEBUG] Threshold date for deletion: {threshold_date.strftime('%Y-%m-%d')}")

    for root, dirs, _ in os.walk(base_directory):
        print(f"[DEBUG] Scanning directory: {root}")
        for dir_name in dirs:
            full_path = os.path.join(root, dir_name)  # Check entire path

            folder_type = None
            if "exposures" in full_path:
                folder_type = "exposures"
            elif "timelapse" in full_path:
                folder_type = "timelapse"
            
            print(f"[DEBUG] Folder '{dir_name}' categorized as: {folder_type}")

            if not folder_type:
                continue

            match = date_pattern.search(dir_name)
            if match:
                folder_date = datetime.strptime(match.group(), "%Y%m%d")
                print(f"[DEBUG] Found folder: {full_path} (Date: {folder_date.strftime('%Y-%m-%d')})")

                if folder_date < threshold_date:
                    print(f"[DEBUG] Folder is older than threshold. Archiving...")
                    archive_and_move_folder(full_path, target_directory, folder_type)

def main():
    parser = argparse.ArgumentParser(description="Archive and move old 'exposures' and 'timelapse' folders.")
    parser.add_argument("base_directory", help="Base directory to scan")
    parser.add_argument("target_directory", help="Target directory to store archives")

    args = parser.parse_args()

    if not os.path.exists(args.target_directory):
        os.makedirs(args.target_directory)
        print(f"[DEBUG] Created target directory: {args.target_directory}")

    move_old_folders(args.base_directory, args.target_directory)
    print("[DEBUG] Archiving and cleanup complete!")

if __name__ == "__main__":
    main()

