variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "backup_vault_name" {
  description = "Backup vault name"
  type        = string
}

variable "storage_account_id" {
  description = "Storage account ID"
  type        = string
}

variable "storage_account_name" {
  description = "Storage account name"
  type        = string
}