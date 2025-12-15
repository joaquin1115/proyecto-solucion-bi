variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
}

variable "location" {
  description = "The Azure region."
  type        = string
}

variable "container_app_name" {
  description = "The name of the Container App."
  type        = string
}

variable "environment_name" {
  description = "The name of the Container App Environment."
  type        = string
}

variable "subnet_id" {
  description = "The ID of the infrastructure subnet for the Container App Environment."
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics Workspace."
  type        = string
}

variable "environment_variables" {
  description = "A map of environment variables for the container."
  type        = map(string)
  default     = {}
}

variable "key_vault_id" {
  description = "The ID of the Key Vault to grant access to."
  type        = string
}

variable "allowed_cors_origin" {
  description = "The allowed origin for CORS."
  type        = string
}