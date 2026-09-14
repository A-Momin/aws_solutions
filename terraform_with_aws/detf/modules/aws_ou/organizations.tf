# 1. Initialize the AWS Organization
resource "aws_organizations_organization" "org" {
  aws_service_access_principals = [
    "cloudtrail.amazonaws.com",
    "config.amazonaws.com",
  ]
  # Enable all policy types for full governance
  enabled_policy_types = [
    "SERVICE_CONTROL_POLICY",
    "TAG_POLICY",
    "BACKUP_POLICY"
  ]
  feature_set = "ALL"
}

# 2. Create Organizational Units (OUs)
resource "aws_organizations_organizational_unit" "prod" {
  name      = "Production"
  parent_id = aws_organizations_organization.org.roots[0].id
}

resource "aws_organizations_organizational_unit" "dev" {
  name      = "Development"
  parent_id = aws_organizations_organization.org.roots[0].id
}

# 3. Create a Member Account within the Dev OU
# Note: AWS will send a confirmation email to the address below.
resource "aws_organizations_account" "dev_account" {
  name = "dev_account"
  # used Dynamic Email Alias to create unique email for testing
  email     = "dev_account+aminulmomin.ny@gmail.com"
  parent_id = aws_organizations_organizational_unit.dev.id

  # Allows IAM users in the management account to access this account via a role
  role_name = "OrganizationAccountAccessRole"
}

# 4. Define a Service Control Policy (SCP)
# This example denies all actions if they are NOT in the us-east-1 region.
resource "aws_organizations_policy" "region_restriction" {
  name        = "EnforceRegionRestriction"
  description = "Deny all actions outside of us-east-1"
  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyAllOutsideUSEast1"
        Effect = "Deny"
        NotAction = [
          "iam:*",
          "organizations:*",
          "route53:*",
          "budgets:*",
          "waf:*",
          "cloudfront:*",
          "globalaccelerator:*",
          "importexport:*",
          "support:*"
        ]
        Resource = "*"
        Condition = {
          StringNotEquals = {
            "aws:RequestedRegion" = ["us-east-1"]
          }
        }
      }
    ]
  })
}

# 5. Attach the Policy to the Production OU
resource "aws_organizations_policy_attachment" "prod_region_lock" {
  policy_id = aws_organizations_policy.region_restriction.id
  target_id = aws_organizations_organizational_unit.prod.id
}

