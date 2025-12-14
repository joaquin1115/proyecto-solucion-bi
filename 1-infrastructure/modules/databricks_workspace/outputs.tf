output "workspace_id" {
  description = "Databricks workspace ID"
  value       = azurerm_databricks_workspace.main.id
}

output "workspace_url" {
  description = "Databricks workspace URL"
  value       = azurerm_databricks_workspace.main.workspace_url
}