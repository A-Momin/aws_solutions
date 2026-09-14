I will create a new file, vpc_peering_setup.tf, which includes the resources for the VPCs (as placeholders), the peering request and acceptance, and the necessary route table updates.
Since managing cross-account resources often involves using different AWS providers within the same Terraform configuration (one for Account A/Requester, one for Account B/Accepter), I'm providing a comprehensive example below.
I'll assume the following for this example:

-   **Account A (Requester)**: Where the Security Group from cross_account_sg.tf lives.
-   **Account B (Accepter)**: The peer account where the other Security Group lives.
-   **VPC A CIDR**: 10.10.0.0/16
-   **VPC B CIDR**: 10.20.0.0/16

I am creating a file named vpc_peering_setup.tf that demonstrates the full connection setup.

This file provides the framework for cross-account VPC peering. The critical components are:
The aws_vpc_peering_connection request, which uses peer_owner_id.
The aws_vpc_peering_connection_accepter (commented out, as it requires a different provider configuration).
The aws_route resources in both accounts that direct traffic to the peer network via the newly established peering connection.
This setup, combined with the Security Group configuration in cross_account_sg.tf, completes the network setup for cross-account communication! Let me know if you need help structuring your provider blocks to handle the two different AWS accounts.

```ini
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

```

---

The main difference is that we can define both VPCs and all the necessary components (VPCs, route tables, and the connection) in one file, and AWS automatically accepts the peering request.
I have updated the vpc_peering_setup.tf file to demonstrate a complete, self-contained same-account VPC peering configuration.

Changes Made:

Defined VPC B: Added aws_vpc.vpc_b and aws_route_table.rt_b directly.
Removed Mocks: Eliminated the locals block containing peer_vpc_id, peer_owner_id, and peer_route_table_id.
Simplified Peering Request: The aws_vpc_peering_connection.peer_request now references aws_vpc.vpc_b.id and no longer requires peer_owner_id. The acceptance resource is removed as it's automatic.
Completed Route Updates: The route for VPC B back to VPC A is now fully defined and active.
Here is the updated configuration:

This configuration ensures that both VPC A and VPC B have the necessary routes to communicate with each other, fulfilling the routing requirement. If you combine this with the Security Group rule we discussed earlier, you will have both the necessary routing and the necessary firewall filtering for secure cross-VPC communication.

```ini
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
  tags = { Name = "VPC-A-Requester" }
}

resource "aws_route_table" "rt_a" {
  vpc_id = aws_vpc.vpc_a.id
  tags = { Name = "RouteTable-VPC-A" }
}

# -----------------------------------------------------
# 2. Accepter VPC and Route Table (VPC B)
#    CIDR: 10.20.0.0/16
# -----------------------------------------------------
resource "aws_vpc" "vpc_b" {
  cidr_block = "10.20.0.0/16"
  tags = { Name = "VPC-B-Accepter" }
}

resource "aws_route_table" "rt_b" {
  vpc_id = aws_vpc.vpc_b.id
  tags = { Name = "RouteTable-VPC-B" }
}


# -----------------------------------------------------
# 3. VPC Peering Connection Request (Auto-Accepts)
# -----------------------------------------------------
resource "aws_vpc_peering_connection" "peer_request" {
  # Requester (Local) details
  vpc_id         = aws_vpc.vpc_a.id

  # Accepter (Local) details
  # No peer_owner_id is needed for same-account peering.
  peer_vpc_id    = aws_vpc.vpc_b.id

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
  route_table_id         = aws_route_table.rt_a.id
  destination_cidr_block = aws_vpc.vpc_b.cidr_block # 10.20.0.0/16
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
```

---
