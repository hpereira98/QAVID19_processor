import os
import shutil
import sys
import json
import base64
from time import sleep
from datetime import datetime
from dotenv import load_dotenv

# execution interval
EXE_INTERVAL = 7200 # 2 hours

def decode_base64(str):
    base64_bytes = str.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message

def parse_html(str):
    pass

def process_file(file_path, finished_path, err_path):
    try:
        # Open JSON file
        f = open(file_path)
        # load file to dict
        data = json.load(f)

        # decode base64 string
        decoded_html = decode_base64(data["content"])

        # parse html
        parse_html(decoded_html)

        # move to finished
        with open(finished_path, 'w') as outfile:
            json.dump(data, outfile)
        os.remove(file_path)
        return True

    except Exception as e:
        print("Error trying to process file:", e)
        # move to failed
        shutil.move(file_path, err_path)
        return False

def main():
    # load env vars
    load_dotenv()
    try:
        # source dir
        SOURCE_DIR = os.environ.get("SOURCE_DIR")
        # inprogress dir
        INPROGRESS_DIR = os.environ.get("INPROGRESS_DIR")
        # error dir
        ERROR_DIR = os.environ.get("ERROR_DIR")
        # finished_dir
        FINISHED_DIR = os.environ.get("FINISHED_DIR")
    except Exception as e:
        print("Error loading .env vars:", e)
        sys.exit()

    # start execution
    while True:
        try:
            print("Starting execution:", datetime.now())
            processed_files_count = 0
            error_files_count = 0
            # iterate over files in source_dir and move them to inprogress_dir
            for _, _, files in os.walk(SOURCE_DIR):
                for filename in files:
                    #shutil.move(SOURCE_DIR + '/' + filename, INPROGRESS_DIR + '/' + filename)
                    shutil.copy2(SOURCE_DIR + '/' + filename, INPROGRESS_DIR + '/' + filename)

            # start processing files
            for _, _, files in os.walk(INPROGRESS_DIR):
                for filename in files:
                    if process_file(INPROGRESS_DIR + '/' + filename, FINISHED_DIR + '/' + filename, ERROR_DIR + '/' + filename):
                        processed_files_count += 1
                    else:
                        error_files_count += 1
            
            print("Processed files:", processed_files_count)
            print("Failed processing:", error_files_count)
            sleep(EXE_INTERVAL)

        except KeyboardInterrupt:
            print("Interruption signal at", datetime.now())
            print("Stopping execution...")
            sys.exit()

if __name__ == '__main__':
    main()