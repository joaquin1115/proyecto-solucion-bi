# Action Group for email notifications
resource "azurerm_monitor_action_group" "main" {
  name                = var.action_group_name
  resource_group_name = var.resource_group_name
  short_name          = var.action_group_short_name

  email_receiver {
    name          = "sendtoadmin"
    email_address = var.alert_email
  }
}

# Storage Account Alerts
resource "azurerm_monitor_metric_alert" "storage_errors" {
  name                = "alert-storage-errors-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.storage_account_id]
  description         = "Alert for when storage account transactions have errors."
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.Storage/storageAccounts"
    metric_name      = "Transactions" # Note: For ADLS Gen2, 'BlobTransactions' might be more appropriate
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5

    dimension {
      name     = "ResponseType"
      operator = "Include"
      values   = ["Error"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "storage_latency" {
  name                = "alert-storage-latency-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.storage_account_id]
  description         = "Alert for when storage account E2E latency is high."
  severity            = 3
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.Storage/storageAccounts"
    metric_name      = "SuccessE2ELatency"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 200
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "storage_egress" {
  name                = "alert-storage-egress-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.storage_account_id]
  description         = "Alert for when storage account egress is unusually high."
  severity            = 3
  frequency           = "PT30M"
  window_size         = "P1D"

  criteria {
    metric_namespace = "Microsoft.Storage/storageAccounts"
    metric_name      = "Egress"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 209715200 # 200 MB in bytes
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# Container App Alerts
resource "azurerm_monitor_metric_alert" "backend_5xx" {
  name                = "alert-backend-5xx-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.container_app_id]
  description         = "Alert for when the backend API returns 5xx server errors."
  severity            = 1
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "Requests"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5

    dimension {
      name     = "statusCodeCategory"
      operator = "Include"
      values   = ["5xx"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "backend_no_requests" {
  name                = "alert-backend-no-requests-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.container_app_id]
  description         = "Alert for when the backend API receives no requests, indicating a potential outage."
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "Requests"
    aggregation      = "Total"
    operator         = "LessThan"
    threshold        = 1
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "backend_cpu_high" {
  name                = "alert-backend-cpu-high-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.container_app_id]
  description         = "Alert for when the backend API CPU usage is high."
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "UsageNanoCores"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 70
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# PostgreSQL Alerts
resource "azurerm_monitor_metric_alert" "postgres_cpu_high" {
  name                = "alert-postgres-cpu-high-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.postgresql_server_id]
  description         = "Alert for when PostgreSQL CPU usage is high."
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.DBforPostgreSQL/flexibleServers"
    metric_name      = "cpu_percent"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 70
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "postgres_connections_high" {
  name                = "alert-postgres-connections-high-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.postgresql_server_id]
  description         = "Alert for when active connections to PostgreSQL are high."
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_namespace = "Microsoft.DBforPostgreSQL/flexibleServers"
    metric_name      = "active_connections"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "postgres_storage_low" {
  name                = "alert-postgres-storage-low-${var.environment}"
  resource_group_name = var.resource_group_name
  scopes              = [var.postgresql_server_id]
  description         = "Alert for when PostgreSQL storage is running low."
  severity            = 2
  frequency           = "PT30M"
  window_size         = "PT1H"

  criteria {
    metric_namespace = "Microsoft.DBforPostgreSQL/flexibleServers"
    metric_name      = "storage_percent"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}
