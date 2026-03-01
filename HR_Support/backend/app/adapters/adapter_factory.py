"""
Botivate HR Support - Adapter Factory
Dynamically returns the correct database adapter based on the database type.
New adapters can be plugged in here without modifying any other code.

OPTIMIZED: Connection caching — reuses OAuth-authenticated adapters for 45 min.
Data is still fetched fresh every time, only the CONNECTION is cached.
"""

import time
from typing import Dict, Any, Optional, Tuple
from app.adapters.base_adapter import BaseDatabaseAdapter
from app.adapters.google_sheets_adapter import GoogleSheetsAdapter
from app.models.models import DatabaseType


# ── Registry: map DatabaseType → Adapter Class ────────────
ADAPTER_REGISTRY: Dict[DatabaseType, type] = {
    DatabaseType.GOOGLE_SHEETS: GoogleSheetsAdapter,
    # Future adapters:
    # DatabaseType.POSTGRESQL: PostgreSQLAdapter,
    # DatabaseType.MONGODB: MongoDBAdapter,
}


# ── Connection Cache ──────────────────────────────────────
# Key: (db_type, spreadsheet_id) → (adapter_instance, created_timestamp)
# TTL: 45 minutes (OAuth tokens typically valid for 1 hour)
_adapter_cache: Dict[str, Tuple[BaseDatabaseAdapter, float]] = {}
_CACHE_TTL_SECONDS = 45 * 60  # 45 minutes


def _make_cache_key(db_type: DatabaseType, connection_config: Dict[str, Any]) -> str:
    """Generate a unique cache key from db type and spreadsheet ID."""
    spreadsheet_id = connection_config.get("spreadsheet_id", "")
    # Extract ID from URL if needed
    if "spreadsheets/d/" in spreadsheet_id:
        parts = spreadsheet_id.split("spreadsheets/d/")
        if len(parts) > 1:
            spreadsheet_id = parts[1].split("/")[0]
    refresh_token = connection_config.get("google_refresh_token", "")[:20]  # Partial for uniqueness
    return f"{db_type.value}:{spreadsheet_id}:{refresh_token}"


async def get_cached_adapter(
    db_type: DatabaseType,
    connection_config: Dict[str, Any],
    refresh_token: Optional[str] = None,
) -> BaseDatabaseAdapter:
    """
    Get a cached adapter connection. Reuses OAuth-authenticated adapters.
    Data is always fetched fresh — only the CONNECTION is cached.
    """
    cache_key = _make_cache_key(db_type, connection_config)
    now = time.time()

    # Check cache
    if cache_key in _adapter_cache:
        adapter, created_at = _adapter_cache[cache_key]
        age = now - created_at
        if age < _CACHE_TTL_SECONDS:
            print(f"[ADAPTER CACHE] ♻️ Reusing cached connection (age: {int(age)}s)")
            return adapter
        else:
            print(f"[ADAPTER CACHE] ⏰ Cache expired (age: {int(age)}s). Reconnecting...")
            del _adapter_cache[cache_key]

    # Create new adapter and cache it
    print(f"[ADAPTER CACHE] 🔌 Creating new connection for {db_type.value}...")
    adapter = await get_adapter(db_type, connection_config, refresh_token)
    _adapter_cache[cache_key] = (adapter, now)
    return adapter


def invalidate_adapter_cache(db_type: DatabaseType = None, connection_config: Dict[str, Any] = None):
    """Clear adapter cache. Call when credentials change."""
    if db_type and connection_config:
        cache_key = _make_cache_key(db_type, connection_config)
        _adapter_cache.pop(cache_key, None)
    else:
        _adapter_cache.clear()
    print(f"[ADAPTER CACHE] 🗑️ Cache invalidated.")


async def get_adapter(
    db_type: DatabaseType,
    connection_config: Dict[str, Any],
    refresh_token: Optional[str] = None,
) -> BaseDatabaseAdapter:
    """
    Factory function: returns a NEW connected adapter instance.
    Use get_cached_adapter() for performance in chat flows.
    """
    adapter_class = ADAPTER_REGISTRY.get(db_type)
    if not adapter_class:
        raise ValueError(f"No adapter registered for database type: {db_type.value}. "
                         f"Supported types: {[t.value for t in ADAPTER_REGISTRY.keys()]}")

    adapter = adapter_class()
    await adapter.connect(connection_config, refresh_token=refresh_token)
    return adapter
