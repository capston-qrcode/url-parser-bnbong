# 외부 피싱 Dataset 구조

## 한국인터넷진흥원_피싱사이트 URL_20221130.csv
| 항목명        | 항목명 (영문명) | 항목 설명    | 데이터타입        |
|---------------|----------------|-------------|--------------|
| 날짜          | DATE           | 탐지날짜    | VARCHAR |
| 홈페이지주소  | URL            | 피싱사이트 URL | VARCHAR |

## balanced_urls.csv
| 항목명          | 항목명 (영문명) | 항목 설명           | 데이터타입 |
|-----------------|-----------|---------------------|------------|
| 홈페이지주소    | url       | 분석된 웹사이트 URL   | VARCHAR    |
| 라벨           | label     | 사이트의 유형 (benign 또는 phishing) | VARCHAR    |
| 결과           | result    | 탐지 결과 (0: 비정상 아님, 1: 피싱 의심) | INTEGER    |

## phishing_and_benign_websites.csv
| 항목명      | 항목명 (영문명) | 항목 설명                        | 데이터타입 |
|----------|-----------|------------------------------|------------|
| 홈페이지주소목록 | URLs       | 분석된 웹사이트 URL 목록              | VARCHAR    |
| 라벨           | Label     | 사이트의 유형 (Benign 또는 Phishing) | VARCHAR    |

## urlset.csv
| 항목명           | 항목명 (영문명) | 항목 설명                                                   | 데이터타입 |
|------------------|-----------------|-------------------------------------------------------------|------------|
| 도메인            | DOMAIN          | 분석된 웹사이트 도메인 URL                                   | VARCHAR    |
| 순위              | RANKING         | 웹사이트의 글로벌 순위                                       | INTEGER    |
| MLD 결과          | MLD_RES         | MLD 모델의 탐지 결과 (1: 피싱, 0: 정상)                      | FLOAT      |
| MLD PS 결과       | MLD_PS_RES      | MLD PS 모델의 탐지 결과 (1: 피싱, 0: 정상)                   | FLOAT      |
| 카드 제거         | CARD_REM        | 웹사이트에서 탐지된 카드 제거의 횟수                         | INTEGER    |
| 비율 R 제거       | RATIO_RREM      | R 제거의 비율                                                | FLOAT      |
| 비율 A 제거       | RATIO_AREM      | A 제거의 비율                                                | FLOAT      |
| 자카드 RR        | JACCARD_RR      | RR 자카드 유사도                                             | FLOAT      |
| 자카드 RA        | JACCARD_RA      | RA 자카드 유사도                                             | FLOAT      |
| 자카드 AR        | JACCARD_AR      | AR 자카드 유사도                                             | FLOAT      |
| 자카드 AA        | JACCARD_AA      | AA 자카드 유사도                                             | FLOAT      |
| 자카드 ARrd      | JACCARD_ARRD    | ARrd 자카드 유사도                                           | FLOAT      |
| 자카드 ARrem     | JACCARD_ARREM   | ARrem 자카드 유사도                                          | FLOAT      |
| 라벨             | LABEL           | 탐지된 웹사이트의 유형 (1: 피싱, 0: 정상)                    | FLOAT      |

## Webpages_Classification_test_data.csv & Webpages_Classification_train_data.csv
> 사용 불확실

| 항목명          | 항목명 (영문명) | 항목 설명                                                       | 데이터타입 |
|-----------------|-----------------|-----------------------------------------------------------------|------------|
| URL             | URL             | 분석된 웹사이트 URL                                               | VARCHAR    |
| URL 길이        | URL_LEN         | URL의 길이                                                        | INTEGER    |
| IP 주소         | IP_ADD          | 웹사이트의 IP 주소                                                 | VARCHAR    |
| 지리적 위치     | GEO_LOC         | 웹사이트의 지리적 위치                                              | VARCHAR    |
| 최상위 도메인    | TLD             | 웹사이트의 최상위 도메인                                            | VARCHAR    |
| WHOIS 정보      | WHO_IS          | 웹사이트의 WHOIS 정보                                               | VARCHAR    |
| HTTPS 사용      | HTTPS           | HTTPS 프로토콜 사용 여부                                            | VARCHAR    |
| 자바스크립트 길이 | JS_LEN          | 페이지의 자바스크립트 코드 길이 (KB 단위)                           | FLOAT      |
| 자바스크립트 난독화 길이 | JS_OBF_LEN     | 난독화된 자바스크립트 코드의 길이 (KB 단위)                        | FLOAT      |
| 콘텐츠          | CONTENT         | 페이지의 텍스트 콘텐츠                                              | TEXT       |
| 라벨            | LABEL           | 탐지된 웹사이트의 유형 (good: 정상, phishing: 피싱)                  | VARCHAR    |

