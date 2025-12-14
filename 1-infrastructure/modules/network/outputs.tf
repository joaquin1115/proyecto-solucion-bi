output "vnet_id" {
  description = "The ID of the virtual network."
  value       = azurerm_virtual_network.main.id
}

output "vnet_name" {
  description = "The name of the virtual network."
  value       = azurerm_virtual_network.main.name
}

output "storage_subnet_id" {
  description = "The ID of the storage subnet."
  value       = azurerm_subnet.storage.id
}

output "postgresql_subnet_id" {
  description = "The ID of the postgresql subnet."
  value       = azurerm_subnet.postgresql.id
}

output "containerapp_infra_subnet_id" {
  description = "The ID of the containerapp infra subnet."
  value       = azurerm_subnet.containerapp_infra.id
}

output "containerapp_subnet_id" {
  description = "The ID of the containerapp subnet."
  value       = azurerm_subnet.containerapp.id
}

output "firewall_subnet_id" {
  description = "The ID of the firewall subnet."
  value       = azurerm_subnet.firewall.id
}

output "private_dns_zone_blob_id" {
  description = "The ID of the private DNS zone for blob storage."
  value       = azurerm_private_dns_zone.blob.id
}

output "private_dns_zone_dfs_id" {
  description = "The ID of the private DNS zone for dfs storage."
  value       = azurerm_private_dns_zone.dfs.id
}

output "private_dns_zone_postgres_id" {
  description = "The ID of the private DNS zone for PostgreSQL."
  value       = azurerm_private_dns_zone.postgres.id
}

output "private_dns_zone_acr_id" {
  description = "The ID of the private DNS zone for Azure Container Registry."
  value       = azurerm_private_dns_zone.acr.id
}