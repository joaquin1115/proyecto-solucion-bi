import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)

# ================================
# CONFIGURACIÓN DATABRICKS (ENV VARS)
# ================================
DATABRICKS_WORKSPACE_URL = os.environ.get("DATABRICKS_WORKSPACE_URL")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
CLUSTER_ID = os.environ.get("DATABRICKS_CLUSTER_ID")

if not DATABRICKS_WORKSPACE_URL:
    raise RuntimeError("❌ ERROR: La variable DATABRICKS_WORKSPACE_URL no está definida en las variables de entorno.")

if not DATABRICKS_TOKEN:
    raise RuntimeError("❌ ERROR: La variable DATABRICKS_TOKEN no está definida en las variables de entorno.")


HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}


# ================================
# NOTEBOOK PATHS EN DATABRICKS
# ================================
NOTEBOOKS = {
    "practitioner": [
        "/Workspace/Users/leogcardenasp@gmail.com/Limpiar Practitioner",
        "/Workspace/Users/leogcardenasp@gmail.com/Transformar Practitioner",
        "/Workspace/Users/leogcardenasp@gmail.com/Vista Practitioner"
    ],
    "continuous_integration": [
        "/Workspace/Users/leogcardenasp@gmail.com/Limpiar Continuous Integration",
        "/Workspace/Users/leogcardenasp@gmail.com/Transformar Continuous Integration",
        "/Workspace/Users/leogcardenasp@gmail.com/Vista Continuous Integration"
    ]
}


# ================================
# Listar clusters disponibles
# ================================
def list_clusters():
    """Lista todos los clusters disponibles para diagnóstico"""
    logging.info("📋 Listando clusters disponibles...")
    url = f"{DATABRICKS_WORKSPACE_URL}/api/2.0/clusters/list"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            clusters = response.json().get("clusters", [])
            if clusters:
                for cluster in clusters:
                    logging.info(
                        f"📌 Cluster: {cluster['cluster_name']} | "
                        f"ID: {cluster['cluster_id']} | "
                        f"Estado: {cluster['state']}"
                    )
            else:
                logging.warning("⚠️ No se encontraron clusters")
            return clusters
        else:
            logging.error(f"❌ Error listando clusters: {response.text}")
            return []
    except Exception as e:
        logging.error(f"❌ Excepción listando clusters: {str(e)}")
        return []


# ================================
# Verificar y arrancar cluster si es necesario
# ================================
def ensure_cluster_running(cluster_id: str):
    """Asegura que el cluster esté en estado RUNNING"""
    logging.info(f"🔍 Verificando estado del cluster: {cluster_id}")
    
    url = f"{DATABRICKS_WORKSPACE_URL}/api/2.0/clusters/get"
    
    try:
        response = requests.get(url, headers=HEADERS, params={"cluster_id": cluster_id})
        
        if response.status_code != 200:
            logging.error(f"❌ Error obteniendo estado del cluster: {response.text}")
            logging.info("📋 Intentando listar clusters disponibles...")
            list_clusters()
            raise Exception(f"❌ No se pudo obtener información del cluster {cluster_id}")
        
        cluster_info = response.json()
        state = cluster_info.get("state")
        cluster_name = cluster_info.get("cluster_name", "Unknown")
        
        logging.info(f"📊 Cluster '{cluster_name}' está en estado: {state}")
        
        if state == "TERMINATED":
            logging.info("🔄 Cluster terminado. Iniciando cluster...")
            start_url = f"{DATABRICKS_WORKSPACE_URL}/api/2.0/clusters/start"
            start_response = requests.post(
                start_url, 
                headers=HEADERS, 
                json={"cluster_id": cluster_id}
            )
            
            if start_response.status_code != 200:
                raise Exception(f"❌ Error iniciando cluster: {start_response.text}")
            
            # Esperar a que el cluster inicie
            max_wait = 300  # 5 minutos
            start_time = time.time()
            
            while True:
                if time.time() - start_time > max_wait:
                    raise Exception("⛔ Timeout esperando que el cluster inicie")
                
                response = requests.get(url, headers=HEADERS, params={"cluster_id": cluster_id})
                current_state = response.json().get("state")
                
                logging.info(f"   → Estado actual: {current_state}")
                
                if current_state == "RUNNING":
                    logging.info("✅ Cluster iniciado y listo")
                    break
                elif current_state == "ERROR":
                    raise Exception("❌ El cluster entró en estado ERROR")
                
                time.sleep(10)
        
        elif state == "PENDING" or state == "RESTARTING":
            logging.info(f"⏳ Cluster en estado {state}. Esperando...")
            max_wait = 300
            start_time = time.time()
            
            while True:
                if time.time() - start_time > max_wait:
                    raise Exception(f"⛔ Timeout esperando que el cluster esté listo desde estado {state}")
                
                response = requests.get(url, headers=HEADERS, params={"cluster_id": cluster_id})
                current_state = response.json().get("state")
                
                logging.info(f"   → Estado actual: {current_state}")
                
                if current_state == "RUNNING":
                    logging.info("✅ Cluster listo")
                    break
                elif current_state == "ERROR":
                    raise Exception("❌ El cluster entró en estado ERROR")
                
                time.sleep(10)
        
        elif state == "RUNNING":
            logging.info("✅ Cluster ya está corriendo")
        
        else:
            logging.warning(f"⚠️ Estado desconocido del cluster: {state}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Error verificando/iniciando cluster: {str(e)}")
        raise


