resource "redpanda_serverless_cluster" "mas_cluster" {
  name           = "mas-cluster-${var.environment}"
  serverless_region = "ap-south-1"
}

output "redpanda_bootstrap_server" {
  value = redpanda_serverless_cluster.mas_cluster.bootstrap_servers
}
