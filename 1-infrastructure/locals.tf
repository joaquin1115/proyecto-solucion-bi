locals {
  # Variables de entorno para el módulo Container App.
  container_app_environment_variables = {
    DB_HOST                         = module.postgresql.server_fqdn
    DB_PORT                         = "5432"
    DB_USER                         = var.postgresql_admin_username
    DB_PASSWORD                     = var.postgresql_admin_password
    DB_NAME_PRACTITIONER            = var.postgresql_databases[0]
    DB_NAME_CI                      = var.postgresql_databases[1]
    DATABRICKS_WORKSPACE_URL        = "https://${module.databricks_workspace.workspace_url}"
    DATABRICKS_TOKEN                = module.databricks_config.token
    FLASK_ENV                       = "production"
    AZURE_STORAGE_CONNECTION_STRING = module.storage.connection_string
    DATABRICKS_CLUSTER_ID           = module.databricks_config.cluster_id
    KEY_VAULT_NAME                  = var.key_vault_name
  }

  # Lista de nombres de subredes para asociar a la tabla de rutas.
  route_table_associated_subnet_map = {
    # Las subredes de Databricks ahora tienen su propia tabla de rutas.
    # Se elimina la asociación de Databricks ya que no está en la VNet.
    containerapp = module.network.containerapp_subnet_id
  }

  # Mapa de rutas para la tabla de rutas.
  # Se elimina la creación de la ruta por defecto aquí para evitar conflictos.
  # Se asume que el módulo 'firewall' gestiona su propia ruta por defecto.
  routes_map = {}
}