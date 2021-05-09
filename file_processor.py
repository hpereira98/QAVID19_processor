import os
import shutil
import sys
import json
import base64
import html2text
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# execution interval
EXE_INTERVAL = 7200 # 2 hours

def decode_base64(str):
    base64_bytes = str.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message

def parse_html(html_parser, html_str):
    return html_parser.handle(html_str)

def parse_html_bs4(html_str):
    soup = BeautifulSoup(html_str, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    # get text
    text = soup.get_text()
    # # break into lines and remove leading and trailing space on each
    # lines = (line.strip() for line in text.splitlines())
    # # break multi-headlines into a line each
    # chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # # drop blank lines
    # text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def process_file(filename, inprogress_path, finished_path, err_path, html_parser, clean_text_dir):
    try:
        # Open JSON file
        f = open(inprogress_path + "/" + filename)
        # load file to dict
        data = json.load(f)

        # decode base64 string
        decoded_html = decode_base64(data["content"])

        # parse html
        text = parse_html(html_parser, decoded_html)
        #text = parse_html_bs4(decoded_html)

        # write clean text to file
        with open(clean_text_dir + "/" + filename + ".txt", "w") as clean_text_file:
            # Writing data to a file
            clean_text_file.write(text)

        # move to finished
        shutil.move(inprogress_path + "/" + filename, finished_path + "/" + filename)
        return True

    except Exception as e:
        print("Error trying to process file:", e)
        # move to failed
        shutil.move(inprogress_path + "/" + filename, err_path + "/" + filename)
        return False

def init_html_parser():
    html_parser = html2text.HTML2Text()
    html_parser.ignore_links = True
    html_parser.bypass_tables = False
    html_parser.ignore_images = True
    html_parser.ignore_emphasis = True
    html_parser.ignore_tables = True
    html_parser.use_automatic_links = False
    return html_parser

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
        # clean text dir
        CLEAN_TEXT_DIR = os.environ.get("CLEAN_TEXT_DIR")
    except Exception as e:
        print("Error loading .env vars:", e)
        sys.exit()

    html_parser = init_html_parser()

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
                    if process_file(filename, INPROGRESS_DIR, FINISHED_DIR, ERROR_DIR, html_parser, CLEAN_TEXT_DIR):
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