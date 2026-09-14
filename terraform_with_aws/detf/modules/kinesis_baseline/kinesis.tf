# Define the Kinesis Stream
resource "aws_kinesis_stream" "kp1_data_stream" {
  name        = "KP1DataStream"
  shard_count = 2
  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}