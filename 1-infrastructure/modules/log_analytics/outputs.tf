output "workspace_id" {
  description = "Log Analytics workspace ID"
  value       = azurerm_log_analytics_workspace.main.id
}

output "workspace_customer_id" {
  description = "Log Analytics workspace customer ID"
  value       = azurerm_log_analytics_workspace.main.workspace_id
}

output "workspace_shared_key" {
  description = "Log Analytics workspace shared key"
  value       = azurerm_log_analytics_workspace.main.primary_shared_key
  sensitive   = true
}