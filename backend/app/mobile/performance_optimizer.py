"""
Mobile Performance Optimizer
Optimizes API responses and data for mobile devices
"""

import gzip
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from fastapi import Request
import time

logger = logging.getLogger(__name__)


class ConnectionType(str, Enum):
    """Mobile connection types"""
    WIFI = "wifi"
    CELLULAR_5G = "5g"
    CELLULAR_4G = "4g"
    CELLULAR_3G = "3g"
    CELLULAR_2G = "2g"
    SLOW_2G = "slow-2g"
    OFFLINE = "offline"


class DeviceClass(str, Enum):
    """Device performance classes"""
    HIGH_END = "high_end"        # Latest flagship devices
    MID_RANGE = "mid_range"      # Mid-range devices
    LOW_END = "low_end"          # Entry-level devices
    LEGACY = "legacy"            # Older devices


@dataclass
class MobileContext:
    """Mobile device context for optimization"""
    device_class: DeviceClass
    connection_type: ConnectionType
    screen_density: float
    screen_width: int
    screen_height: int
    memory_gb: float
    cpu_cores: int
    battery_level: Optional[float] = None
    is_power_save_mode: bool = False
    preferred_image_format: str = "webp"
    supports_lazy_loading: bool = True


@dataclass
class OptimizationProfile:
    """Performance optimization profile"""
    name: str
    max_response_size_kb: int
    max_image_width: int
    max_image_height: int
    image_quality: int  # 1-100
    enable_compression: bool
    enable_caching: bool
    lazy_load_threshold: int
    pagination_limit: int
    reduce_precision: bool
    exclude_heavy_fields: List[str]
    cache_ttl_seconds: int


