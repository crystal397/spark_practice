from typing import List
from datetime import datetime

from pyspark import SparkContext, RDD
from pyspark.sql import SparkSession

if __name__ == "__main__":
    ss: SparkSession = SparkSession.builder\
        .master("local")\
        .appName("rdd ver")\
        .getOrCreate()

    sc: SparkContext = ss.sparkContext

    log_rdd: RDD[str] = sc.textFile("file:///{절대경로}/data/log.txt")

    # check count
    print(f"count of RDD ==> {log_rdd.count()}")

    # print each row
    log_rdd.foreach(lambda v:print(v))

    # a) map
    # a-1) log.txt 의 각 행을 List[str] 형태로 받아오기
    def parse_line(row: str):
        return row.strip().split(" | ")

    parsed_log_rdd: RDD[List[str]] = log_rdd.map(parse_line)
    #parsed_log_rdd.foreach(print)

    # b) filter
    # b-1) status code가 404인 log만 필터링
    def get_only_404(row: List[str]) -> bool:
        status_code = row[-1]
        return status_code == '404'

    rdd_404 = parsed_log_rdd.filter(get_only_404)
    #rdd_404.foreach(print)

    # b-2) status code가 정상인 경우(2xx)인 log만 필터링
    def get_only_2xx(row: List[str]) -> bool:
        status_code = row[-1]
        return status_code.startswith("2")

    rdd_normal = parsed_log_rdd.filter(get_only_2xx)
    #rdd_normal.foreach(print)

    # b-3) post 요청이고 /playbooks api인 log만 필터링
    def get_post_request_and_playbooks_api(row: List[str]):
        log = row[2].replace("\"", "")
        return log.startswith("POST") and "/playbooks" in log

    rdd_post_playbooks = parsed_log_rdd\
        .filter(get_post_request_and_playbooks_api)
    #get_post_request_and_playbooks_api.foreach(print)

    # c) reduce
    # c-1) API method (POST/GET/PUT/PATCH/DELETE) 별 개수 출력
    def extract_api_method(row: List[str]):
        log = row[2].replace("\"", "")
        api_method = log.split(" ")[0]
        return api_method, 1

    rdd_count_by_api_method = parsed_log_rdd.map(extract_api_method)\
        .reduceByKey(lambda c1, c2: c1 + c2).sortByKey()

    #rdd_count_by_api_method.foreach(print)

    # c-2) 분 단위 별 요청 횟수 출력
    def extract_hour_and_minute(row: List[str]) -> tuple[str, int]:
        timestamp = row[1].replace("[","").replace("]","")
        date_format = "%d/%b/%Y:%H:%M:%S"
        date_time_obj = datetime.strptime(timestamp, date_format)
        return f"{date_time_obj.hour}:{date_time_obj.minute}", 1

    rdd_count_by_hour_and_minute = parsed_log_rdd.map(extract_hour_and_minute)\
        .reduceByKey(lambda c1, c2: c1 + c2)\
        .sortByKey()

    #rdd_count_by_hour_and_minute.foreach(print)

    # d) group by
    # 모든 데이터를 익스큐터들끼리 교환
    # d-1) status code, api method 별 ip 리스트 출력
    def extract_cols(row: List[str]) -> tuple[str, str, str]:
        ip = row[0]
        status_code = row[-1]
        api_method = row[2].replace("\"", "").split(" ")[0]

        return status_code, api_method, ip

    result = parsed_log_rdd.map(extract_cols)\
        .map(lambda x: ((x[0], x[1]), x[2]))\
        .groupByKey().mapValues(list)

    #result.foreach(print)

    # reduceByKey 사용
    # 익스큐터들끼리 데이터를 교환하기 전에 한 익스큐터 내부에서 어느 정도 reduce 연산을 수행 후 다른 익스큐터들과 데이터 교환이 발생
    # 'ip1', 'ip2' -> 'ip1, ip2'
    # 성능이 더 좋음
    result2 = parsed_log_rdd.map(extract_cols) \
        .map(lambda x: ((x[0], x[1]), x[2]))\
        .reduceByKey(lambda i1, i2: f"{i1}, {i2}")\
        .map(lambda row: (row[0], row[1]).split(","))

    # result2.foreach(print)