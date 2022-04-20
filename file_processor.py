import os
import shutil
import sys
import json
import base64
import html2text
import requests
from elasticsearch import Elasticsearch
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langdetect import detect

# execution interval
EXE_INTERVAL = 7200  # 2 hours


def decode_base64(str):
    base64_bytes = str.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message


def encode_base64(str):
    message_bytes = str.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message[:512]


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


def create_elasticsearch_doc(es, url, text, idx):
    doc = {"url": url, "text": text, "indexed_date": datetime.now()}
    es.index(index=idx, id=encode_base64(url), body=doc)


def process_file(filename, inprogress_path, finished_path, err_path, html_parser, clean_text_dir, es):
    try:
        # Open JSON file
        f = open(inprogress_path + "/" + filename)
        # load file to dict
        data = json.load(f)

        # decode base64 string
        decoded_html = decode_base64(data["content"])
        # data["content"] = decoded_html

        # parse html
        text = parse_html(html_parser, decoded_html)
        #text = parse_html_bs4(decoded_html)

        # detect language
        try:
            lang = detect(text.lower())
        except Exception as e:
            print("Error on language detection:", e)
            lang = "undefined"

        if lang not in lang_count:
            lang_count[lang] = 0
        lang_count[lang] += 1

        # write clean text to file
        # with open(f"{clean_text_dir}/{filename}.txt", "w") as clean_text_file:
        #     # Writing data to a file
        #     clean_text_file.write(text)

        # create index name
        idx = f"covid_{lang}_v2"

        # with open(clean_text_dir + "_1/" + filename + ".txt", "w") as decoded_json:
        #     # Writing data to a file
        #     json.dump(data,decoded_json)

        # index treated text with elasticsearch
        create_elasticsearch_doc(es, data["url"], text, idx)

        # move to finished
        shutil.move(inprogress_path + "/" + filename,
                    finished_path + "/" + filename)

        return True

    except Exception as e:
        print("Error trying to process file:", e)
        # move to failed
        shutil.move(inprogress_path + "/" + filename,
                    err_path + "/" + filename)
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


def init_elasticsearch():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    return es


def check_elasticsearch_running():
    res = requests.get('http://localhost:9200')
    return res.status_code


def main():
    # load env vars
    load_dotenv()

    global lang_count
    lang_count = {}

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
    es = init_elasticsearch()

    try:
        es_status = check_elasticsearch_running()
    except:
        print("Could not connect to ElasticSearch!")
        print("Exiting...")
        sys.exit()

    if es_status != 200:
        print("Could not connect to ElasticSearch!")
        print("Exiting...")
        sys.exit()
    else:
        print("Connected successfully to ElasticSearch!")

    # start execution
    while True:
        try:
            print("Starting execution:", datetime.now())
            processed_files_count = 0
            error_files_count = 0
            # iterate over files in source_dir and move them to inprogress_dir
            for _, _, files in os.walk(SOURCE_DIR):
                for filename in files:
                    shutil.move(SOURCE_DIR + '/' + filename,
                                INPROGRESS_DIR + '/' + filename)
                    # shutil.copy2(SOURCE_DIR + '/' + filename,
                    #              INPROGRESS_DIR + '/' + filename)

            # start processing files
            for _, _, files in os.walk(INPROGRESS_DIR):
                for filename in files:
                    if process_file(filename, INPROGRESS_DIR, FINISHED_DIR, ERROR_DIR, html_parser, CLEAN_TEXT_DIR, es):
                        processed_files_count += 1
                    else:
                        error_files_count += 1

            print("Processed files:", processed_files_count)
            print("Failed processing:", error_files_count)
            print("Language Count: ", lang_count)
            sleep(EXE_INTERVAL)

        except KeyboardInterrupt:
            print("Interruption signal at", datetime.now())
            print("Stopping execution...")
            sys.exit()


if __name__ == '__main__':
    main()
