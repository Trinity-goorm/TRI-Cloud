cat << 'EOF' > install_node_exporter.sh
#!/bin/bash
# Docker 설치 (없는 경우)
if ! command -v docker &> /dev/null; then
  sudo dnf install -y docker
  sudo systemctl start docker
  sudo systemctl enable docker
  sudo usermod -aG docker $(whoami)
fi

# Node Exporter 실행
docker run -d --name node-exporter \
  --restart=always \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host
EOF

chmod +x install_node_exporter.sh
