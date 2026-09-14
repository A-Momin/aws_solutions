#!/bin/bash
#
# User data for ECS-Optimized AL2023 instances
#
set -euo pipefail

###############################################
# VARIABLES (provided by Terraform)
###############################################
cluster_name="${cluster_name}"

echo "Starting ECS AL2023 bootstrap..."

###############################################
# Confirm ECS-Optimized AMI
###############################################
if ! rpm -qa | grep -q "ecs-init"; then
  echo "ERROR: This is NOT an ECS-Optimized AMI" >&2
  exit 1
fi

###############################################
# Configure CloudWatch Agent (logs + metrics)
###############################################

mkdir -p /opt/aws/amazon-cloudwatch-agent/etc

cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<EOF
{
  "metrics": {
    "namespace": "ECS/Instance",
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_idle","cpu_usage_user","cpu_usage_system"],
        "metrics_collection_interval": 60
      },
      "mem": {
        "measurement": ["mem_used_percent"],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": ["used_percent"],
        "resources": ["*"],
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
            "log_group_name": "/ecs/agent",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/ecs/system",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -s || true


###############################################
# ECS Cluster Registration
###############################################

mkdir -p /etc/ecs
if ! grep -q "^ECS_CLUSTER=" /etc/ecs/ecs.config 2>/dev/null; then
  echo "ECS_CLUSTER=${cluster_name}" >> /etc/ecs/ecs.config
fi

echo "ECS_BACKEND_HOST=ecs.us-east-1.amazonaws.com" >> /etc/ecs/ecs.config || true

systemctl enable --now ecs || systemctl restart ecs || true


###############################################
# Health Check Script (containerd + ecs-agent)
###############################################
cat > /usr/local/bin/ecs-health-check.sh <<'EOS'
#!/bin/bash
set -e

# ECS agent health
if ! systemctl is-active --quiet ecs; then
  echo "ECS agent not running" >&2
  exit 1
fi

# containerd health
if ! systemctl is-active --quiet containerd; then
  echo "containerd not running" >&2
  exit 1
fi

# Root filesystem usage
USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$USAGE" -ge 90 ]; then
  echo "Disk usage above 90%" >&2
  exit 1
fi

echo "OK"
EOS

chmod +x /usr/local/bin/ecs-health-check.sh

###############################################
# Cronjob to log health
###############################################
( crontab -l 2>/dev/null | grep -Fv ecs-health-check.sh || true
  echo "*/5 * * * * /usr/local/bin/ecs-health-check.sh >> /var/log/ecs-health.log 2>&1"
) | crontab -


###############################################
# Final
###############################################
echo "ECS AL2023 bootstrap completed successfully."
