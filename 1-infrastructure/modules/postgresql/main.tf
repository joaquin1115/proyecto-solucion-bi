resource "azurerm_postgresql_flexible_server" "main" {
  name                   = var.server_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  administrator_login    = var.admin_username
  administrator_password = var.admin_password
  storage_mb             = 131072
  sku_name               = "GP_Standard_D2ds_v5"
  zone                   = "1"
  public_network_access_enabled = false
}

resource "azurerm_postgresql_flexible_server_database" "databases" {
  for_each  = toset(var.databases)
  name      = each.value
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Private Endpoint
resource "azurerm_private_endpoint" "postgresql" {
  name                = "pe-postgresql"
  location            = var.location
  resource_group_name = var.private_endpoint_resource_group_name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "conn-postgresql"
    private_connection_resource_id = azurerm_postgresql_flexible_server.main.id
    subresource_names              = ["postgresqlServer"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "zg-postgresql"
    private_dns_zone_ids = [var.private_dns_zone_id]
  }
}

# Store credentials in Key Vault
resource "azurerm_key_vault_secret" "db_host" {
  name         = "db-host"
  value        = azurerm_postgresql_flexible_server.main.fqdn
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "db_port" {
  name         = "db-port"
  value        = "5432"
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "db_user" {
  name         = "db-user"
  value        = var.admin_username
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  value        = var.admin_password
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "db_name_practitioner" {
  name         = "db-name-practitioner"
  value        = var.databases[0]
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "db_name_ci" {
  name         = "db-name-ci"
  value        = var.databases[1]
  key_vault_id = var.key_vault_id
}