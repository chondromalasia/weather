provider "aws" {
	region = "eu-central-1"
}

resource "aws_instance" "vps" {
	ami = "ami-07c27171ff332e277"
	instance_type = "t4g.micro"

	tags = {
		Name = "weather-vps"
	}
}