class MobilePerformanceOptimizer:
    """Service for optimizing mobile performance"""

    def __init__(self):
        self.optimization_profiles = self._initialize_profiles()
        self.request_metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _initialize_profiles(self) -> Dict[DeviceClass, OptimizationProfile]:
        """Initialize optimization profiles for different device classes"""

        return {
            DeviceClass.HIGH_END: OptimizationProfile(
                name="High-End Device",
                max_response_size_kb=1024,  # 1MB
                max_image_width=1920,
                max_image_height=1080,
                image_quality=85,
                enable_compression=True,
                enable_caching=True,
                lazy_load_threshold=10,
                pagination_limit=50,
                reduce_precision=False,
                exclude_heavy_fields=[],
                cache_ttl_seconds=3600
            ),
            DeviceClass.MID_RANGE: OptimizationProfile(
                name="Mid-Range Device",
                max_response_size_kb=512,   # 512KB
                max_image_width=1280,
                max_image_height=720,
                image_quality=75,
                enable_compression=True,
                enable_caching=True,
                lazy_load_threshold=15,
                pagination_limit=25,
                reduce_precision=True,
                exclude_heavy_fields=["detailed_analytics", "raw_data"],
                cache_ttl_seconds=1800
            ),
            DeviceClass.LOW_END: OptimizationProfile(
                name="Low-End Device",
                max_response_size_kb=256,   # 256KB
                max_image_width=800,
                max_image_height=600,
                image_quality=60,
                enable_compression=True,
                enable_caching=True,
                lazy_load_threshold=20,
                pagination_limit=15,
                reduce_precision=True,
                exclude_heavy_fields=["detailed_analytics", "raw_data", "full_history", "metadata"],
                cache_ttl_seconds=900
            ),
            DeviceClass.LEGACY: OptimizationProfile(
                name="Legacy Device",
                max_response_size_kb=128,   # 128KB
                max_image_width=480,
                max_image_height=320,
                image_quality=50,
                enable_compression=True,
                enable_caching=True,
                lazy_load_threshold=25,
                pagination_limit=10,
                reduce_precision=True,
                exclude_heavy_fields=["detailed_analytics", "raw_data", "full_history", "metadata", "debug_info"],
                cache_ttl_seconds=600
            )
        }

    def detect_mobile_context(self, request: Request) -> MobileContext:
        """Detect mobile context from request headers"""

        user_agent = request.headers.get("user-agent", "").lower()

        # Simple device detection (in production, use a proper device detection library)
        device_class = DeviceClass.MID_RANGE
        if any(premium in user_agent for premium in ["iphone 14", "iphone 15", "pixel 7", "pixel 8", "galaxy s23", "galaxy s24"]):
            device_class = DeviceClass.HIGH_END
        elif any(budget in user_agent for budget in ["android 8", "android 9", "ios 12", "ios 13"]):
            device_class = DeviceClass.LEGACY
        elif any(entry in user_agent for entry in ["android 10", "android 11", "ios 14", "ios 15"]):
            device_class = DeviceClass.LOW_END

        # Detect connection type from headers
        connection_type = ConnectionType.WIFI
        connection_header = request.headers.get("connection-type", "").lower()
        if "cellular" in connection_header:
            if "5g" in connection_header:
                connection_type = ConnectionType.CELLULAR_5G
            elif "4g" in connection_header or "lte" in connection_header:
                connection_type = ConnectionType.CELLULAR_4G
            elif "3g" in connection_header:
                connection_type = ConnectionType.CELLULAR_3G
            else:
                connection_type = ConnectionType.CELLULAR_2G

        # Get device info from headers (many mobile apps send custom headers)
        screen_width = int(request.headers.get("x-screen-width", "375"))
        screen_height = int(request.headers.get("x-screen-height", "667"))
        screen_density = float(request.headers.get("x-screen-density", "2.0"))
        memory_gb = float(request.headers.get("x-device-memory", "4.0"))
        cpu_cores = int(request.headers.get("x-cpu-cores", "4"))
        battery_level = request.headers.get("x-battery-level")
        battery_level = float(battery_level) if battery_level else None

        return MobileContext(
            device_class=device_class,
            connection_type=connection_type,
            screen_density=screen_density,
            screen_width=screen_width,
            screen_height=screen_height,
            memory_gb=memory_gb,
            cpu_cores=cpu_cores,
            battery_level=battery_level,
            is_power_save_mode=request.headers.get("x-power-save", "false").lower() == "true",
            preferred_image_format=request.headers.get("accept", "").split(",")[0] if "webp" in request.headers.get("accept", "") else "jpeg"
        )

    def optimize_response(
        self,
        data: Dict[str, Any],
        mobile_context: MobileContext,
        request_path: str = "unknown"
    ) -> Dict[str, Any]:
        """Optimize response data for mobile device"""

        start_time = time.time()

        # Get optimization profile
        profile = self.optimization_profiles[mobile_context.device_class]

        # Apply optimizations
        optimized_data = self._apply_optimizations(data, profile, mobile_context)

        # Track optimization metrics
        optimization_time = time.time() - start_time
        self._track_optimization_metrics(request_path, mobile_context, optimization_time, data, optimized_data)

        return optimized_data

    def _apply_optimizations(
        self,
        data: Dict[str, Any],
        profile: OptimizationProfile,
        context: MobileContext
    ) -> Dict[str, Any]:
        """Apply specific optimizations based on profile"""

        optimized = data.copy()

        # Remove heavy fields
        for field in profile.exclude_heavy_fields:
            if field in optimized:
                del optimized[field]

        # Optimize lists and pagination
        optimized = self._optimize_lists(optimized, profile)

        # Optimize images
        optimized = self._optimize_images(optimized, profile, context)

        # Reduce precision for numbers
        if profile.reduce_precision:
            optimized = self._reduce_number_precision(optimized)

        # Optimize text fields
        optimized = self._optimize_text_fields(optimized, profile)

        # Add mobile-specific metadata
        optimized["_mobile_optimized"] = {
            "profile": profile.name,
            "device_class": context.device_class,
            "connection_type": context.connection_type,
            "optimizations_applied": self._get_applied_optimizations(profile)
        }

        return optimized

    def _optimize_lists(self, data: Dict[str, Any], profile: OptimizationProfile) -> Dict[str, Any]:
        """Optimize lists by applying pagination"""

        optimized = data.copy()

        for key, value in data.items():
            if isinstance(value, list) and len(value) > profile.pagination_limit:
                # Truncate list and add pagination info
                optimized[key] = value[:profile.pagination_limit]
                optimized[f"{key}_pagination"] = {
                    "total_count": len(value),
                    "page_size": profile.pagination_limit,
                    "has_more": True,
                    "next_page": 2
                }
            elif isinstance(value, dict):
                optimized[key] = self._optimize_lists(value, profile)

        return optimized

    def _optimize_images(
        self,
        data: Dict[str, Any],
        profile: OptimizationProfile,
        context: MobileContext
    ) -> Dict[str, Any]:
        """Optimize image references"""

        optimized = data.copy()

        for key, value in data.items():
            if isinstance(value, str) and any(ext in value for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                # Add optimization parameters to image URLs
                separator = "&" if "?" in value else "?"
                optimized[key] = (
                    f"{value}{separator}"
                    f"w={profile.max_image_width}&"
                    f"h={profile.max_image_height}&"
                    f"q={profile.image_quality}&"
                    f"format={context.preferred_image_format}"
                )
            elif isinstance(value, dict) and "url" in value and "width" in value and "height" in value:
                # Optimize image object
                optimized[key] = {
                    **value,
                    "url": self._optimize_image_url(value["url"], profile, context),
                    "optimized_width": min(value.get("width", 0), profile.max_image_width),
                    "optimized_height": min(value.get("height", 0), profile.max_image_height)
                }
            elif isinstance(value, dict):
                optimized[key] = self._optimize_images(value, profile, context)
            elif isinstance(value, list):
                optimized[key] = [
                    self._optimize_images(item, profile, context) if isinstance(item, dict) else item
                    for item in value
                ]

        return optimized

    def _optimize_image_url(self, url: str, profile: OptimizationProfile, context: MobileContext) -> str:
        """Optimize a single image URL"""

        separator = "&" if "?" in url else "?"
        return (
            f"{url}{separator}"
            f"w={profile.max_image_width}&"
            f"h={profile.max_image_height}&"
            f"q={profile.image_quality}&"
            f"format={context.preferred_image_format}"
        )

    def _reduce_number_precision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce precision of floating point numbers"""

        optimized = data.copy()

        for key, value in data.items():
            if isinstance(value, float):
                # Round to 2 decimal places for most numbers
                optimized[key] = round(value, 2)
            elif isinstance(value, dict):
                optimized[key] = self._reduce_number_precision(value)
            elif isinstance(value, list):
                optimized[key] = [
                    self._reduce_number_precision(item) if isinstance(item, dict)
                    else round(item, 2) if isinstance(item, float)
                    else item
                    for item in value
                ]

        return optimized

    def _optimize_text_fields(self, data: Dict[str, Any], profile: OptimizationProfile) -> Dict[str, Any]:
        """Optimize text fields by truncating long content"""

        optimized = data.copy()
        max_text_length = 500 if profile.max_response_size_kb < 300 else 1000

        for key, value in data.items():
            if isinstance(value, str) and len(value) > max_text_length:
                # Truncate long text fields
                optimized[key] = value[:max_text_length] + "..."
                optimized[f"{key}_truncated"] = True
            elif isinstance(value, dict):
                optimized[key] = self._optimize_text_fields(value, profile)

        return optimized

    def _get_applied_optimizations(self, profile: OptimizationProfile) -> List[str]:
        """Get list of applied optimizations"""

        optimizations = []

        if profile.exclude_heavy_fields:
            optimizations.append("heavy_fields_removed")

        if profile.reduce_precision:
            optimizations.append("number_precision_reduced")

        if profile.pagination_limit < 50:
            optimizations.append("list_pagination_applied")

        optimizations.extend([
            "image_optimization",
            "text_truncation",
            "mobile_context_aware"
        ])

        return optimizations

    def _track_optimization_metrics(
        self,
        request_path: str,
        context: MobileContext,
        optimization_time: float,
        original_data: Dict[str, Any],
        optimized_data: Dict[str, Any]
    ):
        """Track optimization performance metrics"""

        if request_path not in self.request_metrics:
            self.request_metrics[request_path] = []

        # Calculate size reduction
        original_size = len(json.dumps(original_data))
        optimized_size = len(json.dumps(optimized_data))
        size_reduction_percent = ((original_size - optimized_size) / original_size) * 100

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "device_class": context.device_class,
            "connection_type": context.connection_type,
            "optimization_time_ms": optimization_time * 1000,
            "original_size_bytes": original_size,
            "optimized_size_bytes": optimized_size,
            "size_reduction_percent": size_reduction_percent,
            "battery_level": context.battery_level,
            "power_save_mode": context.is_power_save_mode
        }

        self.request_metrics[request_path].append(metrics)

        # Keep only last 100 metrics per path
        if len(self.request_metrics[request_path]) > 100:
            self.request_metrics[request_path] = self.request_metrics[request_path][-100:]

    def compress_response(self, data: str, context: MobileContext) -> bytes:
        """Compress response data for mobile"""

        profile = self.optimization_profiles[context.device_class]

        if profile.enable_compression:
            # Use gzip compression for responses
            return gzip.compress(data.encode('utf-8'))

        return data.encode('utf-8')

    def should_enable_lazy_loading(self, context: MobileContext, item_count: int) -> bool:
        """Determine if lazy loading should be enabled"""

        profile = self.optimization_profiles[context.device_class]
        return item_count >= profile.lazy_load_threshold

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization performance statistics"""

        total_requests = sum(len(metrics) for metrics in self.request_metrics.values())

        if total_requests == 0:
            return {"total_requests": 0}

        # Calculate aggregate metrics
        all_metrics = []
        for path_metrics in self.request_metrics.values():
            all_metrics.extend(path_metrics)

        avg_optimization_time = sum(m["optimization_time_ms"] for m in all_metrics) / len(all_metrics)
        avg_size_reduction = sum(m["size_reduction_percent"] for m in all_metrics) / len(all_metrics)

        # Device class distribution
        device_distribution = {}
        for metrics in all_metrics:
            device_class = metrics["device_class"]
            device_distribution[device_class] = device_distribution.get(device_class, 0) + 1

        # Connection type distribution
        connection_distribution = {}
        for metrics in all_metrics:
            connection_type = metrics["connection_type"]
            connection_distribution[connection_type] = connection_distribution.get(connection_type, 0) + 1

        return {
            "total_requests": total_requests,
            "avg_optimization_time_ms": round(avg_optimization_time, 2),
            "avg_size_reduction_percent": round(avg_size_reduction, 2),
            "device_distribution": device_distribution,
            "connection_distribution": connection_distribution,
            "paths_optimized": len(self.request_metrics),
            "cache_entries": len(self.cache)
        }

    def get_adaptive_settings(self, context: MobileContext) -> Dict[str, Any]:
        """Get adaptive settings based on device context"""

        profile = self.optimization_profiles[context.device_class]

        settings = {
            "lazy_loading_enabled": True,
            "image_lazy_threshold": profile.lazy_load_threshold,
            "pagination_size": profile.pagination_limit,
            "image_quality": profile.image_quality,
            "enable_animations": context.device_class in [DeviceClass.HIGH_END, DeviceClass.MID_RANGE],
            "enable_background_sync": not context.is_power_save_mode,
            "cache_strategy": "aggressive" if context.connection_type in [ConnectionType.CELLULAR_2G, ConnectionType.SLOW_2G] else "normal",
            "preload_next_page": context.connection_type == ConnectionType.WIFI and context.device_class == DeviceClass.HIGH_END,
            "max_concurrent_requests": 6 if context.device_class == DeviceClass.HIGH_END else 3,
            "request_timeout_ms": 30000 if context.connection_type in [ConnectionType.CELLULAR_2G, ConnectionType.SLOW_2G] else 10000
        }

        return settings


# Global performance optimizer instance
performance_optimizer: Optional[MobilePerformanceOptimizer] = None

def get_performance_optimizer() -> MobilePerformanceOptimizer:
    """Get the global performance optimizer instance"""
    global performance_optimizer
    if performance_optimizer is None:
        performance_optimizer = MobilePerformanceOptimizer()
    return performance_optimizer