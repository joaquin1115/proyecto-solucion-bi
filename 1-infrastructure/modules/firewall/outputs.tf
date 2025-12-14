output "firewall_id" {
  description = "Firewall ID"
  value       = azurerm_firewall.main.id
}

output "private_ip_address" {
  description = "Firewall private IP address"
  value       = azurerm_firewall.main.ip_configuration[0].private_ip_address
}

output "public_ip_address" {
  description = "Firewall public IP address"
  value       = azurerm_public_ip.firewall.ip_address
}