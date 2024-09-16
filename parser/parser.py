# --------------------------------------------------------------------------
# URL, HTML Parser를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import time
import sqlite3
import pandas as pd

from logging import Logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class HTMLParser:
    """URL을 바탕으로 HTML 페이지를 로드하여 파싱.

    :param db_path: sqlite3 database 위치
    :param logger: logger 객체
    """

    def __init__(self, db_path: str, logger: Logger):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.__logger = logger

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # No GUI
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        chromedriver_path = "/usr/bin/chromedriver"
        self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)

        self.__logger.info("[HTMLParser] Selenium WebDriver initialized.")

    def parse_and_save_single_url(self, url) -> None:
        """단일 URL을 파싱하고 결과를 저장"""
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            self.__logger.info(f"[HTMLParser] Fetching URL: {url}")
            self.driver.get(url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            title = soup.title.string if soup.title else "No title"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            meta_desc_content = (
                meta_desc["content"] if meta_desc else "No meta description"
            )
            body_text = (
                soup.body.get_text() if soup.body else "No body content"
            )

            self.__logger.info(f"[HTMLParser] Title: {title}")
            self.__logger.info(f"[HTMLParser] Meta Description: {meta_desc_content}")
            self.__logger.info(
                f"[HTMLParser] Body: {body_text[:100]}..."
            )  # 로그에는 처음 100자만 출력

            self.save_data(url, title, meta_desc_content, body_text)
            self.__logger.info(f"[HTMLParser] Data fetched for URL: {url}")
        except Exception as e:
            self.__logger.error(f"[HTMLParser] Error processing URL {url}: {e}")

    def save_data(self, url, title, meta_desc, body_text) -> None:
        """파싱한 데이터를 SQLite3 데이터베이스에 저장"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE phishing_data 
            SET title = ?, meta_description = ?, body_content = ? 
            WHERE url = ?
        """,
            (title, meta_desc, body_text, url),
        )
        self.conn.commit()
        self.__logger.info(f"[HTMLParser] Data saved for URL: {url}")

    def close(self) -> None:
        """Selenium WebDriver와 SQLite3 연결을 종료"""
        self.driver.quit()
        self.conn.close()
        self.__logger.info(
            "[HTMLParser] Selenium WebDriver and SQLite connection closed."
        )


class URLParser:
    """URL 데이터 셋에서 URL을 sqlite3 DB에 저장.

    :param csv_path: dataset 위치
    :param logger: logger 객체
    """

    def __init__(
        self,
        csv_path: str,
        url_column: str,
        title_column: str,
        logger: Logger,
        db_path: str,
    ):
        self.csv_path = csv_path
        self.db_path = db_path
        self.url_column = url_column
        self.title_column = title_column
        self.__logger = logger

    def parse(self) -> None:
        """CSV 파일에서 URL을 읽어 SQLite3 데이터베이스에 저장"""
        data = pd.read_csv(self.csv_path)
        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        for index, row in data.iterrows():
            url = row[self.url_column]
            title = row[self.title_column]
            cursor.execute(
                "INSERT INTO phishing_data (url, title) VALUES (?, ?)", (url, title)
            )
            self.__logger.info(f"[URLParser] URL inserted: {url}, Title: {title}")

        conn.commit()
        conn.close()
        self.__logger.info(f"[URLParser] All URLs inserted into database.")
