location                     = "westus3"
resource_group_name          = "rg-demo-dashboard"
network_resource_group_name  = "rg-demo-red"
alerts_resource_group_name   = "rg-demo-alerts"
project_name                 = "demo-dashboard"

# Network
vnet_address_space = ["10.0.0.0/16"]

subnet_prefixes = {
  containerapp       = "10.0.1.0/24"
  containerapp_infra = "10.0.8.0/23"
  postgresql         = "10.0.2.0/24"
  databricks_public  = "10.0.3.0/24"
  databricks_private = "10.0.4.0/24"
  storage            = "10.0.5.0/24"
  firewall           = "10.0.6.0/24"
  keyvault           = "10.0.7.0/24"
}

# Key Vault
key_vault_name = "kv-demo-dashboard"

# Storage
storage_account_name = "stdemodatalake576"

# PostgreSQL
postgresql_server_name    = "pg-demo-dashboard-001"
postgresql_location       = "westus3"
postgresql_admin_username = "adminuser"
postgresql_admin_password = "SecurePass123!"
postgresql_databases      = ["data_oro_practitioner", "data_oro_ci"]

# Databricks
databricks_workspace_name = "dbw-demo-dashboard"
databricks_managed_rg_name = "rg-demo-dashboard-db-managed"

# Container Registry
container_registry_name = "acrdemodashboard"

# Log Analytics
log_analytics_workspace_name = "law-demo-dashboard"

# Container App
container_app_name            = "demo-backend-api"
container_app_environment_name = "managedEnvironment-vnet"
container_app_image           = "acrdemodashboard.azurecr.io/demo-backend:v1"

# Static Web App
static_web_app_name     = "demo-dashboard-frontend-001"
static_web_app_location = "centralus"

# Firewall
firewall_name           = "fw-demo-dashboard"
firewall_policy_name    = "policy-demo-firewall"
firewall_public_ip_name = "pip-firewall"

# Route Table
route_table_name = "rt-firewall"

# Backup Vault
backup_vault_name = "rg-demo-dashboard-backup"

# Alerts
alert_email = "joaquin14142@gmail.com"
action_group_name = "ag-demo-dashboard-alerts"
action_group_short_name = "demodash"
environment = "dev"