output "container_app_id" {
  description = "Container App ID"
  value       = azurerm_container_app.main.id
}

output "container_app_fqdn" {
  description = "Container App FQDN"
  value       = azurerm_container_app.main.ingress[0].fqdn
}

output "container_app_principal_id" {
  description = "Container App principal ID"
  value       = azurerm_container_app.main.identity[0].principal_id
}
