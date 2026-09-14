#!/bin/bash
# User data script for Blue-Green deployment
# This script sets up the web server with environment-specific content

# Variables passed from Terraform
ENVIRONMENT="${environment}"
APP_VERSION="${app_version}"

# Update the system and install Apache
yum update -y
yum install -y httpd awscli

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Get instance metadata
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id -H "X-aws-ec2-metadata-token: $TOKEN")
AVAILABILITY_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone -H "X-aws-ec2-metadata-token: $TOKEN")
INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type -H "X-aws-ec2-metadata-token: $TOKEN")

# Set environment-specific colors and styling
if [ "$ENVIRONMENT" = "blue" ]; then
    BG_COLOR="#0066CC"
    TEXT_COLOR="#FFFFFF"
    ENV_DISPLAY="BLUE"
elif [ "$ENVIRONMENT" = "green" ]; then
    BG_COLOR="#00AA44"
    TEXT_COLOR="#FFFFFF"
    ENV_DISPLAY="GREEN"
else
    BG_COLOR="#666666"
    TEXT_COLOR="#FFFFFF"
    ENV_DISPLAY="UNKNOWN"
fi

# Create the main index.html
cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo App - $ENV_DISPLAY Environment</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, $BG_COLOR 0%, darken($BG_COLOR, 20%) 100%);
            color: $TEXT_COLOR;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .environment-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.2em;
            font-weight: bold;
            margin: 20px 0;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .info-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .info-card h3 {
            margin-top: 0;
            color: rgba(255, 255, 255, 0.9);
        }
        .info-card p {
            margin: 5px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .health-check {
            margin-top: 30px;
            padding: 15px;
            background: rgba(0, 255, 0, 0.2);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 0, 0.3);
        }
        .timestamp {
            margin-top: 20px;
            font-size: 0.8em;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Demo Application</h1>
        <div class="environment-badge">$ENV_DISPLAY Environment</div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>🏷️ Environment Info</h3>
                <p><strong>Environment:</strong> $ENVIRONMENT</p>
                <p><strong>Version:</strong> $APP_VERSION</p>
                <p><strong>Status:</strong> Active</p>
            </div>
            
            <div class="info-card">
                <h3>🖥️ Instance Details</h3>
                <p><strong>Instance ID:</strong> $INSTANCE_ID</p>
                <p><strong>Instance Type:</strong> $INSTANCE_TYPE</p>
                <p><strong>AZ:</strong> $AVAILABILITY_ZONE</p>
            </div>
        </div>
        
        <div class="health-check">
            <h3>✅ Health Check Status</h3>
            <p>Application is running and healthy</p>
            <p>All systems operational</p>
        </div>
        
        <div class="timestamp">
            <p>Last updated: $(date)</p>
            <p>Deployment time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")</p>
        </div>
    </div>
</body>
</html>
EOF

# Create a health check endpoint
cat > /var/www/html/health << EOF
{
    "status": "healthy",
    "environment": "$ENVIRONMENT",
    "version": "$APP_VERSION",
    "instance_id": "$INSTANCE_ID",
    "timestamp": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
}
EOF

# Create a version endpoint
cat > /var/www/html/version << EOF
{
    "version": "$APP_VERSION",
    "environment": "$ENVIRONMENT",
    "build_time": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")",
    "instance_id": "$INSTANCE_ID"
}
EOF

# Set proper permissions
chown -R apache:apache /var/www/html/
chmod -R 755 /var/www/html/

# Configure Apache for better performance
cat >> /etc/httpd/conf/httpd.conf << EOF

# Performance and security configurations
ServerTokens Prod
ServerSignature Off
KeepAlive On
MaxKeepAliveRequests 100
KeepAliveTimeout 15

# Enable compression
LoadModule deflate_module modules/mod_deflate.so
<Location />
    SetOutputFilter DEFLATE
    SetEnvIfNoCase Request_URI \
        \.(?:gif|jpe?g|png)$ no-gzip dont-vary
    SetEnvIfNoCase Request_URI \
        \.(?:exe|t?gz|zip|bz2|sit|rar)$ no-gzip dont-vary
</Location>

# Custom log format for ALB
LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\" %D" combined_with_time
CustomLog logs/access_log combined_with_time
EOF

# Install CloudWatch agent for monitoring
yum install -y amazon-cloudwatch-agent

# Create CloudWatch agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "metrics": {
        "namespace": "DemoApp/$ENV_DISPLAY",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "diskio": {
                "measurement": [
                    "io_time"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            }
        }
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/httpd/access_log",
                        "log_group_name": "/aws/ec2/demoapp/$ENVIRONMENT/httpd/access",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "file_path": "/var/log/httpd/error_log",
                        "log_group_name": "/aws/ec2/demoapp/$ENVIRONMENT/httpd/error",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Create a simple monitoring script
cat > /usr/local/bin/app-monitor.sh << 'EOF'
#!/bin/bash
# Simple application monitoring script

LOG_FILE="/var/log/app-monitor.log"
HEALTH_URL="http://localhost/health"

while true; do
    TIMESTAMP=$(date)
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "[$TIMESTAMP] Health check passed - HTTP $HTTP_STATUS" >> $LOG_FILE
    else
        echo "[$TIMESTAMP] Health check failed - HTTP $HTTP_STATUS" >> $LOG_FILE
        # Restart Apache if health check fails
        systemctl restart httpd
    fi
    
    sleep 30
done
EOF

chmod +x /usr/local/bin/app-monitor.sh

# Create systemd service for monitoring
cat > /etc/systemd/system/app-monitor.service << EOF
[Unit]
Description=Application Health Monitor
After=httpd.service

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/app-monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
systemctl daemon-reload
systemctl enable app-monitor
systemctl start app-monitor

# Restart Apache to apply all configurations
systemctl restart httpd

# Log deployment completion
echo "$(date): $ENVIRONMENT environment deployment completed successfully" >> /var/log/deployment.log
echo "Environment: $ENVIRONMENT" >> /var/log/deployment.log
echo "Version: $APP_VERSION" >> /var/log/deployment.log
echo "Instance ID: $INSTANCE_ID" >> /var/log/deployment.log