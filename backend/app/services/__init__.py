"""Application services"""

# Import factory functions instead of initialized services
try:
    from .storage_factory import get_storage_service, get_storage_info
    __all__ = ["get_storage_service", "get_storage_info"]
except ImportError:
    __all__ = []

# Optional services with dependencies
try:
    from .claude_mcp import ClaudeMCPService
    __all__.append("ClaudeMCPService")
except ImportError:
    pass

try:
    from .embeddings import EmbeddingService
    __all__.append("EmbeddingService")
except ImportError:
    pass