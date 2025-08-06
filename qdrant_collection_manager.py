#!/usr/bin/env python3
"""
Qdrant Collection Manager - ENHANCED
====================================

Script para gestionar colecciones de Qdrant de forma remota.

Funcionalidades:
- ✅ Listar todas las colecciones existentes  
- ✅ Crear nuevas colecciones con configuración personalizada
- ✅ Eliminar colecciones (individual, múltiple o todas)
- ✅ Interface interactiva y amigable
- ✅ Verificar resultado post-operaciones

Autor: RAG MK3 System
Fecha: Agosto 2025
Versión: 2.0 Enhanced
"""

import os
import sys
import requests
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from colorama import init, Fore, Back, Style
import json
import time

# Inicializar colorama para compatibilidad con Windows
init(autoreset=True)

class QdrantCollectionManager:
    """
    Gestor de colecciones de Qdrant con interface interactiva MEJORADO.
    """
    
    def __init__(self):
        """Inicializar el gestor cargando configuración desde .env"""
        self.load_config()
        self.base_url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password) if self.user and self.password else None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
    def load_config(self):
        """Cargar configuración desde archivo .env"""
        load_dotenv()
        
        self.host = os.getenv('QDRANT_HOST')
        self.port = os.getenv('QDRANT_PORT', '6333')
        self.user = os.getenv('QDRANT_USER')
        self.password = os.getenv('QDRANT_PASSWORD')
        
        # Validar configuración
        if not self.host:
            self.print_error("❌ ERROR: QDRANT_HOST no encontrado en .env")
            sys.exit(1)
            
        if not self.user or not self.password:
            self.print_warning("⚠️  ADVERTENCIA: Credenciales no configuradas completamente")
    
    def print_header(self, text: str):
        """Imprimir header con formato"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print(f"{text.center(60)}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    def print_success(self, text: str):
        """Imprimir mensaje de éxito"""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
    
    def print_error(self, text: str):
        """Imprimir mensaje de error"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
    
    def print_warning(self, text: str):
        """Imprimir mensaje de advertencia"""
        print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")
    
    def print_info(self, text: str):
        """Imprimir mensaje informativo"""
        print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")
    
    def test_connection(self) -> bool:
        """
        Probar conexión con Qdrant.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            self.print_info(f"Probando conexión a {self.base_url}...")
            
            response = requests.get(
                f"{self.base_url}/",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.print_success(f"Conexión exitosa a Qdrant")
                return True
            else:
                self.print_error(f"Error de conexión: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_error("Error: No se puede conectar al servidor Qdrant")
            self.print_info(f"Verificar que Qdrant esté ejecutándose en {self.host}:{self.port}")
            return False
        except requests.exceptions.Timeout:
            self.print_error("Error: Timeout de conexión")
            return False
        except Exception as e:
            self.print_error(f"Error inesperado: {str(e)}")
            return False
    
    def get_collections(self) -> Optional[List[Dict]]:
        """
        Obtener lista de colecciones desde Qdrant.
        
        Returns:
            List[Dict]: Lista de colecciones o None si hay error
        """
        try:
            response = requests.get(
                f"{self.base_url}/collections",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    return data.get('result', {}).get('collections', [])
                else:
                    self.print_error(f"Error en respuesta de Qdrant: {data}")
                    return None
            else:
                self.print_error(f"Error HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.print_error(f"Error obteniendo colecciones: {str(e)}")
            return None
    
    def display_collections(self, collections: List[Dict]) -> None:
        """
        Mostrar colecciones en formato tabular mejorado.
        
        Args:
            collections: Lista de colecciones
        """
        if not collections:
            self.print_warning("✨ No hay colecciones en Qdrant (está limpio)")
            return
        
        print(f"{Fore.CYAN}{Style.BRIGHT}📚 Colecciones disponibles:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        
        # Header de tabla
        print(f"{Fore.WHITE}{Style.BRIGHT}{'#':>3} {'Nombre':<25} {'Vectores':<12} {'Estado':<10}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        
        for i, collection in enumerate(collections, 1):
            name = collection.get('name', 'Sin nombre')
            vectors_count = collection.get('vectors_count', 'N/A')
            status = collection.get('status', 'unknown')
            
            # Formato de estado con colores
            if status == 'green':
                status_display = f"{Fore.GREEN}●{Style.RESET_ALL} OK"
            elif status == 'yellow':
                status_display = f"{Fore.YELLOW}●{Style.RESET_ALL} Warn"
            elif status == 'red':
                status_display = f"{Fore.RED}●{Style.RESET_ALL} Error"
            else:
                status_display = f"{Fore.LIGHTBLACK_EX}●{Style.RESET_ALL} {status}"
            
            print(f"{Fore.WHITE}{i:3}. {Fore.YELLOW}{name:<25}{Style.RESET_ALL} {vectors_count:<12} {status_display}")
        
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total: {len(collections)} colecciones{Style.RESET_ALL}\n")
    
    # ========== NUEVA FUNCIONALIDAD: CREAR COLECCIONES ==========
    
    def get_collection_config(self) -> Optional[Dict]:
        """
        Obtener configuración para nueva colección del usuario.
        
        Returns:
            Dict: Configuración de la colección o None si se cancela
        """
        print(f"{Fore.CYAN}{Style.BRIGHT}🔧 Configuración de nueva colección{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
        
        try:
            # Nombre de la colección
            while True:
                name = input(f"{Fore.YELLOW}📝 Nombre de la colección: {Style.RESET_ALL}").strip()
                if not name:
                    self.print_warning("El nombre no puede estar vacío")
                    continue
                
                # Verificar si ya existe
                collections = self.get_collections()
                if collections and any(col['name'] == name for col in collections):
                    self.print_error(f"La colección '{name}' ya existe")
                    continue
                
                break
            
            # Tamaño del vector
            print(f"\n{Fore.CYAN}📐 Tamaño del vector (dimensiones):{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Azure OpenAI text-embedding-3-large: {Fore.YELLOW}3072{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Azure OpenAI text-embedding-3-small: {Fore.YELLOW}1536{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• OpenAI text-embedding-ada-002: {Fore.YELLOW}1536{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Sentence Transformers (típico): {Fore.YELLOW}384 o 768{Style.RESET_ALL}")
            
            while True:
                try:
                    vector_size = input(f"{Fore.YELLOW}Tamaño del vector [1536]: {Style.RESET_ALL}").strip()
                    if not vector_size:
                        vector_size = 1536
                    else:
                        vector_size = int(vector_size)
                    
                    if vector_size <= 0:
                        self.print_error("El tamaño debe ser mayor que 0")
                        continue
                    
                    if vector_size > 65536:
                        self.print_warning("Tamaño muy grande, ¿estás seguro?")
                        confirm = input(f"{Fore.YELLOW}¿Continuar? (y/n): {Style.RESET_ALL}").strip().lower()
                        if confirm not in ['y', 'yes', 'sí', 'si']:
                            continue
                    
                    break
                except ValueError:
                    self.print_error("Por favor ingresa un número válido")
            
            # Función de distancia
            print(f"\n{Fore.CYAN}📏 Función de distancia:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}1. {Fore.YELLOW}Cosine{Style.RESET_ALL} - Recomendado para embeddings de texto")
            print(f"{Fore.WHITE}2. {Fore.YELLOW}Euclidean{Style.RESET_ALL} - Distancia euclidiana clásica")
            print(f"{Fore.WHITE}3. {Fore.YELLOW}Dot{Style.RESET_ALL} - Producto punto (para vectores normalizados)")
            
            distance_options = {
                '1': 'Cosine',
                '2': 'Euclidean', 
                '3': 'Dot'
            }
            
            while True:
                choice = input(f"{Fore.YELLOW}Selecciona función de distancia [1]: {Style.RESET_ALL}").strip()
                if not choice:
                    choice = '1'
                
                if choice in distance_options:
                    distance = distance_options[choice]
                    break
                else:
                    self.print_error("Opción inválida. Selecciona 1, 2 o 3")
            
            # Configuración adicional
            config = {
                "vectors": {
                    "size": vector_size,
                    "distance": distance
                }
            }
            
            # Mostrar resumen
            print(f"\n{Fore.CYAN}{Style.BRIGHT}📋 Resumen de configuración:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Nombre: {Fore.YELLOW}{name}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Tamaño vector: {Fore.YELLOW}{vector_size}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}• Distancia: {Fore.YELLOW}{distance}{Style.RESET_ALL}")
            
            # Confirmación
            confirm = input(f"\n{Fore.YELLOW}¿Crear colección? (y/n): {Style.RESET_ALL}").strip().lower()
            
            if confirm in ['y', 'yes', 'sí', 'si']:
                return {'name': name, 'config': config}
            else:
                self.print_info("Creación de colección cancelada")
                return None
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operación cancelada por el usuario{Style.RESET_ALL}")
            return None
    
    def create_collection(self, collection_name: str, config: Dict) -> bool:
        """
        Crear una nueva colección en Qdrant.
        
        Args:
            collection_name: Nombre de la colección
            config: Configuración de la colección
            
        Returns:
            bool: True si la creación fue exitosa
        """
        try:
            self.print_info(f"Creando colección '{collection_name}'...")
            
            response = requests.put(
                f"{self.base_url}/collections/{collection_name}",
                json=config,
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get('result') is True:
                    self.print_success(f"Colección '{collection_name}' creada exitosamente")
                    return True
                else:
                    self.print_error(f"Error creando colección: {data}")
                    return False
            else:
                self.print_error(f"Error HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error creando colección '{collection_name}': {str(e)}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """
        Obtener información detallada de una colección.
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Dict: Información de la colección o None si hay error
        """
        try:
            response = requests.get(
                f"{self.base_url}/collections/{collection_name}",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    return data.get('result')
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            return None
    
    # ========== FUNCIONALIDADES EXISTENTES MEJORADAS ==========
    
    def get_user_selection(self, collections: List[Dict], action: str = "borrar") -> Optional[List[str]]:
        """
        Obtener selección del usuario.
        
        Args:
            collections: Lista de colecciones disponibles
            action: Acción a realizar ("borrar", "info", etc.)
            
        Returns:
            List[str]: Lista de nombres de colecciones seleccionadas
        """
        print(f"{Fore.CYAN}{Style.BRIGHT}🎯 Opciones de selección para {action}:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Número individual: {Fore.YELLOW}1{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Múltiples números: {Fore.YELLOW}1,3,5{Style.RESET_ALL}")
        if action == "borrar":
            print(f"{Fore.WHITE}• Todas las colecciones: {Fore.YELLOW}all{Style.RESET_ALL} o {Fore.YELLOW}*{Style.RESET_ALL}")
        print(f"{Fore.WHITE}• Salir: {Fore.YELLOW}q{Style.RESET_ALL} o {Fore.YELLOW}exit{Style.RESET_ALL}\n")
        
        while True:
            try:
                selection = input(f"{Fore.CYAN}Selecciona colecciones para {action}: {Style.RESET_ALL}").strip()
                
                if not selection:
                    self.print_warning("Por favor ingresa una selección")
                    continue
                
                # Salir
                if selection.lower() in ['q', 'quit', 'exit']:
                    return None
                
                # Todas las colecciones (solo para borrar)
                if action == "borrar" and selection.lower() in ['all', '*', 'todas']:
                    return [col['name'] for col in collections]
                
                # Selección por números
                selected_collections = []
                
                # Parsear números separados por comas
                numbers = [num.strip() for num in selection.split(',')]
                
                for num_str in numbers:
                    try:
                        num = int(num_str)
                        if 1 <= num <= len(collections):
                            collection_name = collections[num-1]['name']
                            if collection_name not in selected_collections:
                                selected_collections.append(collection_name)
                        else:
                            self.print_error(f"Número {num} fuera de rango (1-{len(collections)})")
                            return None
                    except ValueError:
                        self.print_error(f"'{num_str}' no es un número válido")
                        return None
                
                if selected_collections:
                    return selected_collections
                else:
                    self.print_warning("No se seleccionaron colecciones válidas")
                    continue
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operación cancelada por el usuario{Style.RESET_ALL}")
                return None
    
    def confirm_deletion(self, collections_to_delete: List[str]) -> bool:
        """
        Confirmar borrado de colecciones.
        
        Args:
            collections_to_delete: Lista de nombres de colecciones a borrar
            
        Returns:
            bool: True si el usuario confirma
        """
        print(f"\n{Fore.RED}{Style.BRIGHT}⚠️  CONFIRMACIÓN DE BORRADO ⚠️{Style.RESET_ALL}")
        print(f"{Fore.RED}{'─'*50}{Style.RESET_ALL}")
        
        print(f"{Fore.WHITE}Se borrarán las siguientes colecciones:{Style.RESET_ALL}")
        for collection in collections_to_delete:
            print(f"{Fore.RED}  • {collection}{Style.RESET_ALL}")
        
        print(f"\n{Fore.RED}⚠️  ESTA ACCIÓN NO SE PUEDE DESHACER ⚠️{Style.RESET_ALL}")
        print(f"{Fore.RED}{'─'*50}{Style.RESET_ALL}")
        
        while True:
            confirmation = input(f"{Fore.YELLOW}¿Confirmas el borrado? (y/n): {Style.RESET_ALL}").strip().lower()
            
            if confirmation in ['y', 'yes', 'sí', 'si']:
                return True
            elif confirmation in ['n', 'no']:
                return False
            else:
                self.print_warning("Por favor responde 'y' (sí) o 'n' (no)")
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Borrar una colección específica.
        
        Args:
            collection_name: Nombre de la colección a borrar
            
        Returns:
            bool: True si el borrado fue exitoso
        """
        try:
            response = requests.delete(
                f"{self.base_url}/collections/{collection_name}",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') is True:
                    return True
                else:
                    self.print_error(f"Error borrando '{collection_name}': {data}")
                    return False
            else:
                self.print_error(f"Error HTTP {response.status_code} borrando '{collection_name}': {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Error borrando '{collection_name}': {str(e)}")
            return False
    
    def delete_collections(self, collections_to_delete: List[str]) -> Tuple[List[str], List[str]]:
        """
        Borrar múltiples colecciones.
        
        Args:
            collections_to_delete: Lista de nombres de colecciones a borrar
            
        Returns:
            Tuple[List[str], List[str]]: (exitosas, fallidas)
        """
        successful = []
        failed = []
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🗑️  Iniciando proceso de borrado...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
        
        for i, collection_name in enumerate(collections_to_delete, 1):
            print(f"{Fore.WHITE}[{i}/{len(collections_to_delete)}] Borrando '{collection_name}'...", end=" ")
            
            if self.delete_collection(collection_name):
                successful.append(collection_name)
                print(f"{Fore.GREEN}✅ Éxito{Style.RESET_ALL}")
            else:
                failed.append(collection_name)
                print(f"{Fore.RED}❌ Error{Style.RESET_ALL}")
            
            # Pequeña pausa entre borrados
            time.sleep(0.5)
        
        return successful, failed
    
    def display_results(self, successful: List[str], failed: List[str], operation: str = "borrado") -> None:
        """
        Mostrar resultados de operaciones.
        
        Args:
            successful: Operaciones exitosas
            failed: Operaciones fallidas
            operation: Tipo de operación realizada
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 RESULTADOS DEL {operation.upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        if successful:
            print(f"{Fore.GREEN}{Style.BRIGHT}✅ {operation.capitalize()} exitoso ({len(successful)}):{Style.RESET_ALL}")
            for item in successful:
                print(f"{Fore.GREEN}  • {item}{Style.RESET_ALL}")
        
        if failed:
            print(f"\n{Fore.RED}{Style.BRIGHT}❌ Errores ({len(failed)}):{Style.RESET_ALL}")
            for item in failed:
                print(f"{Fore.RED}  • {item}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total procesadas: {len(successful) + len(failed)}{Style.RESET_ALL}")
    
    def show_collection_details(self, collections: List[Dict]) -> None:
        """
        Mostrar detalles de colecciones seleccionadas.
        
        Args:
            collections: Lista de colecciones a mostrar
        """
        selected = self.get_user_selection(collections, "ver detalles")
        
        if not selected:
            return
        
        for collection_name in selected:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}📋 Detalles de '{collection_name}'{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
            
            info = self.get_collection_info(collection_name)
            
            if info:
                # Información básica
                status = info.get('status', 'unknown')
                vectors_count = info.get('vectors_count', 0)
                indexed_vectors_count = info.get('indexed_vectors_count', 0)
                
                print(f"{Fore.WHITE}• Estado: {self.format_status(status)}")
                print(f"{Fore.WHITE}• Vectores totales: {Fore.YELLOW}{vectors_count:,}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}• Vectores indexados: {Fore.YELLOW}{indexed_vectors_count:,}{Style.RESET_ALL}")
                
                # Configuración de vectores
                config = info.get('config', {})
                params = config.get('params', {})
                vectors_config = params.get('vectors', {})
                
                if vectors_config:
                    size = vectors_config.get('size', 'N/A')
                    distance = vectors_config.get('distance', 'N/A')
                    print(f"{Fore.WHITE}• Dimensiones: {Fore.YELLOW}{size}{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}• Función distancia: {Fore.YELLOW}{distance}{Style.RESET_ALL}")
                
                # Optimizadores
                optimizer_config = config.get('optimizer_config', {})
                if optimizer_config:
                    print(f"{Fore.WHITE}• Config optimizador: {Fore.LIGHTBLACK_EX}{json.dumps(optimizer_config, indent=2)}{Style.RESET_ALL}")
                
            else:
                self.print_error(f"No se pudo obtener información de '{collection_name}'")
            
            print()
    
    def format_status(self, status: str) -> str:
        """Formatear estado con colores."""
        if status == 'green':
            return f"{Fore.GREEN}●{Style.RESET_ALL} Saludable"
        elif status == 'yellow':
            return f"{Fore.YELLOW}●{Style.RESET_ALL} Advertencia"
        elif status == 'red':
            return f"{Fore.RED}●{Style.RESET_ALL} Error"
        else:
            return f"{Fore.LIGHTBLACK_EX}●{Style.RESET_ALL} {status}"
    
    def show_main_menu(self) -> str:
        """
        Mostrar menú principal y obtener selección del usuario.
        
        Returns:
            str: Opción seleccionada
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🎮 MENÚ PRINCIPAL{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*30}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. {Fore.GREEN}👀 Ver colecciones{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. {Fore.BLUE}➕ Crear colección{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. {Fore.YELLOW}📋 Ver detalles{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. {Fore.RED}🗑️  Eliminar colecciones{Style.RESET_ALL}")
        print(f"{Fore.WHITE}5. {Fore.LIGHTBLACK_EX}❌ Salir{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*30}{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"{Fore.CYAN}Selecciona una opción (1-5): {Style.RESET_ALL}").strip()
                
                if choice in ['1', '2', '3', '4', '5']:
                    return choice
                else:
                    self.print_warning("Por favor selecciona una opción válida (1-5)")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Saliendo...{Style.RESET_ALL}")
                return '5'
    
    def run(self):
        """Ejecutar el gestor de colecciones con menú interactivo."""
        
        # Header del programa
        self.print_header("QDRANT COLLECTION MANAGER - ENHANCED")
        
        print(f"{Fore.WHITE}Configuración:{Style.RESET_ALL}")
        print(f"  • Host: {Fore.YELLOW}{self.host}:{self.port}{Style.RESET_ALL}")
        print(f"  • Usuario: {Fore.YELLOW}{self.user or 'No configurado'}{Style.RESET_ALL}")
        print(f"  • Auth: {Fore.YELLOW}{'Configurada' if self.auth else 'No configurada'}{Style.RESET_ALL}")
        
        # Probar conexión
        if not self.test_connection():
            self.print_error("No se puede continuar sin conexión a Qdrant")
            sys.exit(1)
        
        try:
            while True:
                choice = self.show_main_menu()
                
                if choice == '1':  # Ver colecciones
                    self.print_info("Obteniendo lista de colecciones...")
                    collections = self.get_collections()
                    
                    if collections is None:
                        self.print_error("No se pudieron obtener las colecciones")
                    else:
                        self.display_collections(collections)
                
                elif choice == '2':  # Crear colección
                    collection_config = self.get_collection_config()
                    
                    if collection_config:
                        name = collection_config['name'] 
                        config = collection_config['config']
                        
                        if self.create_collection(name, config):
                            self.print_info("Verificando colección creada...")
                            time.sleep(1)
                            
                            # Mostrar info de la nueva colección
                            info = self.get_collection_info(name)
                            if info:
                                print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 Colección creada exitosamente{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}• Nombre: {Fore.YELLOW}{name}{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}• Estado: {self.format_status(info.get('status', 'unknown'))}")
                
                elif choice == '3':  # Ver detalles
                    collections = self.get_collections()
                    
                    if collections is None:
                        self.print_error("No se pudieron obtener las colecciones")
                    elif not collections:
                        self.print_warning("No hay colecciones para mostrar detalles")
                    else:
                        self.display_collections(collections)
                        self.show_collection_details(collections)
                
                elif choice == '4':  # Eliminar colecciones
                    collections = self.get_collections()
                    
                    if collections is None:
                        self.print_error("No se pudieron obtener las colecciones")
                    elif not collections:
                        self.print_warning("No hay colecciones para eliminar")
                    else:
                        self.display_collections(collections)
                        
                        selected = self.get_user_selection(collections, "borrar")
                        
                        if selected and self.confirm_deletion(selected):
                            successful, failed = self.delete_collections(selected)
                            self.display_results(successful, failed, "borrado")
                        elif selected:
                            self.print_info("Borrado cancelado por el usuario")
                
                elif choice == '5':  # Salir
                    break
                
                # Pausa antes de mostrar el menú nuevamente
                if choice != '5':
                    input(f"\n{Fore.LIGHTBLACK_EX}Presiona Enter para continuar...{Style.RESET_ALL}")
                    
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Programa interrumpido por el usuario{Style.RESET_ALL}")
        except Exception as e:
            self.print_error(f"Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}¡Gracias por usar Qdrant Collection Manager Enhanced!{Style.RESET_ALL}")


def main():
    """Función principal."""
    try:
        manager = QdrantCollectionManager()
        manager.run()
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()