import os
from importlib.metadata import version
from inspect import currentframe, getframeinfo
from pathlib import Path

from decouple import config
from theflow.settings.default import *  # noqa

# Supported languages mapping
SUPPORTED_LANGUAGE_MAP = {
    "en": "English",
    "vi": "Tiếng Việt", 
    "ja": "日本語",
    "ko": "한국어",
    "zh": "中文",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "pt": "Português",
    "ru": "Русский",
}

cur_frame = currentframe()
if cur_frame is None:
    raise ValueError("Cannot get the current frame.")
this_file = getframeinfo(cur_frame).filename
this_dir = Path(this_file).parent

# change this if your app use a different name
KH_PACKAGE_NAME = "kotaemon_app"

KH_APP_VERSION = config("KH_APP_VERSION", None)
if not KH_APP_VERSION:
    try:
        # Caution: This might produce the wrong version
        # https://stackoverflow.com/a/59533071
        KH_APP_VERSION = version(KH_PACKAGE_NAME)
    except Exception:
        KH_APP_VERSION = "local"

KH_GRADIO_SHARE = config("KH_GRADIO_SHARE", default=False, cast=bool)
KH_ENABLE_FIRST_SETUP = config("KH_ENABLE_FIRST_SETUP", default=True, cast=bool)
KH_DEMO_MODE = config("KH_DEMO_MODE", default=False, cast=bool)
KH_OLLAMA_URL = config("KH_OLLAMA_URL", default="http://localhost:11434/v1/")

# App can be ran from anywhere and it's not trivial to decide where to store app data.
# So let's use the same directory as the flowsetting.py file.
KH_APP_DATA_DIR = this_dir / "ktem_app_data"
KH_APP_DATA_EXISTS = KH_APP_DATA_DIR.exists()
KH_APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# User data directory
KH_USER_DATA_DIR = KH_APP_DATA_DIR / "user_data"
KH_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# markdown output directory
KH_MARKDOWN_OUTPUT_DIR = KH_APP_DATA_DIR / "markdown_cache_dir"
KH_MARKDOWN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# chunks output directory
KH_CHUNKS_OUTPUT_DIR = KH_APP_DATA_DIR / "chunks_cache_dir"
KH_CHUNKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# zip output directory
KH_ZIP_OUTPUT_DIR = KH_APP_DATA_DIR / "zip_cache_dir"
KH_ZIP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# zip input directory
KH_ZIP_INPUT_DIR = KH_APP_DATA_DIR / "zip_cache_dir_in"
KH_ZIP_INPUT_DIR.mkdir(parents=True, exist_ok=True)

# HF models can be big, let's store them in the app data directory so that it's easier
# for users to manage their storage.
# ref: https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache
os.environ["HF_HOME"] = str(KH_APP_DATA_DIR / "huggingface")
os.environ["HF_HUB_CACHE"] = str(KH_APP_DATA_DIR / "huggingface")

# doc directory
KH_DOC_DIR = this_dir / "docs"

# Language settings
KH_LANG = config("KH_LANG", default="en")
if KH_LANG not in SUPPORTED_LANGUAGE_MAP:
    print(f"Warning: Language {KH_LANG} is not supported. Falling back to English.")
    KH_LANG = "en"

# Additional required settings
KH_MODE = config("KH_MODE", default="dev")
KH_SSO_ENABLED = config("KH_SSO_ENABLED", default=False, cast=bool)
KH_FEATURE_CHAT_SUGGESTION = config("KH_FEATURE_CHAT_SUGGESTION", default=False, cast=bool)
KH_FEATURE_USER_MANAGEMENT = config("KH_FEATURE_USER_MANAGEMENT", default=True, cast=bool)
KH_USER_CAN_SEE_PUBLIC = None
KH_FEATURE_USER_MANAGEMENT_ADMIN = config("KH_FEATURE_USER_MANAGEMENT_ADMIN", default="admin")
KH_FEATURE_USER_MANAGEMENT_PASSWORD = config("KH_FEATURE_USER_MANAGEMENT_PASSWORD", default="admin")
KH_ENABLE_ALEMBIC = False
KH_DATABASE = f"sqlite:///{KH_USER_DATA_DIR / 'sql.db'}"
KH_FILESTORAGE_PATH = str(KH_USER_DATA_DIR / "files")
KH_WEB_SEARCH_BACKEND = (
    "kotaemon.indices.retrievers.tavily_web_search.WebSearch"
    # "kotaemon.indices.retrievers.jina_web_search.WebSearch"
)
KH_APP_NAME = config("KH_APP_NAME", default="Kotaemon")

