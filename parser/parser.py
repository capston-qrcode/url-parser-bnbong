# --------------------------------------------------------------------------
# URL, HTML Parser를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import time
import platform
import sqlite3

import pandas as pd
from pandas import DataFrame

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from logging import Logger


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

        if platform.system() == "Darwin":  # MacOS M1 (local)
            self.driver = webdriver.Chrome(options=chrome_options)
        else:  # Ubuntu, Linux (cloud)
            chromedriver_path = "/usr/bin/chromedriver"
            self.driver = webdriver.Chrome(
                service=Service(chromedriver_path), options=chrome_options
            )

        self.__logger.info("[HTMLParser] Selenium WebDriver initialized.")

    def parse_and_save_single_url(self, url, label) -> None:
        """단일 URL을 파싱하고 결과를 저장"""
        try:
            self.__logger.info(f"[HTMLParser] Fetching URL: {url}")
            self.driver.get(url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            html_content = str(soup)

            self.__logger.info(f"[HTMLParser] Fetched HTML content for {url}")

            self._save_data(url, html_content, label)
            self.__logger.info(f"[HTMLParser] Data saved for URL: {url}")
            self.__logger.debug(f"[HTMLParser] saved HTML content : {html_content}")
        except Exception as e:
            self.__logger.error(f"[HTMLParser] Error processing URL {url}: {e}")

    def _save_data(self, url, html_content, label) -> None:
        """파싱한 데이터를 SQLite3 데이터베이스에 저장"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE phishing_data 
            SET html_content = ?, label = ? 
            WHERE url = ?
        """,
            (html_content, label, url),
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
        label_column: str,
        logger: Logger,
        db_path: str,
        data: DataFrame,
    ):
        self.csv_path = csv_path
        self.db_path = db_path
        self.url_column = url_column
        self.label_column = label_column
        self.data = data
        self.__logger = logger

    def parse(self) -> None:
        """CSV 파일에서 URL과 Label을 읽어 SQLite3 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for index, row in self.data.iterrows():
            url = row[self.url_column]
            label = row[self.label_column] if self.label_column else "unknown"

            if not label == "unknown" and label in ["benign", "Benign"]:
                self.__logger.warning(
                    f"Skipping row {index} via Benign URL."
                )
                continue

            if pd.isna(url) or pd.isna(label):
                self.__logger.warning(
                    f"Skipping row {index} due to missing URL or label."
                )
                continue

            # URL 형식 보정
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            cursor.execute(
                "INSERT INTO phishing_data (url, label) VALUES (?, ?)", (url, label)
            )
            self.__logger.info(f"[URLParser] URL inserted: {url}, Label: {label}")

        conn.commit()
        conn.close()
        self.__logger.info(f"[URLParser] All URLs inserted into database.")
