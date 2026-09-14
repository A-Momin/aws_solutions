output "kinesis_stream_name" {
  description = "Kinesis stream name"
  value       = aws_kinesis_stream.kp1_data_stream.name
}