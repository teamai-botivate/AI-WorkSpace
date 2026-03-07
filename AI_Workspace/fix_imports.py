"""
Fix imports in HR Support agent files for the plugin structure.
Original: from app.X import Y
New: relative imports based on location within hr_support plugin
"""
import os
import re

hr_base = os.path.join("backend", "app", "agents", "hr_support")

def fix_hr_imports(filepath, content):
    replacements = [
        (r'from app\.config import settings', 'from ....config import get_settings'),
        (r'from app\.config import', 'from ....config import'),
        (r'from app\.database import', 'from ....core.database import'),
        (r'from app\.models\.models import', 'from ..models.models import'),
        (r'from app\.models\.schemas import', 'from ..models.schemas import'),
        (r'from app\.services\.(\w+) import', r'from ..services.\1 import'),
        (r'from app\.services import', 'from ..services import'),
        (r'from app\.agents\.(\w+) import', r'from ..agents.\1 import'),
        (r'from app\.utils\.(\w+) import', r'from ..utils.\1 import'),
        (r'from app\.adapters\.(\w+) import', r'from ..adapters.\1 import'),
    ]
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    if 'from ....config import get_settings' in content:
        content = content.replace(
            'from ....config import get_settings',
            'from ....config import get_settings\nsettings = get_settings()'
        )
    return content

count = 0
for root, dirs, files in os.walk(hr_base):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                content = fh.read()
            original = content
            content = fix_hr_imports(fpath, content)
            if content != original:
                with open(fpath, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                print(f'Fixed: {os.path.relpath(fpath, hr_base)}')
                count += 1
            else:
                print(f'No changes: {os.path.relpath(fpath, hr_base)}')

print(f'\nDone. Fixed {count} files.')
