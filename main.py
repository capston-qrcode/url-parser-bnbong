# --------------------------------------------------------------------------
# Parser를 동작시키는 메인 모듈입니다.
#
# 전체 구조 : 모든 데이터셋에서 url을 추출하여 sqlite3 DB에 저장 (URLParser)
#           -> url 저장이 완료 된 후 url에서 HTML 요소를 추출 (HTMLParser)
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import sqlite3
from typing import List
import pandas as pd
import threading

from datetime import datetime

from db import init_db
from parser.parser import HTMLParser, URLParser
from logger.logger import get_logger

logger = get_logger()


def start_crawler_thread(
    thread_id: int, urls: List[str], labels: List[str], db_path: str
) -> None:
    """각 스레드에서 URL을 처리하는 함수"""
    logger.info(f"[Thread-{thread_id}] Processing URLs: {len(urls)}")
    html_parser = HTMLParser(db_path, logger=logger)

    for url, label in zip(urls, labels):
        try:
            logger.info(f"[Thread-{thread_id}] Processing URL: {url}")
            html_parser.parse_and_save_single_url(url, label)
            logger.info(f"[Thread-{thread_id}] Finished URL: {url}")
        except Exception as e:
            logger.error(f"[Thread-{thread_id}] Error processing URL {url}: {e}")

    html_parser.close()
    logger.info(f"[Thread-{thread_id}] Finished processing all URLs.")


def divide_indices(total_count: int, num_threads: int) -> List[range]:
    """인덱스를 스레드 개수에 따라 나누는 함수"""
    avg = total_count // num_threads
    indices = [range(i * avg, (i + 1) * avg) for i in range(num_threads)]
    if total_count % num_threads != 0:
        indices[-1] = range((num_threads - 1) * avg, total_count)
    return indices


def load_csv_and_store_urls(csv_path: str, db_path: str) -> None:
    """CSV 파일을 불러와 URL과 Label을 DB에 저장"""
    logger.info(f"Loading dataset from {csv_path}...")
    try:
        data = pd.read_csv(csv_path, on_bad_lines="skip")
    except UnicodeDecodeError:
        data = pd.read_csv(csv_path, encoding="ISO-8859-1", on_bad_lines="skip")

    url_column = None
    label_column = None

    for possible_url_col in [
        "domain",
        "URLs",
        "url",
        "urls",
        "URL",
        "Website",
        "Link",
        "홈페이지주소",
    ]:
        if possible_url_col in data.columns:
            url_column = possible_url_col
            break

    for possible_label_col in ["label", "Label", "classification", "Category"]:
        if possible_label_col in data.columns:
            label_column = possible_label_col
            break

    if not url_column:
        logger.error("Unrecognized CSV format. URL column not found.")
        return

    logger.info(f"Using URL column: {url_column}, Label column: {label_column}")

    url_parser = URLParser(
        csv_path=csv_path,
        url_column=url_column,
        label_column=label_column,
        logger=logger,
        db_path=db_path,
        data=data,
    )
    url_parser.parse()


def fetch_urls_from_db(db_path: str) -> List:
    """데이터베이스에서 아직 처리되지 않은 URL과 Label을 가져옴"""
    logger.info("Fetching URLs from database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, label FROM phishing_data WHERE html_content IS NULL")
    urls_labels = cursor.fetchall()
    conn.close()
    return urls_labels


def process_all_urls(db_path: str, threads_num: int) -> None:
    """수집된 모든 URL에 대해 스레드를 사용해 HTML 파싱을 진행"""
    urls_labels = fetch_urls_from_db(db_path)

    if not urls_labels:
        logger.info("No URLs to process.")
        return

    urls, labels = zip(*urls_labels)

    url_indices = divide_indices(len(urls), threads_num)

    threads = []
    logger.info("Initializing threads...")
    for idx, indices in enumerate(url_indices):
        thread_urls = [urls[i] for i in indices]
        thread_labels = [labels[i] for i in indices]
        thread = threading.Thread(
            target=start_crawler_thread, args=(idx, thread_urls, thread_labels, db_path)
        )
        thread.start()
        logger.info(f"Thread {idx} started.")
        threads.append(thread)

    for thread in threads:
        thread.join()

    logger.info("All threads finished processing.")


def main():
    logger.info("Initializing database...")
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = f"db/phishing_sites_{current_time}.db"
    init_db.initialize_database(db_path)

    csv_files = [
        "dataset/balanced_urls.csv",
        "dataset/phishing_and_benign_websites.csv",
        "dataset/urlset.csv",
        "dataset/한국인터넷진흥원_피싱사이트 URL_20221130.csv",
        "dataset/202401.csv",
        "dataset/202402.csv",
        "dataset/202403.csv",
        "dataset/202404.csv",
        "dataset/202405.csv",
        "dataset/202406.csv",
        "dataset/202407.csv",
    ]

    for csv_file in csv_files:
        load_csv_and_store_urls(csv_file, db_path)

    threads_num = int(os.getenv("THREADS", 8))
    process_all_urls(db_path, threads_num)


if __name__ == "__main__":
    logger.info("Starting parser...")
    main()
    logger.info("Parser finished.")
