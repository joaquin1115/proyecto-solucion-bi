variable "location" {
  description = "Azure region"
  type        = string
}

variable "resource_group_name" {
  description = "Main resource group name"
  type        = string
}

variable "network_resource_group_name" {
  description = "Network resource group name"
  type        = string
}

variable "alerts_resource_group_name" {
  description = "Alerts resource group name"
  type        = string
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "common_tags" {
  description = "Etiquetas comunes para aplicar a los recursos."
  type        = map(string)
  default = {
    ManagedBy = "Terraform"
    Project   = "Demo"
  }
}

# Network
variable "vnet_address_space" {
  description = "Virtual network address space"
  type        = list(string)
}

variable "subnet_prefixes" {
  description = "Subnet address prefixes"
  type        = map(string)
}

# Key Vault
variable "key_vault_name" {
  description = "Key Vault name"
  type        = string
}

# Storage
variable "storage_account_name" {
  description = "Storage account name"
  type        = string
}

# PostgreSQL
variable "postgresql_server_name" {
  description = "PostgreSQL server name"
  type        = string
}

variable "postgresql_location" {
  description = "PostgreSQL location"
  type        = string
}

variable "postgresql_admin_username" {
  description = "PostgreSQL admin username"
  type        = string
  sensitive   = true
}

variable "postgresql_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "postgresql_databases" {
  description = "List of databases to create"
  type        = list(string)
}

# Databricks
variable "databricks_workspace_name" {
  description = "Databricks workspace name"
  type        = string
}

variable "databricks_managed_rg_name" {
  description = "Databricks managed resource group name"
  type        = string
}

# Container Registry
variable "container_registry_name" {
  description = "Container Registry name"
  type        = string
}

# Log Analytics
variable "log_analytics_workspace_name" {
  description = "Log Analytics workspace name"
  type        = string
}

# Container App
variable "container_app_name" {
  description = "Container App name"
  type        = string
}

variable "container_app_environment_name" {
  description = "Container App environment name"
  type        = string
}

variable "container_app_image" {
  description = "Container image"
  type        = string
}

# Static Web App
variable "static_web_app_name" {
  description = "Static Web App name"
  type        = string
}

variable "static_web_app_location" {
  description = "Static Web App location"
  type        = string
}

# Firewall
variable "firewall_name" {
  description = "Firewall name"
  type        = string
}

variable "firewall_policy_name" {
  description = "Firewall policy name"
  type        = string
}

variable "firewall_public_ip_name" {
  description = "Firewall public IP name"
  type        = string
}

# Route Table
variable "route_table_name" {
  description = "Route table name"
  type        = string
}

# Backup Vault
variable "backup_vault_name" {
  description = "Backup vault name"
  type        = string
}

# Alerts
variable "alert_email" {
  description = "Email for alert notifications"
  type        = string
}

variable "action_group_name" {
  description = "Name for the monitor action group."
  type        = string
}

variable "action_group_short_name" {
  description = "Short name for the monitor action group."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}