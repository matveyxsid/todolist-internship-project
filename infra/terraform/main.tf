### VirtualBox TF (Win host)
terraform {
  required_providers {
    virtualbox = {
      source = "terra-farm/virtualbox"
      version = "0.2.2-alpha.1"
    }
  }
}

provider "virtualbox" {}

resource "virtualbox_vm" "k8s-nodes" {
  count  = 2
  name   = "k8s-node-${count.index + 1}"
  image  = "${path.module}/ubuntu2004.box"
  cpus   = "4"
  memory = "4 gib"

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Wi-Fi 6E AX210 160MHz"
  }
}

locals {
  vm_ips   = [for vm in virtualbox_vm.k8s-nodes : vm.network_adapter[0].ipv4_address]
  vm_names = [for vm in virtualbox_vm.k8s-nodes : vm.name]
}

output "vm_ips" {
  description = "IPs"
  value       = local.vm_ips
}

output "vm_names" {
  description = "VBox names"
  value       = local.vm_names
}

# to file
resource "local_file" "ips_json" {
  filename = "${path.module}/ips.json"
  content  = jsonencode({
    vm_ips   = local.vm_ips
    vm_names = local.vm_names
  })
}