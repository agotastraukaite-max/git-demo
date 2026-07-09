#!/usr/bin/env python
import os

os.chdir(r'C:\Users\AgotaStraukaite\.copilot\chats\39969f8e-4918-4663-899d-f248a6ddd5e4')

# Read the test file
with open('tests/test_logsum.py', 'r') as f:
    content = f.read()

# Replace the problematic fixture
old_timestamp = "{'timestamp': '2026-07-09', 'level': 'ERROR', 'service': 'svc', 'message': 'also bad'},"
new_timestamp = "{'timestamp': 'invalid-ts-2026-07-09', 'level': 'ERROR', 'service': 'svc', 'message': 'also bad'},"

if old_timestamp in content:
    content = content.replace(old_timestamp, new_timestamp)
    with open('tests/test_logsum.py', 'w') as f:
        f.write(content)
    print("[FIXED] Malformed timestamp test fixture")
    print("  Changed: '2026-07-09' -> 'invalid-ts-2026-07-09'")
else:
    print("[ERROR] Could not find fixture to fix")
