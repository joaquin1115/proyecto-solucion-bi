variable "resource_group_name" {
  description = "The name of the resource group in which to create the route table."
  type        = string
}

variable "location" {
  description = "The Azure region where the route table will be created."
  type        = string
}

variable "route_table_name" {
  description = "The name of the route table."
  type        = string
}

variable "routes" {
  description = "A map of routes to create in the route table."
  type = map(object({
    address_prefix         = string
    next_hop_type          = string
    next_hop_in_ip_address = optional(string)
  }))
  default = {}
}

variable "subnet_id_map" {
  description = "A map of subnet IDs to associate with the route table."
  type        = map(string)
  default     = {}
}