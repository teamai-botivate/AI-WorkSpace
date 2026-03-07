import re

base = 'backend/app/agents/hr_support/routers'
for fn in ['company_router.py', 'auth_router.py', 'chat_router.py', 'approval_router.py']:
    fpath = f'{base}/{fn}'
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content.replace('prefix="/api/', 'prefix="/')
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed prefix in {fn}')
    else:
        print(f'No prefix change in {fn}')
