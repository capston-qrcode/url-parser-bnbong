# --------------------------------------------------------------------------
# Parser 모듈 테스트케이스 입니다.
#
# 데이터셋에 있는 URL을 sqlite3 DB에 잘 저장하는지 테스트합니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import sqlite3
import unittest
from unittest.mock import patch

from parser.parser import URLParser
from db import init_db
from logger.logger import get_logger

logger = get_logger()


class TestPhishingParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """테스트 환경을 위한 SQLite3 데이터베이스 생성"""
        cls.db_path = "test_phishing_sites.db"
        init_db.initialize_database(cls.db_path)

        # Mock ChromeDriver for HTMLParser
        cls.mock_driver = patch("selenium.webdriver.Chrome").start()
        cls.mock_driver_instance = cls.mock_driver.return_value
        cls.mock_driver_instance.get.return_value = None
        cls.mock_driver_instance.page_source = (
            "<html><head><title>Test</title></head><body>Test content</body></html>"
        )

        cls.test_dataset_1_path = os.path.join(
            os.path.dirname(__file__), "../dataset/urlset.csv"
        )
        cls.test_dataset_2_path = os.path.join(
            os.path.dirname(__file__), "../dataset/phishing_and_benign_websites.csv"
        )
        cls.test_dataset_3_path = os.path.join(
            os.path.dirname(__file__), "../dataset/balanced_urls.csv"
        )

    @classmethod
    def tearDownClass(cls):
        """테스트가 끝난 후 SQLite3 데이터베이스 삭제"""
        patch.stopall()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_url_parser_with_dataset_1(self):
        """dataset/urlset.csv 파일에서 URL과 label을 제대로 파싱하는지 테스트"""
        url_parser = URLParser(
            csv_path=self.test_dataset_1_path,
            url_column="domain",
            label_column="label",
            logger=logger,
            db_path=self.db_path,
        )
        url_parser.parse()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, label FROM phishing_data")
        results = cursor.fetchall()

        self.assertGreater(len(results), 0)
        self.assertEqual(
            results[0][0],
            "nobell.it/70ffb52d079109dca5664cce6f317373782/login.SkyPe.com/en/cgi-bin/verification/login/70ffb52d079109dca5664cce6f317373/index.php?cmd=_profile-ach&outdated_page_tmpl=p/gen/failed-to-load&nav=0.5.1&login_access=1322408526",
        )
        self.assertEqual(results[0][1], "1.0")

    def test_url_parser_with_dataset_2(self):
        """dataset/phishing_and_benign_websites.csv 파일에서 URL과 label을 제대로 파싱하는지 테스트"""
        url_parser = URLParser(
            csv_path=self.test_dataset_2_path,
            url_column="URLs",
            label_column="Label",
            logger=logger,
            db_path=self.db_path,
        )
        url_parser.parse()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, label FROM phishing_data")
        results = cursor.fetchall()

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0], "http://www.wmmayhem.com/")
        self.assertEqual(results[0][1], "Benign")

    def test_url_parser_with_dataset_3(self):
        """dataset/balanced_urls.csv 파일에서 URL과 label을 제대로 파싱하는지 테스트"""
        url_parser = URLParser(
            csv_path=self.test_dataset_3_path,
            url_column="url",
            label_column="label",
            logger=logger,
            db_path=self.db_path,
        )
        url_parser.parse()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, label FROM phishing_data")
        results = cursor.fetchall()

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0], "https://www.google.com")
        self.assertEqual(results[0][1], "benign")

    def test_multiple_csv_parsing(self):
        """여러 CSV 파일을 파싱하고 데이터를 저장하는지 확인"""
        csv_files = [
            self.test_dataset_1_path,
            self.test_dataset_2_path,
            self.test_dataset_3_path,
        ]

        for csv_file in csv_files:
            if "1.csv" in csv_file:
                url_column, label_column = "domain", "label"
            elif "2.csv" in csv_file:
                url_column, label_column = "URLs", "Label"
            else:
                url_column, label_column = "url", "label"

            url_parser = URLParser(
                csv_path=csv_file,
                url_column=url_column,
                label_column=label_column,
                logger=logger,
                db_path=self.db_path,
            )
            url_parser.parse()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM phishing_data")
        results = cursor.fetchall()

        self.assertGreater(len(results), 0)
        conn.close()


if __name__ == "__main__":
    unittest.main()
