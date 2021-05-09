import os
import shutil
import sys
from time import sleep
from datetime import datetime
from dotenv import load_dotenv

# control_file
CTRL_FILE = "processed_files.txt"
# execution interval
EXE_INTERVAL = 7200 # 2 hours

def main():
    # load env vars
    load_dotenv()
    try:
        # destination dir
        DEST_DIR = os.environ.get("SOURCE_DIR")
        # source pages dir
        PAGES_DIR = os.environ.get("PAGES_DIR")
    except Exception as e:
        print("Error loading .env vars:", e)
        sys.exit()

    # start execution
    while True:
        try:
            print("Starting execution:", datetime.now())
            moved_files_count = 0
            with open(CTRL_FILE,'a+') as f:
                # get moved file list
                f.seek(0)
                moved_files = f.read()
                moved_files = moved_files.split('\n')
                # iterate over files in pages_dir
                for dirname, dirs, files in os.walk(PAGES_DIR):
                    for filename in files:
                        if filename not in moved_files:
                            shutil.copy2(dirname + '/' + filename, DEST_DIR)
                            f.write(filename + '\n')
                            moved_files_count += 1
            print("Moved files:", moved_files_count)
            # sleep for the given interval
            sleep(EXE_INTERVAL)

        except KeyboardInterrupt:
            print("Interruption signal at", datetime.now())
            print("Stopping execution...")
            sys.exit()

if __name__ == '__main__':
    main()