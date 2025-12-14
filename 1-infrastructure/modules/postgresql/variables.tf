variable "resource_group_name" {
  description = "Resource group name for the PostgreSQL server"
  type        = string
}

variable "private_endpoint_resource_group_name" {
  description = "Resource group name for the Private Endpoint. Should be the same as the VNet's RG."
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "server_name" {
  description = "PostgreSQL server name"
  type        = string
}

variable "admin_username" {
  description = "PostgreSQL admin username"
  type        = string
  sensitive   = true
}

variable "admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "databases" {
  description = "List of databases to create"
  type        = list(string)
}

variable "key_vault_id" {
  description = "Key Vault ID to store secrets"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for private endpoint"
  type        = string
}

variable "private_dns_zone_id" {
  description = "Private DNS Zone ID for PostgreSQL"
  type        = string
}