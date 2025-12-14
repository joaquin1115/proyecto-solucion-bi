output "id" {
  description = "ID del grupo de recursos."
  value       = azurerm_resource_group.this.id
}

output "name" {
  description = "Nombre del grupo de recursos."
  value       = azurerm_resource_group.this.name
}
