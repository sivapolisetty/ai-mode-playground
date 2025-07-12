"""
Component Cache System for Dynamic UI Generation
Provides multi-level caching for UI component library information
"""
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ComponentCache:
    """Multi-level cache system for component library information"""
    
    def __init__(self, cache_dir: str = ".cache/components"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache files
        self.cache_file = self.cache_dir / "component_library.json"
        self.version_file = self.cache_dir / "version.txt"
        self.metadata_file = self.cache_dir / "metadata.json"
        
        # In-memory cache
        self._memory_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour default TTL
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "last_refresh": None
        }
    
    async def get_cached_components(self, components_path: Path, current_hash: str) -> Optional[Dict[str, Any]]:
        """Get components from cache with intelligent fallback"""
        
        # Level 1: Memory cache
        memory_result = await self._get_from_memory_cache()
        if memory_result:
            self.stats["hits"] += 1
            return memory_result
        
        # Level 2: File cache
        file_result = await self._get_from_file_cache(current_hash)
        if file_result:
            # Populate memory cache
            await self._save_to_memory_cache(file_result["data"])
            self.stats["hits"] += 1
            return file_result
        
        # Cache miss
        self.stats["misses"] += 1
        return None
    
    async def _get_from_memory_cache(self) -> Optional[Dict[str, Any]]:
        """Get components from in-memory cache"""
        try:
            current_time = time.time()
            
            if (self._memory_cache and 
                self._cache_timestamp and 
                (current_time - self._cache_timestamp) < self._cache_ttl):
                
                logger.info("Returning components from memory cache")
                return {
                    "success": True,
                    "data": self._memory_cache,
                    "source": "memory_cache",
                    "cached_at": self._cache_timestamp,
                    "cache_age": current_time - self._cache_timestamp
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Memory cache read failed: {e}")
            return None
    
    async def _get_from_file_cache(self, current_hash: str) -> Optional[Dict[str, Any]]:
        """Get components from file cache if valid"""
        try:
            if not self.cache_file.exists() or not self.version_file.exists():
                logger.info("File cache does not exist")
                return None
            
            # Check if component files changed
            with open(self.version_file, 'r') as f:
                cached_hash = f.read().strip()
            
            if current_hash != cached_hash:
                logger.info("Component files changed, file cache invalidated")
                return None
            
            # Load cached data
            with open(self.cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Load metadata if available
            metadata = {}
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            logger.info(f"Loaded {len(cached_data)} components from file cache")
            return {
                "success": True,
                "data": cached_data,
                "source": "file_cache",
                "cache_hash": current_hash,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"File cache read failed: {e}")
            return None
    
    async def save_to_cache(self, components: Dict[str, Any], current_hash: str, metadata: Dict[str, Any] = None):
        """Save components to both memory and file cache"""
        try:
            # Save to memory cache
            await self._save_to_memory_cache(components)
            
            # Save to file cache
            await self._save_to_file_cache(components, current_hash, metadata)
            
            self.stats["last_refresh"] = time.time()
            logger.info(f"Saved {len(components)} components to cache")
            
        except Exception as e:
            logger.error(f"Cache save failed: {e}")
    
    async def _save_to_memory_cache(self, components: Dict[str, Any]):
        """Save components to in-memory cache"""
        self._memory_cache = components.copy()
        self._cache_timestamp = time.time()
    
    async def _save_to_file_cache(self, components: Dict[str, Any], current_hash: str, metadata: Dict[str, Any] = None):
        """Save components to file cache"""
        try:
            # Save component data
            with open(self.cache_file, 'w') as f:
                json.dump(components, f, indent=2, default=str)
            
            # Save version hash
            with open(self.version_file, 'w') as f:
                f.write(current_hash)
            
            # Save metadata
            if metadata:
                with open(self.metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"File cache save failed: {e}")
            raise
    
    async def invalidate_cache(self):
        """Invalidate all cache levels"""
        try:
            # Clear memory cache
            self._memory_cache = {}
            self._cache_timestamp = None
            
            # Remove file cache
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.version_file.exists():
                self.version_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            
            self.stats["invalidations"] += 1
            logger.info("All cache levels invalidated")
            
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        try:
            info = {
                "memory_cache": {
                    "exists": bool(self._memory_cache),
                    "component_count": len(self._memory_cache) if self._memory_cache else 0,
                    "timestamp": self._cache_timestamp,
                    "age_seconds": time.time() - self._cache_timestamp if self._cache_timestamp else None,
                    "ttl_seconds": self._cache_ttl
                },
                "file_cache": {
                    "exists": self.cache_file.exists(),
                    "size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
                    "modified": self.cache_file.stat().st_mtime if self.cache_file.exists() else None
                },
                "statistics": self.stats.copy(),
                "cache_directory": str(self.cache_dir)
            }
            
            # Calculate hit ratio
            total_requests = self.stats["hits"] + self.stats["misses"]
            if total_requests > 0:
                info["hit_ratio"] = self.stats["hits"] / total_requests
            else:
                info["hit_ratio"] = 0.0
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {"error": str(e)}
    
    def set_ttl(self, ttl_seconds: int):
        """Set time-to-live for memory cache"""
        self._cache_ttl = ttl_seconds
        logger.info(f"Cache TTL set to {ttl_seconds} seconds")


class ComponentWatcher:
    """File system watcher for automatic cache invalidation"""
    
    def __init__(self, cache_manager: ComponentCache, components_path: Path):
        self.cache_manager = cache_manager
        self.components_path = components_path
        self.debounce_delay = 2.0  # Wait 2 seconds after last change
        self.pending_invalidation = None
        self.is_watching = False
    
    async def start_watching(self):
        """Start watching for file changes"""
        try:
            # Note: This is a simplified watcher implementation
            # In production, you might want to use watchdog library
            self.is_watching = True
            logger.info(f"Started watching {self.components_path} for changes")
            
            # Start background task to check for changes
            asyncio.create_task(self._watch_loop())
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
    
    async def _watch_loop(self):
        """Background loop to check for file changes"""
        last_hash = None
        
        while self.is_watching:
            try:
                # Simple polling approach - check every 5 seconds
                await asyncio.sleep(5)
                
                if not self.components_path.exists():
                    continue
                
                # Calculate current hash
                current_hash = self._get_directory_hash()
                
                if last_hash and current_hash != last_hash:
                    logger.info("Component files changed, scheduling cache invalidation")
                    await self.schedule_cache_invalidation()
                
                last_hash = current_hash
                
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    def _get_directory_hash(self) -> str:
        """Get hash of all component files"""
        import hashlib
        
        file_hashes = []
        
        for file_path in self.components_path.glob("**/*.tsx"):
            if file_path.is_file():
                stat = file_path.stat()
                file_info = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
                file_hashes.append(file_info)
        
        combined = "|".join(sorted(file_hashes))
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def schedule_cache_invalidation(self):
        """Schedule cache invalidation with debounce"""
        # Cancel previous invalidation
        if self.pending_invalidation:
            self.pending_invalidation.cancel()
        
        # Schedule new invalidation with debounce
        self.pending_invalidation = asyncio.create_task(
            self._debounced_invalidation()
        )
    
    async def _debounced_invalidation(self):
        """Perform cache invalidation after debounce delay"""
        try:
            await asyncio.sleep(self.debounce_delay)
            await self.cache_manager.invalidate_cache()
            logger.info("Cache invalidated due to file changes")
        except asyncio.CancelledError:
            logger.info("Cache invalidation cancelled")
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
    
    def stop_watching(self):
        """Stop watching for file changes"""
        self.is_watching = False
        if self.pending_invalidation:
            self.pending_invalidation.cancel()
        logger.info("Stopped watching for file changes")