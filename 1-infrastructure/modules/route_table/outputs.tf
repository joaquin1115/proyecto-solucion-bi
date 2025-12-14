output "route_table_id" {
  description = "Route table ID"
  value       = azurerm_route_table.main.id
}

output "route_table_name" {
  description = "Route table name"
  value       = azurerm_route_table.main.name
}