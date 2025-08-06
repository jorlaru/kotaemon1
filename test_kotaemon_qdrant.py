# test_kotaemon_qdrant.py
import sys
sys.path.append('.')

from flowsettings import KH_VECTORSTORE

try:
    # Test configuración
    print("🔍 Verificando configuración de kotaemon...")
    print(f"Tipo: {KH_VECTORSTORE['__type__']}")
    print(f"Colección: {KH_VECTORSTORE['collection_name']}")
    
    # Test cliente
    client = KH_VECTORSTORE['client']
    collections = client.get_collections()
    print(f"✅ Conexión desde kotaemon exitosa. Colecciones: {len(collections.collections)}")
    
    print("\n🎉 ¡Kotaemon está configurado correctamente con Qdrant!")
    
except Exception as e:
    print(f"❌ Error en configuración: {e}")