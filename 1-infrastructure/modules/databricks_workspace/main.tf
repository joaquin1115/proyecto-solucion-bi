resource "azurerm_databricks_workspace" "main" {
  name                          = var.workspace_name
  resource_group_name           = var.resource_group_name
  location                      = var.location
  sku                           = "standard"
  managed_resource_group_name   = var.managed_resource_group_name
}

# Store Databricks workspace URL in Key Vault
resource "azurerm_key_vault_secret" "databricks_workspace_url" {
  name         = "databricks-workspace-url"
  value        = azurerm_databricks_workspace.main.workspace_url
  key_vault_id = var.key_vault_id

  depends_on = [azurerm_databricks_workspace.main]
}