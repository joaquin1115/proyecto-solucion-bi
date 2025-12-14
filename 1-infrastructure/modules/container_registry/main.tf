resource "azurerm_container_registry" "main" {
  name                = var.registry_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Premium"
  admin_enabled       = true
  public_network_access_enabled = false
}

# Private Endpoint
resource "azurerm_private_endpoint" "acr" {
  name                = "pe-acr"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "conn-acr"
    private_connection_resource_id = azurerm_container_registry.main.id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "zg-acr"
    private_dns_zone_ids = [var.private_dns_zone_id]
  }
}

# Store ACR credentials in Key Vault
resource "azurerm_key_vault_secret" "acr_password" {
  name         = "acr-password"
  value        = azurerm_container_registry.main.admin_password
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "acr_username" {
  name         = "acr-username"
  value        = azurerm_container_registry.main.admin_username
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "acr_server" {
  name         = "acr-server"
  value        = azurerm_container_registry.main.login_server
  key_vault_id = var.key_vault_id
}