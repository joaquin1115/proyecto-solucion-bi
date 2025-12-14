variable "workspace_url" {
  description = "URL del workspace de Databricks."
  type        = string
}

variable "storage_account_name" {
  description = "Nombre de la cuenta de almacenamiento a conectar."
  type        = string
}

variable "storage_account_key" {
  description = "Clave de acceso de la cuenta de almacenamiento."
  type        = string
  sensitive   = true
}

variable "key_vault_id" {
  description = "ID del Key Vault donde se guardarán los secretos."
  type        = string
}

variable "cluster_name" {
  description = "Nombre del clúster de Databricks."
  type        = string
}

variable "spark_version" {
  description = "Versión de Spark para el clúster."
  type        = string
}

variable "node_type_id" {
  description = "Tipo de nodo para el clúster."
  type        = string
}

variable "num_workers" {
  description = "Número de workers para el clúster. 0 para Single Node."
  type        = number
  default     = 0
}

variable "autotermination_minutes" {
  description = "Minutos de inactividad antes de que el clúster se termine automáticamente."
  type        = number
}

variable "custom_tags" {
  description = "Etiquetas personalizadas para el clúster."
  type        = map(string)
  default = {
    "ResourceClass" = "SingleNode"
  }
}