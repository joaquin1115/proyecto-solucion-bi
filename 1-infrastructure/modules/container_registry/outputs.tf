output "registry_id" {
  description = "Container Registry ID"
  value       = azurerm_container_registry.main.id
}

output "login_server" {
  description = "Container Registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "admin_username" {
  description = "Container Registry admin username"
  value       = azurerm_container_registry.main.admin_username
  sensitive   = true
}

output "admin_password" {
  description = "Container Registry admin password"
  value       = azurerm_container_registry.main.admin_password
  sensitive   = true
}
