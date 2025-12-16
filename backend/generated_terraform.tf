

# providers.tf
provider "azurerm" {
  features {}
}
# variables.tf
variable "vm_name" {
  type        = string
  description = "Name of the virtual machine"
  default     = "vm"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
  default     = "rg"
}

variable "admin_username" {
  type        = string
  description = "Administrator username for the VM"
  default     = "azureuser"
  sensitive   = true
}

variable "admin_password" {
  type        = string
  description = "Administrator password for the VM (use environment variable or .tfvars file)"
  sensitive   = true
  validation {
    condition     = length(var.admin_password) >= 8 && can(regex("[A-Z]", var.admin_password)) && can(regex("[0-9]", var.admin_password))
    error_message = "Password must be at least 8 characters with at least one uppercase letter and one number."
  }
}

variable "allowed_admin_ips" {
  type        = list(string)
  description = "List of IP addresses allowed for SSH/RDP access. Use CIDR notation (e.g., ['203.0.113.0/32'])"
  default     = ["0.0.0.0/0"]
}

variable "enable_public_ip" {
  type        = bool
  description = "Whether to attach a public IP to the VM. Recommended: false for security, use bastion/VPN for access"
  default     = false
}
# outputs.tf
output "public_ip" {
  value       = var.enable_public_ip ? azurerm_public_ip.vm[0].ip_address : "Not allocated (private IP only)"
  description = "Public IP address of the VM (if enabled)"
}

output "private_ip" {
  value       = azurerm_network_interface.vm.private_ip_address
  description = "Private IP address of the VM"
}
# main.tf
resource "azurerm_resource_group" "vm" {
  name     = var.resource_group_name
  location = "eastus"
}

resource "azurerm_public_ip" "vm" {
  count               = var.enable_public_ip ? 1 : 0
  name                = "${var.vm_name}-pip"
  location            = azurerm_resource_group.vm.location
  resource_group_name = azurerm_resource_group.vm.name
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "vm" {
  name                = "${var.vm_name}-nic"
  location            = azurerm_resource_group.vm.location
  resource_group_name = azurerm_resource_group.vm.name

  ip_configuration {
    name                          = "primary"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = var.enable_public_ip ? azurerm_public_ip.vm[0].id : null
  }
}

  resource "azurerm_virtual_network" "main" {
  name                = "${var.vm_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.vm.location
  resource_group_name = azurerm_resource_group.vm.name
}

resource "azurerm_subnet" "internal" {
  name                 = "${var.vm_name}-subnet"
  resource_group_name  = azurerm_resource_group.vm.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Network Security Group for subnet
resource "azurerm_network_security_group" "main" {
  name                = "${var.vm_name}-nsg"
  location            = azurerm_resource_group.vm.location
  resource_group_name = azurerm_resource_group.vm.name

  security_rule {
    name                       = "AllowSSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefixes    = var.allowed_admin_ips
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowRDP"
    priority                   = 101
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefixes    = var.allowed_admin_ips
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAllOutbound"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    environment = "production"
    managed_by  = "terraform"
  }
}

# Associate NSG with subnet
resource "azurerm_subnet_network_security_group_association" "main" {
  subnet_id                 = azurerm_subnet.internal.id
  network_security_group_id = azurerm_network_security_group.main.id
}

resource "azurerm_windows_virtual_machine" "main" {
  name                = var.vm_name
  location            = azurerm_resource_group.vm.location
  resource_group_name = azurerm_resource_group.vm.name
  admin_username      = var.admin_username
  admin_password      = var.admin_password

  network_interface_ids           = [azurerm_network_interface.vm.id]
  size                            = "Standard_D2s_v3"
  encryption_at_host_enabled      = true
  patch_mode                      = "AutomaticByPlatform"

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "production"
    managed_by  = "terraform"
  }
}

locals {
  pricing_region = azurerm_resource_group.vm.location
}

output "pricing_region" {
  value = local.pricing_region
}