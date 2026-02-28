"""
Botivate HR Support - Adapter Factory
Dynamically returns the correct database adapter based on the database type.
New adapters can be plugged in here without modifying any other code.

OPTIMIZED:
- Connection caching — reuses OAuth-authenticated adapters for 45 min.
- Employee data caching — caches employee records for 2 min (data freshness with speed).
- Prefetch support — warm the cache at login time.
"""

import time
import asyncio
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


# ── Employee Data Cache ───────────────────────────────────
# Key: "company_id:employee_id" → (record_dict, timestamp)
# TTL: 2 minutes — employee data doesn't change every second
_employee_data_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_DATA_CACHE_TTL_SECONDS = 120  # 2 minutes


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


# ── Employee Data Cache Functions ─────────────────────────

def get_cached_employee_data(company_id: str, employee_id: str) -> Optional[Dict[str, Any]]:
    """Get employee record from cache if fresh (< 2 min old)."""
    cache_key = f"{company_id}:{employee_id}"
    if cache_key in _employee_data_cache:
        record, ts = _employee_data_cache[cache_key]
        age = time.time() - ts
        if age < _DATA_CACHE_TTL_SECONDS:
            print(f"[DATA CACHE] ♻️ Using cached employee data for '{employee_id}' (age: {int(age)}s)")
            return record
        else:
            del _employee_data_cache[cache_key]
    return None


def set_cached_employee_data(company_id: str, employee_id: str, record: Dict[str, Any]):
    """Store employee record in cache."""
    cache_key = f"{company_id}:{employee_id}"
    _employee_data_cache[cache_key] = (record, time.time())
    print(f"[DATA CACHE] 💾 Cached employee data for '{employee_id}'")


def invalidate_employee_data_cache(company_id: str = None, employee_id: str = None):
    """Clear employee data cache. Call after data updates."""
    if company_id and employee_id:
        cache_key = f"{company_id}:{employee_id}"
        _employee_data_cache.pop(cache_key, None)
    else:
        _employee_data_cache.clear()
    print(f"[DATA CACHE] 🗑️ Employee data cache invalidated.")


async def prefetch_employee_data(
    db_type: DatabaseType,
    connection_config: Dict[str, Any],
    company_id: str,
    employee_id: str,
    primary_key: str,
    master_table: Optional[str] = None,
):
    """
    Background prefetch: warm the adapter + data caches at login time.
    Called as a fire-and-forget task so login response is NOT delayed.
    """
    try:
        # Warm adapter cache
        adapter = await get_cached_adapter(db_type, connection_config)
        # Warm employee data cache
        record = await adapter.get_record_by_key(primary_key, employee_id, table_name=master_table)
        if record:
            set_cached_employee_data(company_id, employee_id, record)
        else:
            # Case-insensitive fallback
            all_records = await adapter.get_all_records(table_name=master_table)
            for rec in all_records:
                if str(rec.get(primary_key, "")).strip().lower() == employee_id.strip().lower():
                    set_cached_employee_data(company_id, employee_id, rec)
                    break
        print(f"[PREFETCH] ✅ Background prefetch complete for '{employee_id}'")
    except Exception as e:
        print(f"[PREFETCH] ⚠️ Background prefetch failed (non-fatal): {e}")


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
