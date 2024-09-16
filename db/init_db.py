# --------------------------------------------------------------------------
# SQLite3 데이터베이스 셋업 로직을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
#
# 컬럼 이름	데이터 타입	설명
# id	            INTEGER	기본 키(PK), 자동 증가
# url	            TEXT	웹사이트 URL, 중복되지 않음
# title	            TEXT	HTML 페이지 title
# meta_description  TEXT    HTML 메타데이터
# body_content      TEXT    HTML content 전문
# label	            INTEGER	피싱 여부를 나타내는 필드 (1 = 피싱, 0 = 정상),
#               추후 트랜스포머 모델이 피싱 사이트 판별 후 라벨 업데이트.
# --------------------------------------------------------------------------
import os
import sqlite3

from sqlite3 import Error
from sqlite3.dbapi2 import Connection


def create_connection(db_file) -> Connection:
    """SQLite3 데이터베이스에 연결하고 커넥션을 반환"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Error connecting to SQLite database: {e}")
    return conn


def create_table(conn) -> None:
    """phishing_data 테이블을 생성"""
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS phishing_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                html_content TEXT,
                label TEXT
            );
        """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(f"Error creating table: {e}")


def initialize_database(db_path) -> None:
    """DB 초기화 함수, 테이블이 존재하지 않으면 생성"""
    conn = create_connection(db_path)

    if conn is not None:
        create_table(conn)
        conn.close()
    else:
        print("Error: Cannot establish a database connection.")
