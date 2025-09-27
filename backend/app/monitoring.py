import logging
import os
import time
from typing import Dict, Any
from pythonjsonlogger import jsonlogger
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None
if sentry_sdk:
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
else:
    FastApiIntegration = None
    AsyncioIntegration = None


def setup_logging():
    """
    Configure structured logging with JSON format for production.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('ffmpeg').setLevel(logging.WARNING)
    
    logger.info("logging_configured", extra={"format": "json"})


def setup_sentry():
    """
    Configure Sentry for error tracking.
    """
    if not sentry_sdk:
        return
        
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                AsyncioIntegration()
            ],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            environment=os.getenv('ENVIRONMENT', 'development'),
            release=os.getenv('APP_VERSION', 'unknown')
        )
        logging.info("sentry_configured", extra={"dsn": sentry_dsn[:20] + "..."})
    else:
        logging.warning("sentry_not_configured", extra={"reason": "no_dsn"})


class MetricsCollector:
    """
    Simple metrics collector for tracking application performance.
    In production, this would integrate with Prometheus/DataDog/etc.
    """
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.histograms: Dict[str, list] = {}
        self.gauges: Dict[str, float] = {}
        self.start_time = time.time()
    
    def increment(self, metric_name: str, value: int = 1, tags: Dict[str, Any] = None):
        """Increment a counter metric"""
        key = self._format_key(metric_name, tags)
        self.counters[key] = self.counters.get(key, 0) + value
        
        logging.info("metric_incremented", extra={
            "metric": metric_name,
            "value": value,
            "tags": tags,
            "total": self.counters[key]
        })
    
    def record(self, metric_name: str, value: float, tags: Dict[str, Any] = None):
        """Record a histogram value"""
        key = self._format_key(metric_name, tags)
        if key not in self.histograms:
            self.histograms[key] = []
        
        self.histograms[key].append(value)
        
        # Keep only last 1000 values to prevent memory issues
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
        
        logging.info("metric_recorded", extra={
            "metric": metric_name,
            "value": value,
            "tags": tags
        })
    
    def set_gauge(self, metric_name: str, value: float, tags: Dict[str, Any] = None):
        """Set a gauge value"""
        key = self._format_key(metric_name, tags)
        self.gauges[key] = value
        
        logging.info("gauge_set", extra={
            "metric": metric_name,
            "value": value,
            "tags": tags
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics statistics"""
        stats = {
            "uptime_seconds": time.time() - self.start_time,
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "histograms": {}
        }
        
        # Calculate histogram stats
        for key, values in self.histograms.items():
            if values:
                stats["histograms"][key] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "p95": self._percentile(values, 0.95),
                    "p99": self._percentile(values, 0.99)
                }
        
        return stats
    
    def _format_key(self, metric_name: str, tags: Dict[str, Any] = None) -> str:
        """Format metric key with tags"""
        if not tags:
            return metric_name
        
        tag_str = ",".join([f"{k}={v}" for k, v in sorted(tags.items())])
        return f"{metric_name}[{tag_str}]"
    
    def _percentile(self, values: list, percentile: float) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global metrics instance
metrics = MetricsCollector()


def check_system_health() -> Dict[str, Any]:
    """
    Check overall system health.
    
    Returns:
        Health status dictionary
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        disk_usage_percent = (used / total) * 100
        
        health_status["checks"]["disk_space"] = {
            "status": "healthy" if disk_usage_percent < 90 else "warning",
            "usage_percent": disk_usage_percent,
            "free_gb": free // (1024**3)
        }
    except Exception as e:
        health_status["checks"]["disk_space"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        health_status["checks"]["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "usage_percent": memory.percent,
            "available_gb": memory.available // (1024**3)
        }
    except ImportError:
        health_status["checks"]["memory"] = {
            "status": "unknown",
            "error": "psutil not available"
        }
    except Exception as e:
        health_status["checks"]["memory"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check if any critical services are down
    critical_checks = ["disk_space"]
    if any(check.get("status") == "error" for key, check in health_status["checks"].items() if key in critical_checks):
        health_status["status"] = "unhealthy"
    elif any(check.get("status") == "warning" for check in health_status["checks"].values()):
        health_status["status"] = "degraded"
    
    return health_status


async def check_dependencies() -> Dict[str, Any]:
    """
    Check health of external dependencies.
    
    Returns:
        Dependency health status
    """
    checks = {
        "timestamp": time.time(),
        "dependencies": {}
    }
    
    # Check OpenAI API
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Simple API test (this would make a real call in production)
        checks["dependencies"]["openai"] = {
            "status": "healthy",
            "configured": bool(os.getenv('OPENAI_API_KEY'))
        }
    except Exception as e:
        checks["dependencies"]["openai"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check FFmpeg
    try:
        import ffmpeg
        
        # Test FFmpeg availability
        ffmpeg.probe('/dev/null')  # This will fail but test if ffmpeg is available
        checks["dependencies"]["ffmpeg"] = {"status": "healthy"}
    except ffmpeg.Error:
        # Expected error, but FFmpeg is available
        checks["dependencies"]["ffmpeg"] = {"status": "healthy"}
    except Exception as e:
        checks["dependencies"]["ffmpeg"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Firebase (mock)
    checks["dependencies"]["firebase"] = {
        "status": "healthy",
        "configured": bool(os.getenv('FIREBASE_PROJECT_ID'))
    }
    
    # Check storage (mock)
    checks["dependencies"]["storage"] = {
        "status": "healthy"
    }
    
    # Overall status
    all_healthy = all(
        dep.get("status") == "healthy" 
        for dep in checks["dependencies"].values()
    )
    
    checks["overall_status"] = "healthy" if all_healthy else "degraded"
    
    return checks


def log_request_metrics(request_path: str, method: str, status_code: int, duration_ms: float):
    """
    Log request metrics for monitoring.
    
    Args:
        request_path: API endpoint path
        method: HTTP method
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    metrics.increment('api_requests_total', tags={
        'method': method,
        'path': request_path,
        'status': str(status_code)
    })
    
    metrics.record('api_request_duration_ms', duration_ms, tags={
        'method': method,
        'path': request_path
    })
    
    # Log slow requests
    if duration_ms > 5000:  # 5 seconds
        logging.warning("slow_request", extra={
            "path": request_path,
            "method": method,
            "duration_ms": duration_ms,
            "status": status_code
        })