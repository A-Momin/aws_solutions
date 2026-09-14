#!/bin/bash

launch_ec2(){
    AMI_ID=$1
    REGION="${AWS_DEFAULT_REGION}"
    INSTANCE_TYPE="t2.micro"
    KEY_PAIR_NAME="${AWS_DEFAULT_KEY_PAIR_NAME}"
    SECURITY_GROUP_ID="${AWS_DEFAULT_SG_ID}"
    SUBNET_ID="${AWS_DEFAULT_SUBNET_ID}"

    # Launch the EC2 instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --region "$REGION" \
        --image-id "$AMI_ID" \
        --instance-type "$INSTANCE_TYPE" \
        --key-name "$KEY_PAIR_NAME" \
        --security-group-ids "$SECURITY_GROUP_ID" \
        --subnet-id "$SUBNET_ID" \
        --query 'Instances[0].InstanceId' \
        --output text)

    sleep 20
    # Check if the instance was launched successfully
    if [ -n "$INSTANCE_ID" ]; then
        echo "EC2 instance with ID $INSTANCE_ID is now launching."
    else
        echo "Failed to launch the EC2 instance."
    fi
}


# aws ec2 stop-instances --instance-ids "i-064af12320b334d23"
# aws ec2 terminate-instances --instance-ids "i-064af12320b334d23"


# Get the Public IP address of the Running Instance
# aws ec2 describe-instances --instance-ids "i-064af12320b334d23" --query 'Reservations[].Instances[].PublicIpAddress' --output text
public_ip_address=$(aws ec2 describe-instances --instance-ids "i-064af12320b334d23" --query 'Reservations[].Instances[].PublicIpAddress' --output text)
# echo $public_ip_address

launch_by_id(){
    : ' Given the AWS EC2 inastance ID and Name, it will launch the instance
    Args:
        ($1): AWS EC2 inastance ID
        ($2): AWS EC2 inastance Name (Host) in your `~/config` file
    '
    local INSTANCE_ID
    INSTANCE_ID=${INSTANCE_ID:-$1}
    INSTANCE_ID=${INSTANCE_ID:-'i-06c960ba29b9803b3'}

    local INSTANCE_NAME
    INSTANCE_NAME=${INSTANCE_NAME:-$2}
    INSTANCE_NAME=${INSTANCE_NAME:-'ubuntu_server'}

    # Start the EC2 instance
    aws ec2 start-instances --instance-ids "$INSTANCE_ID"
    sleep 25

    local matching="Host $INSTANCE_NAME"
    local replacement="HostName $(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[].Instances[].PublicIpAddress' --output text)"

    # echo $INSTANCE_ID
    # echo $INSTANCE_NAME
    # echo $replacement

    # This will find the line containing "Host ubuntu_server", skip to the next line using n, and then delete that line using d.
    sed -i .bak "/$matching/{n; d;}" ~/config 
    # sed -i .bak "/Host ubuntu_server/a $replacement" ~/config # On Linux
    sed -i .bak -e "/$matching/a\\"$'\n'"$replacement" ~/config # on mac Only
}

## Adds inbound rule to ec2 instalce
add_inbound_rules(){

    local group_id=$(aws ec2 describe-instances --instance-ids ${AWS_UBUNTU_SERVER_INSTANCE_ID} --query 'Reservations[].Instances[].SecurityGroups[].GroupId' --output text)
    aws ec2 authorize-security-group-ingress --group-id $group_id --protocol tcp --port 8080 --cidr 0.0.0.0/0
}