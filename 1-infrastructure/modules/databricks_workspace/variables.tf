variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "workspace_name" {
  description = "Databricks workspace name"
  type        = string
}

variable "managed_resource_group_name" {
  description = "Managed resource group name"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault ID"
  type        = string 
}