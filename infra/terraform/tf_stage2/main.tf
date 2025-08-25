terraform {
  required_providers {
    null  = { source = "hashicorp/null",  version = "~> 3.2" }
    local = { source = "hashicorp/local", version = "~> 2.5" }
  }
}

locals {
  artifacts_dir = "${path.module}/artifacts"
}

# scp first tf outputs
resource "null_resource" "fetch_ips" {
  provisioner "local-exec" {
    command = <<EOT
set -e
mkdir -p ${local.artifacts_dir}
scp -o StrictHostKeyChecking=no -i ${var.ssh_key} \
  ${var.win_user}@${var.win_host}:"${var.win_tf_dir}/ips.json" \
  ${local.artifacts_dir}/ips.json
EOT
  }
}

# read ips.json
data "local_file" "ips" {
  depends_on = [null_resource.fetch_ips]
  filename   = "${local.artifacts_dir}/ips.json"
}

# json parsing
locals {
  win_out      = jsondecode(data.local_file.ips.content)
  vm_ips  = local.win_out.vm_ips

  # splitting nodes
  masters = slice(local.vm_ips, 0, var.control_plane_count)
  workers = slice(local.vm_ips, var.control_plane_count, length(local.vm_ips))
}

# creating hosts.yaml
resource "local_file" "hosts_yaml" {
  depends_on = [data.local_file.ips]
  filename   = "${var.kubespray_dir}/inventory/mycluster/hosts.yaml"
  content = templatefile("${path.module}/templates/hosts.tmpl.yaml", {
    masters                        = local.masters
    workers                        = local.workers
    ansible_user                   = var.ansible_user
    ansible_ssh_private_key_file   = var.ansible_ssh_private_key_file
  })
}

# run kubespray (cfg - kubeconfig_localhost: true - {{ inventory_dir }}/artifacts)
resource "null_resource" "kubespray_cluster" {
  depends_on = [local_file.hosts_yaml]

  provisioner "local-exec" {
    command = <<EOT
set -e
cd ${var.kubespray_dir}
"${var.ansible_playbook_bin}" -i inventory/mycluster/hosts.yaml -b -v cluster.yml
EOT
  }
}

# read kubeconfig
data "local_file" "kubeconfig" {
  depends_on = [null_resource.kubespray_cluster]
  filename   = "${var.kubespray_dir}/inventory/mycluster/artifacts/admin.conf"
}

locals {
  kc  = yamldecode(data.local_file.kubeconfig.content)
  api = local.kc.clusters[0].cluster.server
  ca  = base64decode(local.kc.clusters[0].cluster["certificate-authority-data"])
  crt = base64decode(local.kc.users[0].user["client-certificate-data"])
  key = base64decode(local.kc.users[0].user["client-key-data"])
}

provider "kubernetes" {
  host                   = local.api
  cluster_ca_certificate = local.ca
  client_certificate     = local.crt
  client_key             = local.key
}

provider "helm" {
  kubernetes {
    host                   = local.api
    cluster_ca_certificate = local.ca
    client_certificate     = local.crt
    client_key             = local.key
  }
}

# add namespace and deploy helm chart 
resource "kubernetes_namespace" "myapp" {
  depends_on = [null_resource.kubespray_cluster]
  metadata { name = "myapp" }
}
resource "helm_release" "todo_app" {
  depends_on = [kubernetes_namespace.myapp]
  name      = "todo"
  namespace = "myapp"
  chart     = "${var.helm_chart_path}"
}
