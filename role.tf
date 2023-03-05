resource "aws_iam_role" "ec2-cloudwatch" {
  name               = "ec2-cloudwatch"
  assume_role_policy = <<EOF
    { 
      "Version": "2012-10-17",
      "Statement": [ {
        "Action": "sts:AssumeRole",
        "Principal": { "Service": "ec2.amazonaws.com" },
        "Effect": "Allow",
        "Sid": ""
      } ]
    }
    EOF
}

resource "aws_iam_instance_profile" "ec2-cloudwatch" {
  name = "ec2-cloudwatch"
  role = aws_iam_role.ec2-cloudwatch.name
}

resource "aws_iam_policy" "cloudwatch" {
    name = "CloudWatch-PutMetric"
    policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [ {
        "Sid": "Stmt1",
        "Effect": "Allow",
        "Action": [ "cloudwatch:PutMetricData" ],
        "Resource": "*"
      } ]
    }
    EOF
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
    role = aws_iam_role.ec2-cloudwatch.name
    policy_arn = aws_iam_policy.cloudwatch.arn
}