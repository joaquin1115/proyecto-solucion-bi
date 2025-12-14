variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "firewall_name" {
  description = "Firewall name"
  type        = string
}

variable "firewall_policy_name" {
  description = "Firewall policy name"
  type        = string
}

variable "public_ip_name" {
  description = "Public IP name"
  type        = string
}

variable "vnet_name" {
  description = "Virtual network name"
  type        = string
}

variable "firewall_subnet_id" {
  description = "Firewall subnet ID"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID"
  type        = string
}

variable "source_address_range" {
  description = "Source address range for firewall rules"
  type        = string
}
