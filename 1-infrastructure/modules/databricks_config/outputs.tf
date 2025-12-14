output "token" {
  description = "Databricks token"
  value       = databricks_token.main.token_value
  sensitive   = true
}

output "cluster_id" {
  description = "Databricks cluster ID"
  value       = databricks_cluster.main.id
}