"""Quick import test for both agents."""
import sys
import traceback

print("=" * 50)
print("Testing Resume Screening Agent...")
try:
    from app.agents.resume_screening import router as rs_router
    print("  Resume Screening: OK")
except Exception as e:
    print(f"  Resume Screening: FAIL - {e}")
    traceback.print_exc()

print("=" * 50)
print("Testing HR Support Agent...")
try:
    from app.agents.hr_support import router as hr_router
    print("  HR Support: OK")
except Exception as e:
    print(f"  HR Support: FAIL - {e}")
    traceback.print_exc()

print("=" * 50)
print("Testing Main App...")
try:
    from app.main import app
    print("  Main App: OK")
except Exception as e:
    print(f"  Main App: FAIL - {e}")
    traceback.print_exc()

print("=" * 50)
print("ALL TESTS DONE")
