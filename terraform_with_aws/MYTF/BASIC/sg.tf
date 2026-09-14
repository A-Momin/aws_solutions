resource "security_group" "dev_glue_sg" {
  name        = "dev-glue-sg"
  description = "Security group for Dev Glue"
  vpc_id      = aws_vpc.dev_glue_vpc.id

  # Ingress rules
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = "0.0.0.0/0"
    description = "Allow HTTPS traffic from VPC"
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = "0.0.0.0/0"
    description = "Allow SSH traffic from VPC"
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true # 👈 Self-reference here
    description = "Allow all TCP traffic from within the same SG"
  }

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [security_group.dev_glue_sg.id]
    description     = "Allow TCP 8000 from same SG"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --------------------------------------------------  
# VPC Peering Across AWS Accounts
# --------------------------------------------------  

#######################################################
# ASSUMPTIONS & PROVIDER SETUP
# This configuration assumes you have configured two 
# distinct AWS provider blocks in your main config file 
# or use roles/profiles to switch context for different 
# resource blocks.
#######################################################

# -----------------------------------------------------
# 1. Requester VPC and Route Table (Account A)
# -----------------------------------------------------
resource "aws_vpc" "vpc_a" {
  cidr_block = "10.10.0.0/16"
  tags       = { Name = "Requester-VPC-A" }
}

resource "aws_route_table" "rt_a" {
  vpc_id = aws_vpc.vpc_a.id
  tags   = { Name = "Requester-Route-Table" }
}

# -----------------------------------------------------
# 2. Accepter VPC Details (MOCK/DATA SOURCE - Account B)
# -----------------------------------------------------
# In a real-world scenario, you would likely use a 
# separate tfstate or a data block to retrieve the 
# remote VPC ID, Account ID, and Route Table ID.

# --- MOCK PLACEHOLDERS FOR DEMO ---
locals {
  peer_vpc_id         = "vpc-0abc123def4567890" # Peer Account VPC ID
  peer_owner_id       = "111122223333"          # Peer AWS Account ID
  peer_route_table_id = "rtb-0fedcba9876543210" # Peer Account Route Table ID
}

# -----------------------------------------------------
# 3. VPC Peering Connection Request (Account A)
# -----------------------------------------------------
resource "aws_vpc_peering_connection" "peer_request" {
  # Requester (Local) details
  vpc_id = aws_vpc.vpc_a.id

  # Accepter (Remote) details
  peer_vpc_id   = local.peer_vpc_id
  peer_owner_id = local.peer_owner_id

  # Required for cross-region peering, optional otherwise
  # auto_accept_config {
  #   auto_accept = true
  # }

  tags = {
    Name = "VPC-A-to-VPC-B-Peering"
  }
}

# -----------------------------------------------------
# 4. VPC Peering Connection Accepter (Account B)
# -----------------------------------------------------
# NOTE: This resource requires execution under the 
# credentials/provider for Account B. 
/*
resource "aws_vpc_peering_connection_accepter" "peer_accept" {
  provider = aws.account_b # Assuming 'account_b' provider exists
  
  vpc_peering_connection_id = aws_vpc_peering_connection.peer_request.id
  
  auto_accept = true

  tags = {
    Name = "VPC-B-Acceptance"
  }
}
*/

# -----------------------------------------------------
# 5. Route Table Updates (Requester - Account A)
# -----------------------------------------------------
# Route traffic destined for VPC B's CIDR (10.20.0.0/16) 
# through the peering connection.
resource "aws_route" "route_a_to_b" {
  route_table_id            = aws_route_table.rt_a.id
  destination_cidr_block    = "10.20.0.0/16" # CIDR of Peer VPC
  vpc_peering_connection_id = aws_vpc_peering_connection.peer_request.id
}

# -----------------------------------------------------
# 6. Route Table Updates (Accepter - Account B)
# -----------------------------------------------------
# NOTE: This resource requires execution under the 
# credentials/provider for Account B.

/*
resource "aws_route" "route_b_to_a" {
  provider = aws.account_b # Assuming 'account_b' provider exists

  route_table_id            = local.peer_route_table_id # RT in Peer VPC
  destination_cidr_block    = "10.10.0.0/16" # CIDR of Requester VPC
  vpc_peering_connection_id = aws_vpc_peering_connection_accepter.peer_accept.id
}
*/


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

#######################################################
# VPC PEERING SETUP: SAME AWS ACCOUNT
# This configuration creates two VPCs and establishes 
# a full-mesh peering connection between them, including 
# required route table updates for bidirectional traffic.
#######################################################

# -----------------------------------------------------
# 1. Requester VPC and Route Table (VPC A)
#    CIDR: 10.10.0.0/16
# -----------------------------------------------------
resource "aws_vpc" "vpc_a" {
  cidr_block = "10.10.0.0/16"
  tags       = { Name = "VPC-A-Requester" }
}

resource "aws_route_table" "rt_a" {
  vpc_id = aws_vpc.vpc_a.id
  tags   = { Name = "RouteTable-VPC-A" }
}

# -----------------------------------------------------
# 2. Accepter VPC and Route Table (VPC B)
#    CIDR: 10.20.0.0/16
# -----------------------------------------------------
resource "aws_vpc" "vpc_b" {
  cidr_block = "10.20.0.0/16"
  tags       = { Name = "VPC-B-Accepter" }
}

resource "aws_route_table" "rt_b" {
  vpc_id = aws_vpc.vpc_b.id
  tags   = { Name = "RouteTable-VPC-B" }
}


# -----------------------------------------------------
# 3. VPC Peering Connection Request (Auto-Accepts)
# -----------------------------------------------------
resource "aws_vpc_peering_connection" "peer_request" {
  # Requester (Local) details
  vpc_id = aws_vpc.vpc_a.id

  # Accepter (Local) details
  # No peer_owner_id is needed for same-account peering.
  peer_vpc_id = aws_vpc.vpc_b.id

  # The request is automatically accepted by AWS in the same account
  # unless auto_accept is explicitly set to false.

  tags = {
    Name = "VPC-A-to-VPC-B-Same-Account"
  }
}

# -----------------------------------------------------
# 4. Route Table Update (VPC A -> VPC B)
# -----------------------------------------------------
# Route traffic destined for VPC B's CIDR (10.20.0.0/16) 
# through the peering connection.
resource "aws_route" "route_a_to_b" {
  route_table_id            = aws_route_table.rt_a.id
  destination_cidr_block    = aws_vpc.vpc_b.cidr_block # 10.20.0.0/16
  vpc_peering_connection_id = aws_vpc_peering_connection.peer_request.id
}

# -----------------------------------------------------
# 5. Route Table Update (VPC B -> VPC A)
# -----------------------------------------------------
# Route traffic destined for VPC A's CIDR (10.10.0.0/16) 
# through the peering connection.
resource "aws_route" "route_b_to_a" {
  route_table_id            = aws_route_table.rt_b.id
  destination_cidr_block    = aws_vpc.vpc_a.cidr_block # 10.10.0.0/16
  vpc_peering_connection_id = aws_vpc_peering_connection.peer_request.id
}




