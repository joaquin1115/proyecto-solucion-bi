variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "storage_account_id" {
  description = "Storage account ID"
  type        = string
}

variable "container_app_id" {
  description = "Container App ID"
  type        = string
}

variable "postgresql_server_id" {
  description = "PostgreSQL server ID"
  type        = string
}

variable "alert_email" {
  description = "Email address for alerts"
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
  description = "The deployment environment name (e.g., dev, prod) to append to alert names."
  type        = string
  default     = "dev"
}