# ================================
# Ejecutar notebook como Job temporal
# ================================
def run_notebook(notebook_path: str, params: dict):
    logging.info(f"▶️ Ejecutando notebook: {notebook_path}")
    logging.info(f"📝 Parámetros: {params}")
    
    # Verificar que el cluster existe y está corriendo
    ensure_cluster_running(CLUSTER_ID)
    
    payload = {
        "run_name": f"Pipeline - {notebook_path.split('/')[-1]}",
        "existing_cluster_id": CLUSTER_ID,
        "notebook_task": {
            "notebook_path": notebook_path,
            "base_parameters": params
        },
        "timeout_seconds": 3600  # 1 hora de timeout
    }
    
    url = f"{DATABRICKS_WORKSPACE_URL}/api/2.1/jobs/runs/submit"
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code != 200:
            logging.error(f"❌ Response status: {response.status_code}")
            logging.error(f"❌ Response body: {response.text}")
            raise Exception(
                f"❌ Error lanzando notebook '{notebook_path}': {response.text}"
            )
        
        run_id = response.json()["run_id"]
        logging.info(f"✔ Notebook lanzado correctamente. Run ID: {run_id}")
        
        return run_id
        
    except Exception as e:
        logging.error(f"❌ Excepción lanzando notebook: {str(e)}")
        raise


# ================================
# Esperar a que un run termine
# ================================
def wait_for_run(run_id: int, timeout: int = 900):
    logging.info(f"⏳ Esperando ejecución del Run ID: {run_id}")
    
    url = f"{DATABRICKS_WORKSPACE_URL}/api/2.1/jobs/runs/get"
    start = time.time()
    
    while True:
        try:
            response = requests.get(url, headers=HEADERS, params={"run_id": run_id})
            
            if response.status_code != 200:
                logging.error(f"❌ Error consultando estado del run: {response.text}")
                time.sleep(5)
                continue
            
            state = response.json().get("state", {})
            life = state.get("life_cycle_state")
            result = state.get("result_state")
            
            logging.info(f"   → Estado actual: {life} / {result}")
            
            if life == "TERMINATED":
                if result == "SUCCESS":
                    logging.info("✔ Notebook finalizó correctamente.")
                    return True
                else:
                    error_info = state.get("state_message", "Error desconocido")
                    raise Exception(f"❌ Notebook falló: {error_info}")
            
            if time.time() - start > timeout:
                raise Exception(f"⛔ Timeout esperando el run {run_id}")
            
            time.sleep(5)
            
        except Exception as e:
            if "Notebook falló" in str(e) or "Timeout" in str(e):
                raise
            logging.error(f"❌ Error en wait_for_run: {str(e)}")
            time.sleep(5)


# ================================
# Ejecutar los notebooks secuenciales
# ================================
def trigger_notebook_run(destination: str, adls_path: str):
    """
    Ejecuta la secuencia de notebooks para un destino específico
    
    Args:
        destination: 'practitioner' o 'continuous_integration'
        adls_path: Ruta del archivo en ADLS
    """
    
    if destination not in NOTEBOOKS:
        raise ValueError(f"❌ Destino inválido: {destination}. Debe ser 'practitioner' o 'continuous_integration'")
    
    params = {"input_path": adls_path}
    notebook_sequence = NOTEBOOKS[destination]
    
    logging.info("=" * 60)
    logging.info(f"🚀 Pipeline Databricks para: {destination}")
    logging.info(f"📄 Archivo ADLS: {adls_path}")
    logging.info(f"🔧 Cluster ID: {CLUSTER_ID}")
    logging.info("=" * 60)
    
    try:
        for idx, nb in enumerate(notebook_sequence, 1):
            logging.info(f"\n{'='*60}")
            logging.info(f"📓 Paso {idx}/{len(notebook_sequence)}: {nb.split('/')[-1]}")
            logging.info(f"{'='*60}")
            
            run_id = run_notebook(nb, params)
            wait_for_run(run_id)
        
        logging.info("\n" + "=" * 60)
        logging.info("🏁 Pipeline completado exitosamente.")
        logging.info("=" * 60)
        return True
        
    except Exception as e:
        logging.error("\n" + "=" * 60)
        logging.error(f"💥 Pipeline falló: {str(e)}")
        logging.error("=" * 60)
        raise


# ================================
# Función de diagnóstico (opcional)
# ================================
def diagnose_cluster():
    """Función auxiliar para diagnosticar problemas con el cluster"""
    logging.info("\n🔍 DIAGNÓSTICO DE CLUSTER")
    logging.info("=" * 60)
    
    logging.info(f"Cluster ID configurado: {CLUSTER_ID}")
    logging.info(f"Workspace URL: {DATABRICKS_WORKSPACE_URL}")
    
    # Listar todos los clusters
    list_clusters()
    
    # Verificar estado del cluster específico
    try:
        ensure_cluster_running(CLUSTER_ID)
    except Exception as e:
        logging.error(f"❌ No se pudo verificar el cluster: {str(e)}")
    
    logging.info("=" * 60)


# Ejemplo de uso si ejecutas este archivo directamente
if __name__ == "__main__":
    # Descomentar para diagnosticar
    # diagnose_cluster()
    pass