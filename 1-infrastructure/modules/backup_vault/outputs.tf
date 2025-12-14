output "backup_vault_id" {
  description = "Backup vault ID"
  value       = azurerm_data_protection_backup_vault.main.id
}

output "backup_vault_name" {
  description = "Backup vault name"
  value       = azurerm_data_protection_backup_vault.main.name
}