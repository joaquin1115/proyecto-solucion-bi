output "workspace_id" {
  description = "Databricks workspace ID"
  value       = azurerm_databricks_workspace.main.id
}

output "workspace_url" {
  description = "Databricks workspace URL"
  value       = "https://${azurerm_databricks_workspace.main.workspace_url}"
}

output "token" {
  description = "Databricks token"
  value       = databricks_token.main.token_value
  sensitive   = true
}

output "cluster_id" {
  description = "Databricks cluster ID"
  value       = databricks_cluster.main.id
}