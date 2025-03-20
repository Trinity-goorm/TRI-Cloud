# RDS 설정
RDS_CONFIG = {
    'host': 'trinity-db.cbke280aq027.ap-northeast-2.rds.amazonaws.com',
    'user': 'ec2-user',
    'password': 'profect1234*',
    'database': 'trinity-db',
    'port': 3306  # MySQL 기본 포트
}

# MongoDB 설정
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'user': 'ai_user',
    'password': 'profect1234*',
    'database': 'ai_db',
    'collection': 'recsys_data'
}

# 동기화 설정
SYNC_INTERVAL_MINUTES = 60  # 동기화 주기 (분)