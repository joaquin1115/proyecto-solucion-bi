resource "azurerm_route_table" "main" {
  name                          = var.route_table_name
  location                      = var.location
  resource_group_name           = var.resource_group_name
}

resource "azurerm_route" "main" {
  for_each               = var.routes
  name                   = each.key
  resource_group_name    = azurerm_route_table.main.resource_group_name
  route_table_name       = azurerm_route_table.main.name
  address_prefix         = each.value.address_prefix
  next_hop_type          = each.value.next_hop_type
  next_hop_in_ip_address = each.value.next_hop_in_ip_address
}

resource "azurerm_subnet_route_table_association" "main" {
  for_each         = var.subnet_id_map
  subnet_id        = each.value
  route_table_id   = azurerm_route_table.main.id
}