resource "azurerm_public_ip" "firewall" {
  name                = var.public_ip_name
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_firewall_policy" "main" {
  name                = var.firewall_policy_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
}

resource "azurerm_firewall_policy_rule_collection_group" "app_rules" {
  name               = "rcg-app-rules"
  firewall_policy_id = azurerm_firewall_policy.main.id
  priority           = 100

  application_rule_collection {
    name     = "rc-allow-azure"
    priority = 100
    action   = "Allow"

    rule {
      name = "AllowAzureServices"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "*.azure.com",
        "*.microsoft.com",
        "*.windows.net"
      ]
    }

    rule {
      name = "AllowDatabricks"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "*.databricks.net",
        "*.azuredatabricks.net"
      ]
    }

    rule {
      name = "AllowPackages"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "*.pypi.org",
        "*.npmjs.org",
        "*.github.com"
      ]
    }

    rule {
      name = "AllowContainerApps"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "*.azurecontainerapps.io"
      ]
    }

    rule {
      name = "AllowStaticWebApp"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = ["*"]
      destination_fqdns = [
        "*.azurestaticapps.net"
      ]
    }

    rule {
      name = "AllowBlobStorage"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "*.blob.core.windows.net",
        "*.dfs.core.windows.net"
      ]
    }

    rule {
      name = "AllowStorageADLS"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "*.blob.core.windows.net",
        "*.dfs.core.windows.net",
        "login.microsoftonline.com",
        "*.login.microsoftonline.com",
        "*.aadcdn.microsoftonline-p.com"
      ]
    }

    rule {
      name = "AllowAzureManagement"
      protocols {
        type = "Https"
        port = 443
      }
      source_addresses  = [var.source_address_range]
      destination_fqdns = [
        "management.azure.com"
      ]
    }
  }
}

resource "azurerm_firewall" "main" {
  name                = var.firewall_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = "AZFW_VNet"
  sku_tier            = "Standard"
  firewall_policy_id  = azurerm_firewall_policy.main.id

  ip_configuration {
    name                 = "fw-config"
    subnet_id            = var.firewall_subnet_id
    public_ip_address_id = azurerm_public_ip.firewall.id
  }
}