# Application settings (SETTINGS_APP)
SETTINGS_APP = {
    "lang": {
        "name": "Language",
        "value": KH_LANG,
        "choices": [(v, k) for k, v in SUPPORTED_LANGUAGE_MAP.items()],
        "component": "dropdown",
    }
}

# Reasoning settings (SETTINGS_REASONING)  
SETTINGS_REASONING = {
    "use": {
        "name": "Reasoning pipeline",
        "value": "simple",
        "choices": [],
        "component": "dropdown",
    }
}

# Index settings
SETTINGS_INDEX = {}

# Document store configuration
KH_DOCSTORE = {
    # "__type__": "kotaemon.storages.ElasticsearchDocumentStore",
    # "__type__": "kotaemon.storages.SimpleFileDocumentStore",
    "__type__": "kotaemon.storages.LanceDBDocumentStore",
    "path": str(KH_USER_DATA_DIR / "docstore"),
}

# ========== CONFIGURACIÓN QDRANT VPS ==========
def get_qdrant_client():
    """Crear cliente Qdrant configurado con credenciales del .env"""
    from qdrant_client import QdrantClient
    
    host = config('QDRANT_HOST')
    port = config('QDRANT_PORT', '6333')
    user = config('QDRANT_USER', '')
    password = config('QDRANT_PASSWORD', '')
    
    # Construir URL con credenciales
    if user and password:
        url = f"http://{user}:{password}@{host}:{port}"
    else:
        url = f"http://{host}:{port}"
    
    return QdrantClient(
        url=url,
        prefer_grpc=False,
        timeout=10
    )

# Configuración del vectorstore - CAMBIO PRINCIPAL PARA USAR QDRANT
KH_VECTORSTORE = {
    # Configuración original comentada:
    # "__type__": "kotaemon.storages.LanceDBVectorStore",
    # "__type__": "kotaemon.storages.ChromaVectorStore",
    # "__type__": "kotaemon.storages.MilvusVectorStore",
    # "path": str(KH_USER_DATA_DIR / "vectorstore"),
    
    # Nueva configuración para Qdrant VPS:
    "__type__": "kotaemon.storages.QdrantVectorStore",
    "collection_name": config("QDRANT_COLLECTION_NAME", default="kotaemon"),
    "client": get_qdrant_client(),
}
# ========== FIN CONFIGURACIÓN QDRANT ==========

KH_LLMS = {}
KH_EMBEDDINGS = {}
KH_RERANKINGS = {}

# populate options from config
if config("AZURE_OPENAI_API_KEY", default="") and config(
    "AZURE_OPENAI_ENDPOINT", default=""
):
    if config("AZURE_OPENAI_CHAT_DEPLOYMENT", default=""):
        KH_LLMS["azure"] = {
            "spec": {
                "__type__": "kotaemon.llms.AzureChatOpenAI",
                "temperature": 0,
                "azure_endpoint": config("AZURE_OPENAI_ENDPOINT", default=""),
                "api_key": config("AZURE_OPENAI_API_KEY", default=""),
                "api_version": config("OPENAI_API_VERSION", default="")
                or "2024-02-15-preview",
                "azure_deployment": config("AZURE_OPENAI_CHAT_DEPLOYMENT", default=""),
                "timeout": 20,
            },
            "default": False,
        }
    if config("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", default=""):
        KH_EMBEDDINGS["azure"] = {
            "spec": {
                "__type__": "kotaemon.embeddings.AzureOpenAIEmbeddings",
                "azure_endpoint": config("AZURE_OPENAI_ENDPOINT", default=""),
                "api_key": config("AZURE_OPENAI_API_KEY", default=""),
                "api_version": config("OPENAI_API_VERSION", default="")
                or "2024-02-15-preview",
                "azure_deployment": config(
                    "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", default=""
                ),
                "timeout": 10,
            },
            "default": False,
        }

