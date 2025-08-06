# test_qdrant_llamaindex_fixed.py
import os
from dotenv import load_dotenv

print("🔍 Verificando instalación...")

try:
    from qdrant_client import QdrantClient
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    
    load_dotenv()
    
    host = os.getenv('QDRANT_HOST')
    port = int(os.getenv('QDRANT_PORT', 6333))
    user = os.getenv('QDRANT_USER')
    password = os.getenv('QDRANT_PASSWORD')
    
    # Crear URL con credenciales
    qdrant_url = f"http://{user}:{password}@{host}:{port}"
    print(f"🔗 Conectando con URL: http://{user}:***@{host}:{port}")
    
    # PASO 1: Cliente Qdrant configurado
    client = QdrantClient(
        url=qdrant_url,
        prefer_grpc=False,
        timeout=10
    )
    
    collections = client.get_collections()
    print(f"✅ Conexión exitosa. Colecciones: {len(collections.collections)}")
    
    # PASO 2: LlamaIndex con cliente configurado (MÉTODO CORRECTO)
    vs = QdrantVectorStore(
        collection_name="test_kotaemon",
        client=client  # ← Pasar cliente ya configurado
    )
    print("✅ Integración LlamaIndex funcionando")
    
    print("\n🎉 ¡Todo configurado correctamente!")
    
except Exception as e:
    print(f"❌ Error: {e}")