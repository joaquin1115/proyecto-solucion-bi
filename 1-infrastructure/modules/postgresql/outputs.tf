output "server_id" {
  description = "PostgreSQL server ID"
  value       = azurerm_postgresql_flexible_server.main.id
}

output "server_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "database_ids" {
  description = "Database IDs"
  value       = { for k, v in azurerm_postgresql_flexible_server_database.databases : k => v.id }
}