OPENAI_DEFAULT = "<YOUR_OPENAI_KEY>"
OPENAI_API_KEY = config("OPENAI_API_KEY", default=OPENAI_DEFAULT)
GOOGLE_API_KEY = config("GOOGLE_API_KEY", default="your-key")
IS_OPENAI_DEFAULT = len(OPENAI_API_KEY) > 0 and OPENAI_API_KEY != OPENAI_DEFAULT

if OPENAI_API_KEY:
    KH_LLMS["openai"] = {
        "spec": {
            "__type__": "kotaemon.llms.ChatOpenAI",
            "temperature": 0,
            "base_url": config("OPENAI_API_BASE", default="")
            or "https://api.openai.com/v1",
            "api_key": OPENAI_API_KEY,
            "model": config("OPENAI_CHAT_MODEL", default="gpt-4o-mini"),
            "timeout": 20,
        },
        "default": IS_OPENAI_DEFAULT,
    }
    KH_EMBEDDINGS["openai"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
            "base_url": config("OPENAI_API_BASE", default="https://api.openai.com/v1"),
            "api_key": OPENAI_API_KEY,
            "model": config(
                "OPENAI_EMBEDDINGS_MODEL", default="text-embedding-3-large"
            ),
            "timeout": 10,
            "context_length": 8191,
        },
        "default": IS_OPENAI_DEFAULT,
    }

VOYAGE_API_KEY = config("VOYAGE_API_KEY", default="")
if VOYAGE_API_KEY:
    KH_EMBEDDINGS["voyageai"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.VoyageAIEmbeddings",
            "api_key": VOYAGE_API_KEY,
            "model": config("VOYAGE_EMBEDDINGS_MODEL", default="voyage-3-large"),
        },
        "default": False,
    }
    KH_RERANKINGS["voyageai"] = {
        "spec": {
            "__type__": "kotaemon.rerankings.VoyageAIReranking",
            "model_name": "rerank-2",
            "api_key": VOYAGE_API_KEY,
        },
        "default": False,
    }

if config("LOCAL_MODEL", default=""):
    KH_LLMS["ollama"] = {
        "spec": {
            "__type__": "kotaemon.llms.ChatOpenAI",
            "base_url": KH_OLLAMA_URL,
            "model": config("LOCAL_MODEL", default="qwen2.5:7b"),
            "api_key": "ollama",
        },
        "default": False,
    }
    KH_LLMS["ollama-long-context"] = {
        "spec": {
            "__type__": "kotaemon.llms.LCOllamaChat",
            "base_url": KH_OLLAMA_URL.replace("v1/", ""),
            "model": config("LOCAL_MODEL", default="qwen2.5:7b"),
            "num_ctx": 8192,
        },
        "default": False,
    }

    KH_EMBEDDINGS["ollama"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
            "base_url": KH_OLLAMA_URL,
            "model": config("LOCAL_MODEL_EMBEDDINGS", default="nomic-embed-text"),
            "api_key": "ollama",
        },
        "default": False,
    }
    KH_EMBEDDINGS["fast_embed"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.FastEmbedEmbeddings",
            "model_name": "BAAI/bge-base-en-v1.5",
        },
        "default": False,
    }

