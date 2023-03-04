resource "aws_instance" "ubuntu" {
  ami           = data.aws_ami.ubuntu-arm.id
  instance_type = "t4g.micro"
  key_name      = aws_key_pair.ssh.key_name
  tags = {
    Name = "Ubuntu"
  }

  vpc_security_group_ids = [
    aws_security_group.ssh.id
  ]
}

output "ubuntu" {
  value = aws_instance.ubuntu.public_ip
}

resource "aws_instance" "alma" {
  ami           = data.aws_ami.alma-arm.id
  instance_type = "t4g.micro"
  key_name      = aws_key_pair.ssh.key_name
  tags = {
    Name = "Alma"
  }

  vpc_security_group_ids = [
    aws_security_group.ssh.id
  ]
}

output "alma" {
  value = aws_instance.alma.public_ip
}