# scripts/start_sync.sh 내용 작성
#!/bin/bash

cd ~/mongodb/mongodb_sync
source venv/bin/activate  # 가상환경 사용 시
nohup python rds_to_mongodb_sync.py > logs/nohup.out 2>&1 &
echo $! > sync.pid
echo "동기화 서비스 시작됨, PID: $(cat sync.pid)"