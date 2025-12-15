# Data sources
data "azurerm_client_config" "current" {}

# Resource Groups (usando el módulo genérico)
module "rg_main" {
  source   = "./modules/resource_group"
  name     = var.resource_group_name
  location = var.location
  tags     = var.common_tags
}

module "rg_network" {
  source   = "./modules/resource_group"
  name     = var.network_resource_group_name
  location = var.location
  tags     = var.common_tags
}

module "rg_alerts" {
  source   = "./modules/resource_group"
  name     = var.alerts_resource_group_name
  location = var.location
  tags     = var.common_tags
}

# Modules
module "network" {
  source = "./modules/network"

  resource_group_name = module.rg_network.name
  location            = var.location
  vnet_address_space  = var.vnet_address_space
  subnet_prefixes     = var.subnet_prefixes
  project_name        = var.project_name
}

module "key_vault" {
  source = "./modules/key_vault"

  resource_group_name = module.rg_main.name
  location            = var.location
  key_vault_name      = var.key_vault_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  object_id           = data.azurerm_client_config.current.object_id
  
  depends_on = [module.network]
}

# Espera para la propagación de los permisos del Key Vault
resource "time_sleep" "wait_for_key_vault_propagation" {
  create_duration = "30s"

  depends_on = [module.key_vault]
}

module "storage" {
  source = "./modules/storage"

  resource_group_name    = module.rg_main.name
  location               = var.location
  storage_account_name   = var.storage_account_name
  object_id              = data.azurerm_client_config.current.object_id
  key_vault_id          = module.key_vault.key_vault_id
  subnet_id             = module.network.storage_subnet_id
  private_dns_zone_blob = module.network.private_dns_zone_blob_id
  private_dns_zone_dfs  = module.network.private_dns_zone_dfs_id

  depends_on = [time_sleep.wait_for_key_vault_propagation]
}

module "postgresql" {
  source = "./modules/postgresql"
  
  resource_group_name      = module.rg_main.name
  location                 = var.postgresql_location
  server_name              = var.postgresql_server_name
  admin_username           = var.postgresql_admin_username
  admin_password           = var.postgresql_admin_password
  databases                = var.postgresql_databases
  key_vault_id            = module.key_vault.key_vault_id
  subnet_id               = module.network.postgresql_subnet_id
  private_endpoint_resource_group_name = module.rg_network.name
  private_dns_zone_id     = module.network.private_dns_zone_postgres_id

  depends_on = [time_sleep.wait_for_key_vault_propagation]
}

module "databricks_workspace" {
  source = "./modules/databricks_workspace"

  resource_group_name         = module.rg_main.name
  location                    = var.location
  workspace_name              = var.databricks_workspace_name
  managed_resource_group_name = var.databricks_managed_rg_name
  key_vault_id                = module.key_vault.key_vault_id

  depends_on = [time_sleep.wait_for_key_vault_propagation]
}

module "databricks_config" {
  source = "./modules/databricks_config"

  workspace_url        = module.databricks_workspace.workspace_url
  storage_account_name = module.storage.storage_account_name
  storage_account_key  = module.storage.storage_account_key
  key_vault_id         = module.key_vault.key_vault_id
  cluster_name         = var.databricks_cluster_name
  spark_version        = var.databricks_spark_version
  node_type_id         = var.databricks_node_type_id
  num_workers          = var.databricks_num_workers
  autotermination_minutes = var.databricks_autotermination_minutes

  depends_on = [module.databricks_workspace]
}

module "container_registry" {
  source = "./modules/container_registry"

  resource_group_name  = module.rg_main.name
  location             = var.location
  registry_name        = var.container_registry_name
  key_vault_id        = module.key_vault.key_vault_id
  subnet_id           = module.network.storage_subnet_id
  private_dns_zone_id = module.network.private_dns_zone_acr_id

  depends_on = [time_sleep.wait_for_key_vault_propagation]
}

module "log_analytics" {
  source = "./modules/log_analytics"

  resource_group_name = module.rg_main.name
  location            = var.location
  workspace_name      = var.log_analytics_workspace_name
}

module "container_app" {
  source = "./modules/container_app"

  resource_group_name          = module.rg_main.name
  location                     = var.location
  container_app_name           = var.container_app_name
  environment_name             = var.container_app_environment_name
  subnet_id                    = module.network.containerapp_infra_subnet_id
  log_analytics_workspace_id   = module.log_analytics.workspace_id
  key_vault_id                 = module.key_vault.key_vault_id
  allowed_cors_origin          = "https://${module.static_web_app.default_host_name}"
  
  environment_variables = local.container_app_environment_variables

  depends_on = [module.container_registry, module.databricks_config, time_sleep.wait_for_key_vault_propagation]
}

module "static_web_app" {
  source = "./modules/static_web_app"

  resource_group_name = module.rg_main.name
  location            = var.static_web_app_location
  app_name            = var.static_web_app_name
}

module "firewall" {
  source = "./modules/firewall"

  resource_group_name      = module.rg_network.name
  location                 = var.location
  firewall_name            = var.firewall_name
  firewall_policy_name     = var.firewall_policy_name
  public_ip_name           = var.firewall_public_ip_name
  vnet_name                = module.network.vnet_name
  firewall_subnet_id       = module.network.firewall_subnet_id
  log_analytics_workspace_id = module.log_analytics.workspace_id
  source_address_range     = var.vnet_address_space[0]
}

module "route_table" {
  source = "./modules/route_table"

  resource_group_name        = module.rg_network.name
  location                   = var.location
  route_table_name           = var.route_table_name
  routes                     = local.routes_map
  subnet_id_map              = local.route_table_associated_subnet_map
}

module "backup_vault" {
  source = "./modules/backup_vault"

  resource_group_name   = module.rg_main.name
  location              = var.location
  backup_vault_name     = var.backup_vault_name
  storage_account_id    = module.storage.storage_account_id
  storage_account_name  = module.storage.storage_account_name
}

module "alerts" {
  source = "./modules/alerts"

  resource_group_name        = module.rg_alerts.name
  location                   = var.location
  storage_account_id         = module.storage.storage_account_id
  container_app_id           = module.container_app.container_app_id
  postgresql_server_id       = module.postgresql.server_id
  alert_email                = var.alert_email
  action_group_name          = var.action_group_name
  action_group_short_name    = var.action_group_short_name
  environment                = var.environment
}