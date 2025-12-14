variable "name" {
  description = "Nombre del grupo de recursos."
  type        = string
}

variable "location" {
  description = "Ubicación del grupo de recursos."
  type        = string
}

variable "tags" {
  description = "Etiquetas para el grupo de recursos."
  type        = map(string)
  default     = {}
}
