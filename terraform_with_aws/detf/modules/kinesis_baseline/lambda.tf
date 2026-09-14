resource "null_resource" "prepare_lfn_zip_package" {
  provisioner "local-exec" {
    command = <<-EOT
      mkdir -p ${path.module}/lfn_packages
      cp ${path.module}/nodejs/code/consumer.js ${path.module}/lfn_packages/
      cd ${path.module}
      cd -
      npm install
      cp -r ${path.module}/node_modules ${path.module}/lfn_packages/
    EOT
  }

  #   triggers = {
  #     always = timestamp()
  #   }
}


data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lfn_packages"
  output_path = "${path.module}/nodejs/lfn_packages.zip"
  depends_on  = [null_resource.prepare_lfn_zip_package] # ensures zip runs after prep
}

# The Lambda Function
resource "aws_lambda_function" "kp1_consumer" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "KP1Consumer"
  role          = aws_iam_role.kp1_consumer_role.arn
  handler       = "consumer.handler" # Adjusted based on file structure
  runtime       = "nodejs22.x"

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

# The Kinesis Trigger (Event Source Mapping)
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn                   = aws_kinesis_stream.kp1_data_stream.arn
  function_name                      = aws_lambda_function.kp1_consumer.arn
  starting_position                  = "TRIM_HORIZON"
  batch_size                         = 10
  maximum_batching_window_in_seconds = 10
  parallelization_factor             = 1
  #   tumbling_window_in_seconds         = 0 # The range is between 1 second up to 900 seconds. Only available for stream sources (DynamoDB and Kinesis).
}