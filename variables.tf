variable "ssh-subnet" {
  type = string
  default = "0.0.0.0/0"
  description = "Allow SSH from these addresses"
}