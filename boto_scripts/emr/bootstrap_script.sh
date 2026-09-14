#!/bin/bash
# EMR Bootstrap Script - Install Additional Packages
# This script installs additional Python packages and system utilities

set -e

# Parse command line arguments
PACKAGES=""
PYTHON_VERSION="3"
INSTALL_JUPYTER_EXTENSIONS=false
INSTALL_MONITORING_TOOLS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --packages)
            PACKAGES="$2"
            shift 2
            ;;
        --python-version)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --jupyter-extensions)
            INSTALL_JUPYTER_EXTENSIONS=true
            shift
            ;;
        --monitoring-tools)
            INSTALL_MONITORING_TOOLS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Starting EMR bootstrap script..."
echo "Python version: $PYTHON_VERSION"
echo "Packages to install: $PACKAGES"

# Update system packages
echo "Updating system packages..."
sudo yum update -y

# Install system utilities
echo "Installing system utilities..."
sudo yum install -y \
    htop \
    tree \
    jq \
    git \
    wget \
    curl \
    unzip \
    vim \
    tmux

# Install Python packages
if [ ! -z "$PACKAGES" ]; then
    echo "Installing Python packages: $PACKAGES"
    
    # Convert comma-separated packages to space-separated
    PACKAGE_LIST=$(echo $PACKAGES | tr ',' ' ')
    
    # Install packages using pip
    if [ "$PYTHON_VERSION" = "3" ]; then
        sudo python3 -m pip install --upgrade pip
        sudo python3 -m pip install $PACKAGE_LIST
    else
        sudo python -m pip install --upgrade pip
        sudo python -m pip install $PACKAGE_LIST
    fi
fi

# Install common data science packages
echo "Installing common data science packages..."
if [ "$PYTHON_VERSION" = "3" ]; then
    sudo python3 -m pip install \
        pandas \
        numpy \
        scipy \
        scikit-learn \
        matplotlib \
        seaborn \
        plotly \
        boto3 \
        awscli \
        jupyter \
        jupyterlab \
        notebook
else
    sudo python -m pip install \
        pandas \
        numpy \
        scipy \
        scikit-learn \
        matplotlib \
        seaborn \
        plotly \
        boto3 \
        awscli \
        jupyter \
        jupyterlab \
        notebook
fi

# Install Jupyter extensions
if [ "$INSTALL_JUPYTER_EXTENSIONS" = true ]; then
    echo "Installing Jupyter extensions..."
    sudo python3 -m pip install \
        jupyterlab-git \
        jupyterlab-s3-browser \
        jupyterlab_widgets \
        ipywidgets
    
    # Enable extensions
    jupyter labextension install @jupyterlab/git
    jupyter serverextension enable --py jupyterlab_git
fi

# Install monitoring tools
if [ "$INSTALL_MONITORING_TOOLS" = true ]; then
    echo "Installing monitoring tools..."
    
    # Install CloudWatch agent
    wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
    sudo rpm -U ./amazon-cloudwatch-agent.rpm
    
    # Install Prometheus node exporter
    wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
    tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
    sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
    sudo useradd -rs /bin/false node_exporter
    
    # Create systemd service for node exporter
    sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable node_exporter
    sudo systemctl start node_exporter
fi

# Configure Spark for better performance
echo "Configuring Spark settings..."
sudo tee -a /etc/spark/conf/spark-defaults.conf > /dev/null <<EOF

# Custom Spark configurations added by bootstrap script
spark.sql.adaptive.enabled=true
spark.sql.adaptive.coalescePartitions.enabled=true
spark.sql.adaptive.skewJoin.enabled=true
spark.serializer=org.apache.spark.serializer.KryoSerializer
spark.sql.hive.metastorePartitionPruning=true
spark.dynamicAllocation.enabled=true
spark.dynamicAllocation.minExecutors=1
spark.dynamicAllocation.maxExecutors=10
spark.dynamicAllocation.initialExecutors=2
EOF

# Set up environment variables
echo "Setting up environment variables..."
sudo tee -a /etc/environment > /dev/null <<EOF
PYSPARK_PYTHON=/usr/bin/python3
PYSPARK_DRIVER_PYTHON=/usr/bin/python3
SPARK_HOME=/usr/lib/spark
HADOOP_HOME=/usr/lib/hadoop
HADOOP_CONF_DIR=/etc/hadoop/conf
HIVE_HOME=/usr/lib/hive
EOF

# Create useful aliases
echo "Creating useful aliases..."
sudo tee -a /etc/bashrc > /dev/null <<EOF

# EMR aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias spark-shell='spark-shell --conf spark.sql.adaptive.enabled=true'
alias pyspark='pyspark --conf spark.sql.adaptive.enabled=true'
alias hdfs-ls='hdfs dfs -ls'
alias hdfs-du='hdfs dfs -du -h'
alias yarn-apps='yarn application -list'
alias spark-history='spark-history-server start'
EOF

# Install additional Hadoop ecosystem tools
echo "Installing additional Hadoop ecosystem tools..."

# Install Apache Airflow (optional)
if command -v python3 &> /dev/null; then
    echo "Installing Apache Airflow..."
    sudo python3 -m pip install apache-airflow
fi

# Set up log rotation for application logs
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/emr-applications > /dev/null <<EOF
/var/log/spark/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}

/var/log/hadoop-yarn/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Create a startup script for custom services
echo "Creating startup script..."
sudo tee /usr/local/bin/emr-startup.sh > /dev/null <<'EOF'
#!/bin/bash
# EMR Custom Startup Script

echo "Running EMR custom startup script..."

# Start any custom services here
# Example: Start a custom monitoring service
# systemctl start custom-monitor

# Set up custom environment
export CUSTOM_EMR_ENV=true

echo "EMR custom startup script completed."
EOF

sudo chmod +x /usr/local/bin/emr-startup.sh

# Add startup script to rc.local
sudo tee -a /etc/rc.local > /dev/null <<EOF
# Run custom EMR startup script
/usr/local/bin/emr-startup.sh
EOF

sudo chmod +x /etc/rc.local

# Clean up
echo "Cleaning up..."
rm -f node_exporter-1.6.1.linux-amd64.tar.gz
rm -rf node_exporter-1.6.1.linux-amd64
rm -f amazon-cloudwatch-agent.rpm

echo "Bootstrap script completed successfully!"
echo "Installed packages: $PACKAGES"
echo "Python version: $PYTHON_VERSION"
echo "Jupyter extensions: $INSTALL_JUPYTER_EXTENSIONS"
echo "Monitoring tools: $INSTALL_MONITORING_TOOLS"