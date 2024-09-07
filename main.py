# TODO: 데이터셋 넣기
# --------------------------------------------------------------------------
# Parser를 동작시키는 메인 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import sqlite3

from concurrent.futures import ThreadPoolExecutor

from db import init_db
from parser.parser import HTMLParser, URLParser
from logger.logger import get_logger

logger = get_logger(__name__)


def process_url(url, db_path: str) -> None:
    """각 URL을 파싱하고 HTML 데이터를 처리하는 함수"""
    logger.info(f"Processing URL: {url}")

    html_parser = HTMLParser(db_path, logger=logger)
    html_parser.parse_and_save_single_url(url)
    html_parser.close()


def main():
    """Parser 메인 동작 함수"""
    # init sqlite3 db
    logger.info("Initializing database...")
    init_db.initialize_database()

    # load env
    db_path = os.getenv("DB_PATH", "db/phishing_sites.db")
    csv_path = os.getenv("CSV_PATH", "dataset/phishing_data.csv")
    threads = int(os.getenv("THREADS", 8))  # 기본 스레드 개수는 8개로 고정(docker compose 동일)

    logger.info(f"Loading URLs from {csv_path}...")
    url_parser = URLParser(csv_path, logger=logger)
    url_parser.parse()

    logger.info(f"Processing URLs with {threads} threads...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM phishing_data WHERE title IS NULL")
    urls = [row[0] for row in cursor.fetchall()]
    conn.close()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(lambda url: process_url(url, db_path), urls)

    logger.info("All URLs processed successfully.")


if __name__ == "__main__":
    logger.info("Starting parser...")
    main()
    logger.info("Parser finished.")
