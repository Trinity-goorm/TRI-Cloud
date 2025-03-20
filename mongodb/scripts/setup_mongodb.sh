# scripts/setup_mongodb.sh 내용 작성
#!/bin/bash

echo "MongoDB 설치 시작..."

# 시스템 업데이트
sudo dnf update -y

# MongoDB 리포지토리 추가
sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo << EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF

# MongoDB 설치
sudo dnf install -y mongodb-org

# MongoDB 서비스 디렉토리 확인 및 생성
sudo mkdir -p /var/lib/mongo
sudo mkdir -p /var/log/mongodb
sudo chown -R mongod:mongod /var/lib/mongo
sudo chown -R mongod:mongod /var/log/mongodb

# MongoDB 설정 파일 수정
sudo cp /etc/mongod.conf /etc/mongod.conf.backup
sudo sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf
echo "security:
  authorization: enabled" | sudo tee -a /etc/mongod.conf

# MongoDB 서비스 시작 및 활성화
sudo systemctl start mongod
sudo systemctl enable mongod

echo "MongoDB 설치 완료!"