"""Application services"""

# Only import services that don't have missing dependencies
try:
    from .storage_factory import storage_service, storage_info
    __all__ = ["storage_service", "storage_info"]
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