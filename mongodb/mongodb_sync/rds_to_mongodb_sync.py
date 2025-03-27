import pymysql
import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine
import schedule
import time
import logging
import os
import numpy as np
from dotenv import load_dotenv
from bson import ObjectId
import sys
from config import RDS_CONFIG, MONGO_CONFIG, SYNC_INTERVAL_MINUTES
from queries import *  # 쿼리 파일 임포트

# .env 파일에서 환경 변수 로드 (선택사항)
load_dotenv()

# 로깅 설정
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'sync.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('rds_to_mongodb_sync')

# numpy 값을 Python 네이티브 타입으로 변환하는 함수
def convert_numpy_types(data):
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(v) for v in data]
    elif isinstance(data, np.integer):  # NumPy 정수형
        return int(data)
    elif isinstance(data, np.floating):  # NumPy 실수형
        return float(data)
    elif isinstance(data, np.ndarray):  # NumPy 배열
        return convert_numpy_types(data.tolist())
    elif isinstance(data, ObjectId):  # MongoDB ObjectId
        return str(data)
    else:
        return data

def sync_rds_to_mongodb():
    try:
        # RDS 연결 문자열 생성
        rds_password = os.getenv('RDS_PASSWORD', RDS_CONFIG['password'])
        rds_conn_string = f"mysql+pymysql://{RDS_CONFIG['user']}:{rds_password}@{RDS_CONFIG['host']}:{RDS_CONFIG['port']}/{RDS_CONFIG['database']}"

        # MongoDB 연결 문자열 생성
        mongo_password = os.getenv('MONGO_PASSWORD', MONGO_CONFIG['password'])
        mongo_conn_string = f"mongodb://{MONGO_CONFIG['user']}:{mongo_password}@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/{MONGO_CONFIG['database']}"

        logger.info("RDS 연결 시작")
        rds_engine = create_engine(rds_conn_string)

        logger.info("MongoDB 연결 시작")
        mongo_client = MongoClient(mongo_conn_string)
        mongo_db = mongo_client[MONGO_CONFIG['database']]

        # 레스토랑 데이터 동기화
        logger.info("레스토랑 데이터 동기화 시작")
        restaurant_df = pd.read_sql(RESTAURANT_QUERY, rds_engine)
        logger.info(f"RDS에서 {len(restaurant_df)} 개의 레스토랑 레코드 가져옴")

        # 레스토랑 컬렉션 접근
        restaurant_collection = mongo_db['restaurants']
        restaurant_collection.delete_many({})

        if not restaurant_df.empty:
            restaurant_records = [convert_numpy_types(record) for record in restaurant_df.to_dict('records')]
            restaurant_collection.insert_many(restaurant_records)
            logger.info(f"MongoDB에 {len(restaurant_records)}개 레스토랑 레코드 삽입 완료")

        # 사용자 데이터 동기화
        logger.info("사용자 데이터 동기화 시작")
        user_df = pd.read_sql(USER_QUERY, rds_engine)
        logger.info(f"RDS에서 {len(user_df)} 개의 사용자 레코드 가져옴")

        # 사용자 컬렉션 접근
        user_collection = mongo_db['users']
        user_collection.delete_many({})

        if not user_df.empty:
            user_records = [convert_numpy_types(record) for record in user_df.to_dict('records')]
            user_collection.insert_many(user_records)
            logger.info(f"MongoDB에 {len(user_records)}개 사용자 레코드 삽입 완료")

        # 사용자 선호도 데이터 동기화
        logger.info("사용자 선호도 데이터 동기화 시작")
        user_preferences_df = pd.read_sql(USER_PREFERENCES_QUERY, rds_engine)
        logger.info(f"RDS에서 {len(user_preferences_df)} 개의 사용자 선호도 레코드 가져옴")

        # 사용자 카테고리 선호도 데이터 가져오기
        user_pref_categories_df = pd.read_sql(USER_PREFERENCE_CATEGORIES_QUERY, rds_engine)
        logger.info(f"RDS에서 {len(user_pref_categories_df)} 개의 사용자 카테고리 선호도 레코드 가져옴")

        # 사용자 선호도 컬렉션 접근
        user_preferences_collection = mongo_db['user_preferences']
        user_preferences_collection.delete_many({})

        if not user_preferences_df.empty:
            # 사용자 선호도와 카테고리 선호도 데이터 병합
            merged_preferences = []

            for _, pref_row in user_preferences_df.iterrows():
                user_id = pref_row['user_id']

                # 해당 사용자의 카테고리 선호도 찾기
                if not user_pref_categories_df.empty:
                    # 여기가 문제! NumPy 타입을 Python 네이티브 타입으로 변환
                    user_categories = [convert_numpy_types(cat) for cat in user_pref_categories_df[
                        user_pref_categories_df['user_preference_id'] == user_id
                    ]['category_id'].tolist()]
                else:
                    user_categories = []

                # 병합된 선호도 데이터 생성
                merged_pref = {
                    'user_id': convert_numpy_types(user_id),  # 개별 필드도 변환
                    'min_price': convert_numpy_types(pref_row['min_price']),  # 개별 필드도 변환
                    'max_price': convert_numpy_types(pref_row['max_price']),  # 개별 필드도 변환
                    'preferred_categories': user_categories
                }

                merged_preferences.append(merged_pref)  # 이미 변환된 객체

            # MongoDB에 병합된 선호도 데이터 삽입
            if merged_preferences:
                user_preferences_collection.insert_many(merged_preferences)
                logger.info(f"MongoDB에 {len(merged_preferences)}개 사용자 선호도 레코드 삽입 완료")

        # 좋아요 데이터
        logger.info("좋아요 데이터 동기화 시작")
        likes_df = pd.read_sql(LIKES_QUERY, rds_engine)
        logger.info(f"RDS에서 {len(likes_df)} 개의 좋아요 레코드 가져옴")

        likes_collection = mongo_db['likes']
        likes_collection.delete_many({})

        if not likes_df.empty:
            likes_records = [convert_numpy_types(record) for record in likes_df.to_dict('records')]
            likes_collection.insert_many(likes_records)
            logger.info(f"MongoDB에 {len(likes_records)}개 좋아요 레코드 삽입 완료")

        # 예약 데이터
        logger.info("예약 데이터 동기화 시작")
        reservations_df = pd.read_sql(RESERVATIONS_QUERY, rds_engine)
        logger.info(f"RDS에서 {len(reservations_df)} 개의 예약 레코드 가져옴")

        reservations_collection = mongo_db['reservations']
        reservations_collection.delete_many({})

        if not reservations_df.empty:
            # 날짜 필드 처리 (MongoDB에서 날짜 타입으로 저장)
            if 'reservation_date' in reservations_df.columns:
                reservations_df['reservation_date'] = pd.to_datetime(reservations_df['reservation_date'])

            reservations_records = [convert_numpy_types(record) for record in reservations_df.to_dict('records')]
            reservations_collection.insert_many(reservations_records)
            logger.info(f"MongoDB에 {len(reservations_records)}개 예약 레코드 삽입 완료")

        # 추천 시스템용 통합 데이터 (선택사항)
        logger.info("추천 시스템용 통합 데이터 생성 시작")
        try:
            # 기존 recsys_data 컬렉션 삭제
            recsys_collection = mongo_db[MONGO_CONFIG['collection']]
            recsys_collection.delete_many({})

            # 필요한 모든 데이터를 조합하여 추천 시스템용 데이터 생성
            # 예: 사용자별 예약 및 좋아요 정보를 조합
            all_users = user_df['user_id'].unique()
            recsys_data = []

            for user_id in all_users:
                user_info = user_df[user_df['user_id'] == user_id].iloc[0].to_dict() if not user_df.empty else {}

                # 사용자 선호도 추가
                user_prefs = None
                if merged_preferences:
                    user_prefs_list = [p for p in merged_preferences if p['user_id'] == user_id]
                    if user_prefs_list:
                        user_prefs = user_prefs_list[0]

                # 사용자의 예약 내역 추가
                user_reservations = []
                if not reservations_df.empty:
                    user_reservations = reservations_df[reservations_df['user_id'] == user_id].to_dict('records')

                # 사용자의 좋아요 내역 추가
                user_likes = []
                if not likes_df.empty:
                    user_likes = likes_df[likes_df['user_id'] == user_id].to_dict('records')

                # 통합 데이터 생성
                recsys_entry = convert_numpy_types({
                    'user_info': user_info,
                    'preferences': user_prefs,
                    'reservations': user_reservations,
                    'likes': user_likes,
                    'updated_at': pd.Timestamp.now()
                })

                recsys_data.append(recsys_entry)

            # MongoDB에 저장
            if recsys_data:
                recsys_collection.insert_many(recsys_data)
                logger.info(f"MongoDB에 {len(recsys_data)}개 추천 시스템 레코드 삽입 완료")

        except Exception as e:
            logger.error(f"추천 시스템 데이터 생성 중 오류: {str(e)}")

        logger.info("데이터 동기화 완료")

    except Exception as e:
        logger.error(f"동기화 중 오류 발생: {str(e)}")

# 스케줄링
def main():
    logger.info("동기화 서비스 시작")

    # 초기 실행
    sync_rds_to_mongodb()

    # 주기적 실행 설정
    schedule.every(SYNC_INTERVAL_MINUTES).minutes.do(sync_rds_to_mongodb)

    # 무한 루프로 스케줄 실행
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()