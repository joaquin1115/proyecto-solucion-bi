# Wait for workspace to be fully provisioned before configuring it
resource "time_sleep" "wait_for_workspace" {
  create_duration = "60s"
}

# Create Databricks Token
resource "databricks_token" "main" {
  depends_on       = [time_sleep.wait_for_workspace]
  comment          = "Terraform generated token"
  lifetime_seconds = 7776000 # 90 days
}

# Create Databricks Cluster
resource "databricks_cluster" "main" {
  depends_on              = [time_sleep.wait_for_workspace]
  cluster_name            = var.cluster_name
  spark_version           = var.spark_version
  node_type_id            = var.node_type_id
  num_workers             = var.num_workers
  autotermination_minutes = var.autotermination_minutes

  spark_conf = {
    "fs.azure.account.key.${var.storage_account_name}.dfs.core.windows.net" = var.storage_account_key
  }

  custom_tags = var.custom_tags
}

# Store Databricks configuration in Key Vault
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