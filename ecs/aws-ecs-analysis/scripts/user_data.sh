#!/bin/bash

# user_dat for ECS instances

set -euo pipefail

# # Variables (replace or templated)
# ecs_cluster_name="bookstore-cluster"
# aws_region="us-east-1"

# Install CloudWatch Agent
if command -v yum >/dev/null 2>&1; then
  yum install -y amazon-cloudwatch-agent htop
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y amazon-cloudwatch-agent htop
fi

cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<'EOF'
{
  "metrics": {
    "namespace": "ECS/Django",
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_idle","cpu_usage_iowait","cpu_usage_user","cpu_usage_system"],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": ["used_percent"],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "diskio": {
        "measurement": ["io_time"],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": ["mem_used_percent"],
        "metrics_collection_interval": 60
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/ecs/ecs-agent.log",
            "log_group_name": "/aws/ecs/agent",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/ecs/ecs-init.log",
            "log_group_name": "/aws/ecs/init",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# Start agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s || true

# Configure healthcheck script
cat > /usr/local/bin/ecs-health-check.sh <<'EOC'
#!/bin/bash
set -e
# Check ECS agent service
if systemctl is-active --quiet amazon-ecs-agent || systemctl is-active --quiet ecs; then
  :
else
  echo "ECS agent not active" >&2
  exit 1
fi
# Check docker
if systemctl is-active --quiet docker; then
  :
else
  echo "docker not active" >&2
  exit 1
fi
# Disk usage
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
  echo "Disk usage is above 90%" >&2
  exit 1
fi
echo "OK"
exit 0
EOC

chmod +x /usr/local/bin/ecs-health-check.sh

# Add cron job idempotently
( crontab -l 2>/dev/null | grep -Fv '/usr/local/bin/ecs-health-check.sh' || true; echo "*/5 * * * * /usr/local/bin/ecs-health-check.sh >> /var/log/health-check.log 2>&1" ) | crontab -

# # 1. Configure docker daemon (CRITICAL: ADD LOGGING DRIVER)
# cat > /etc/docker/daemon.json <<'EOF'
# {
#   "log-driver": "awslogs",
#   "log-opts": {
#     "awslogs-group": "/aws/ecs/containerinsights",
#     "awslogs-region": "${aws_region}",
#     "awslogs-stream-prefix": "ecs"
#   },
#   "storage-driver": "overlay2",
#   "max-concurrent-downloads": 10,
#   "max-concurrent-uploads": 5
# }
# EOF

# Configure docker daemon (MINIMAL CONFIG TO PREVENT CRASH)
cat > /etc/docker/daemon.json <<'EOF'
{
  "storage-driver": "overlay2"
}
EOF

# Restart Docker
if systemctl is-active --quiet docker; then
  systemctl restart docker || true
fi

# Register ECS cluster
if [ -f /etc/ecs/ecs.config ]; then
  grep -q "^ECS_CLUSTER=" /etc/ecs/ecs.config || echo "ECS_CLUSTER=${cluster_name}" >> /etc/ecs/ecs.config
else
  echo "ECS_CLUSTER=${cluster_name}" > /etc/ecs/ecs.config
fi

# Restart ECS agent
if systemctl list-unit-files | grep -q amazon-ecs-agent; then
  systemctl restart amazon-ecs-agent || true
elif systemctl list-unit-files | grep -q '^ecs.service'; then
  systemctl restart ecs || true
fi


if systemctl is-active --quiet docker; then
  systemctl restart docker || true
fi

sleep 30
echo "ECS instance setup completed successfully"
