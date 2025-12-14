resource "azurerm_data_protection_backup_vault" "main" {
  name                = var.backup_vault_name
  resource_group_name = var.resource_group_name
  location            = var.location
  datastore_type      = "VaultStore"
  redundancy          = "GeoRedundant"

  identity {
    type = "SystemAssigned"
  }
}