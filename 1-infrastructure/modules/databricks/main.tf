resource "azurerm_databricks_workspace" "main" {
  name                = var.workspace_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "standard"
  managed_resource_group_name = var.managed_resource_group_name
  public_network_access_enabled = true

  custom_parameters {
    no_public_ip        = false
    public_subnet_name  = var.public_subnet_name
    private_subnet_name = var.private_subnet_name
    virtual_network_id  = var.virtual_network_id
  }
}

# Wait for workspace to be fully provisioned
resource "time_sleep" "wait_for_workspace" {
  depends_on = [azurerm_databricks_workspace.main]
  create_duration = "60s"
}

# Create Databricks Token
resource "databricks_token" "main" {
  depends_on = [time_sleep.wait_for_workspace]
  comment    = "Terraform generated token"
  lifetime_seconds = 7776000 # 90 days
}

# Create Databricks Cluster
resource "databricks_cluster" "main" {
  depends_on = [time_sleep.wait_for_workspace]
  cluster_name = "cluster-bbva"
  spark_version = "15.4.x-scala2.12"
  node_type_id = "Standard_DS3_v2"
  num_workers = 0
  autotermination_minutes = 20
  
  spark_conf = {
    "fs.azure.account.key.${var.storage_account_name}.dfs.core.windows.net" = var.storage_account_key
  }

  custom_tags = {
    "ResourceClass" = "SingleNode"
  }

  spark_env_vars = {
    PYSPARK_PYTHON = "/databricks/python3/bin/python3"
  }
}

# Store Databricks configuration in Key Vault
resource "azurerm_key_vault_secret" "databricks_workspace_url" {
  name         = "databricks-workspace-url"
  value        = "https://${azurerm_databricks_workspace.main.workspace_url}"
  key_vault_id = var.key_vault_id
  
  depends_on = [azurerm_databricks_workspace.main]
}

resource "azurerm_key_vault_secret" "databricks_token" {
  name         = "databricks-token"
  value        = databricks_token.main.token_value
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "databricks_cluster_id" {
  name         = "databricks-cluster-id"
  value        = databricks_cluster.main.id
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "datalake_key" {
  name         = "datalake-key"
  value        = var.storage_account_key
  key_vault_id = var.key_vault_id
}