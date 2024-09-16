# TODO: 데이터셋 넣기
# --------------------------------------------------------------------------
# Parser를 동작시키는 메인 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import sqlite3
import pandas as pd
import threading

from datetime import datetime

from db import init_db
from parser.parser import HTMLParser, URLParser
from logger.logger import get_logger

logger = get_logger()


def start_crawler_thread(thread_id, urls, db_path):
    """각 스레드에서 URL을 처리하는 함수"""
    logger.info(f"[Thread-{thread_id}] Processing URLs: {len(urls)}")
    html_parser = HTMLParser(db_path, logger=logger)

    for url in urls:
        try:
            logger.info(f"[Thread-{thread_id}] Processing URL: {url}")
            html_parser.parse_and_save_single_url(url)
            logger.info(f"[Thread-{thread_id}] Finished URL: {url}")
        except Exception as e:
            logger.error(f"[Thread-{thread_id}] Error processing URL {url}: {e}")

    html_parser.close()
    logger.info(f"[Thread-{thread_id}] Finished processing all URLs.")


def divide_indices(total_count, num_threads):
    """인덱스를 스레드 개수에 따라 나누는 함수"""
    avg = total_count // num_threads
    indices = [range(i * avg, (i + 1) * avg) for i in range(num_threads)]
    if total_count % num_threads != 0:
        indices[-1] = range((num_threads - 1) * avg, total_count)
    return indices


def main():
    logger.info("Initializing database...")
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = f"db/phishing_sites_{current_time}.db"
    init_db.initialize_database(db_path)

    csv_path = os.getenv(
        "CSV_PATH", "dataset/한국인터넷진흥원_피싱사이트 URL_20221130.csv"
    )
    threads_num = int(os.getenv("THREADS", 8))

    logger.info(f"Loading dataset from {csv_path}...")
    data = pd.read_csv(csv_path)
    url_column = data.columns[1]
    title_column = data.columns[0]

    logger.info(f"Using URL column: {url_column}, Title column: {title_column}")
    url_parser = URLParser(
        csv_path=csv_path,
        url_column=url_column,
        title_column=title_column,
        logger=logger,
        db_path=db_path,
    )
    url_parser.parse()

    logger.info("Fetching URLs from database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM phishing_data")
    urls = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not urls:
        logger.info("No URLs to process.")
        return

    # URL을 스레드 수에 맞게 나누기
    url_indices = divide_indices(len(urls), threads_num)

    threads = []
    logger.info("Initializing threads...")
    for idx, indices in enumerate(url_indices):
        thread_urls = [urls[i] for i in indices]
        thread = threading.Thread(
            target=start_crawler_thread, args=(idx, thread_urls, db_path)
        )
        thread.start()
        logger.info(f"Thread {idx} started.")
        threads.append(thread)

    for thread in threads:
        thread.join()

    logger.info("All threads finished processing.")


if __name__ == "__main__":
    logger.info("Starting parser...")
    main()
    logger.info("Parser finished.")
