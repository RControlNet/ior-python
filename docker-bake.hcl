group "default" {
  targets = ["ior_baseimage"]
}


target "ior_baseimage"{
  platforms = [
    "linux/amd64",
    "linux/arm64",
    "linux/arm/v7"
  ]
}
