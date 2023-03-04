resource "aws_key_pair" "ssh" {
  key_name   = "ssh-cloudwatch"
  public_key = file("~/.ssh/id_rsa.pub")
}