# additional LLM configurations
KH_LLMS["claude"] = {
    "spec": {
        "__type__": "kotaemon.llms.chats.LCAnthropicChat",
        "model_name": "claude-3-5-sonnet-20240620",
        "api_key": "your-key",
    },
    "default": False,
}
KH_LLMS["google"] = {
    "spec": {
        "__type__": "kotaemon.llms.chats.LCGeminiChat",
        "model_name": "gemini-1.5-flash",
        "api_key": GOOGLE_API_KEY,
    },
    "default": not IS_OPENAI_DEFAULT,
}
KH_LLMS["groq"] = {
    "spec": {
        "__type__": "kotaemon.llms.ChatOpenAI",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
        "api_key": "your-key",
    },
    "default": False,
}
KH_LLMS["cohere"] = {
    "spec": {
        "__type__": "kotaemon.llms.chats.LCCohereChat",
        "model_name": "command-r-plus-08-2024",
        "api_key": config("COHERE_API_KEY", default="your-key"),
    },
    "default": False,
}
KH_LLMS["mistral"] = {
    "spec": {
        "__type__": "kotaemon.llms.ChatOpenAI",
        "base_url": "https://api.mistral.ai/v1",
        "model": "ministral-8b-latest",
        "api_key": config("MISTRAL_API_KEY", default="your-key"),
    },
    "default": False,
}

# additional embeddings configurations
KH_EMBEDDINGS["cohere"] = {
    "spec": {
        "__type__": "kotaemon.embeddings.LCCohereEmbeddings",
        "model": "embed-multilingual-v3.0",
        "cohere_api_key": config("COHERE_API_KEY", default="your-key"),
        "user_agent": "default",
    },
    "default": False,
}
KH_EMBEDDINGS["google"] = {
    "spec": {
        "__type__": "kotaemon.embeddings.LCGoogleEmbeddings",
        "model": "models/text-embedding-004",
        "google_api_key": GOOGLE_API_KEY,
    },
    "default": not IS_OPENAI_DEFAULT,
}
KH_EMBEDDINGS["mistral"] = {
    "spec": {
        "__type__": "kotaemon.embeddings.LCMistralEmbeddings",
        "model": "mistral-embed",
        "api_key": config("MISTRAL_API_KEY", default="your-key"),
    },
    "default": False,
}

# Reasoning pipelines configuration
KH_REASONINGS_USE_MULTIMODAL = config(
    "KH_REASONINGS_USE_MULTIMODAL", default=True, cast=bool
)

KH_REASONINGS = [
    "ktem.reasoning.simple.FullQAPipeline", 
    "ktem.reasoning.simple.FullDecomposeQAPipeline",
]

if config("KH_REASONING_USE_AGENT", default=True, cast=bool):
    KH_REASONINGS += [
        "ktem.reasoning.react.ReactAgentPipeline",
        "ktem.reasoning.rewoo.RewooAgentPipeline",
    ]

if config("USE_GRAPHRAG", default=False, cast=bool):
    KH_REASONINGS += [
        "ktem.reasoning.graph_rag.GraphRAGGlobalPipeline",
        "ktem.reasoning.graph_rag.GraphRAGLocalPipeline",
    ]

if config("USE_LIGHTRAG", default=False, cast=bool):
    KH_REASONINGS += [
        "ktem.reasoning.light_rag.LightRAGPipeline",
    ]

# Index types configuration - REQUERIDO PARA EL INICIO
KH_INDEX_TYPES = [
    "ktem.index.file.index.FileIndex",
]

# Index instances configuration - INSTANCIAS ESPECÍFICAS DE ÍNDICES
KH_INDICES = [
    {
        "name": "default",
        "index_type": "FileIndex",
        "config": {
            "supported_file_types": ".pdf, .txt, .docx, .md, .html",
            "max_file_size": 1000,  # MB
            "max_number_of_files": 0,  # 0 = sin límite
            "private": False,
            "chunk_size": 1024,
            "chunk_overlap": 200,
        },
    }
]

# Feature flags
KH_FEATURE_CHAT_SUGGESTION_SAMPLES = [
    "Summary this document",
    "Generate a FAQ for this document", 
    "Identify the main highlights in bullet points",
]