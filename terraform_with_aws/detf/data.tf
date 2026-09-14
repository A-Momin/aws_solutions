// Data resources needed by root module outputs and references
// This ensures data.aws_caller_identity.current is available at root module scope
// and fixes: "A data resource \"aws_caller_identity\" \"current\" has not been declared in the root module."

data "aws_caller_identity" "current" {}
