import os

# RDS 설정
RDS_CONFIG = {
    'host': os.getenv('RDS_HOST', 'trinity-db.cbke280aq027.ap-northeast-2.rds.amazonaws.com'),
    'user': os.getenv('RDS_USER', 'ec2-user'),
    'password': os.getenv('RDS_PASSWORD', 'profect1234*'),
    'database': os.getenv('RDS_DATABASE', 'trinity-db'),
    'port': int(os.getenv('RDS_PORT', 3306))
}

# MongoDB 설정
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST', '10.0.193.101'),
    'port': int(os.getenv('MONGO_PORT', 27017)),
    'user': os.getenv('MONGO_USER', 'ai_app'),
    'password': os.getenv('MONGO_PASSWORD', 'profect1234*'),
    'database': os.getenv('MONGO_DATABASE', 'ai_database'),
    'collection': os.getenv('MONGO_COLLECTION', 'recsys_data')
}

SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', 60))