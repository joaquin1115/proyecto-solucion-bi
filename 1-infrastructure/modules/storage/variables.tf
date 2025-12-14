variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "storage_account_name" {
  description = "Storage account name"
  type        = string
}

variable "object_id" {
  description = "The object ID of the principal (user, group, or service principal) to grant data access."
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault ID to store secrets"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for private endpoint"
  type        = string
}

variable "private_dns_zone_blob" {
  description = "Private DNS Zone ID for blob storage"
  type        = string
}

variable "private_dns_zone_dfs" {
  description = "Private DNS Zone ID for dfs storage"
  type        = string
}