variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "container_app_name" {
  description = "Container App name"
  type        = string
}

variable "environment_name" {
  description = "Container App Environment name"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace customer ID"
  type        = string
}

variable "log_analytics_workspace_key" {
  description = "Log Analytics workspace shared key"
  type        = string
  sensitive   = true
}

variable "container_image" {
  description = "Container image"
  type        = string
}

variable "registry_server" {
  description = "Container registry server"
  type        = string
}

variable "registry_username" {
  description = "Container registry username"
  type        = string
  sensitive   = true
}

variable "registry_password" {
  description = "Container registry password"
  type        = string
  sensitive   = true
}

variable "environment_variables" {
  description = "Environment variables"
  type        = map(string)
  default     = {}
}

variable "key_vault_id" {
  description = "Key Vault ID"
  type        = string
}