#!/usr/bin/env python3
"""
Systematic endpoint audit script for Phase 4.

Analyzes all router files to identify:
1. Response format patterns
2. Error messages (for extraction to constants)
3. HTTP status code usage
4. OpenAPI compliance issues
"""

import re
import os
from pathlib import Path
from collections import defaultdict

ROUTERS_DIR = Path("app/routers")

# Patterns to identify
STATUS_CODE_PATTERN = r'status_code\s*=\s*(status\.HTTP_\w+|\d+)'
HTTP_EXCEPTION_PATTERN = r'HTTPException\([^)]*detail\s*=\s*["\']([^"\']+)["\']'
RETURN_PATTERN = r'return\s+({.*?}|\[.*?\]|Response|JSONResponse)'


def analyze_router_file(filepath):
    """Analyze a single router file."""
    with open(filepath, 'r') as f:
        content = f.read()

    results = {
        'file': str(filepath),
        'status_codes': [],
        'error_messages': [],
        'response_patterns': [],
        'endpoints': []
    }

    # Find all status codes
    for match in re.finditer(STATUS_CODE_PATTERN, content):
        results['status_codes'].append(match.group(1))

    # Find all error messages
    for match in re.finditer(HTTP_EXCEPTION_PATTERN, content):
        results['error_messages'].append(match.group(1))

    # Count endpoints (router decorators)
    endpoints = re.findall(r'@router\.(get|post|put|patch|delete)\(["\']([^"\']+)', content)
    results['endpoints'] = [(method.upper(), path) for method, path in endpoints]

    return results


def main():
    """Run the audit."""
    print("=" * 80)
    print("BACKEND API ENDPOINT AUDIT - PHASE 4")
    print("=" * 80)
    print()

    all_status_codes = defaultdict(int)
    all_error_messages = []
    total_endpoints = 0

    # Analyze each router file
    router_files = sorted(ROUTERS_DIR.glob("*.py"))
    router_files = [f for f in router_files if f.name != "__init__.py"]

    for router_file in router_files:
        results = analyze_router_file(router_file)

        if not results['endpoints']:
            continue

        print(f"\n{'=' * 80}")
        print(f"FILE: {router_file.name}")
        print(f"{'=' * 80}")
        print(f"Endpoints: {len(results['endpoints'])}")

        # Status codes used
        if results['status_codes']:
            print(f"\nStatus Codes Used:")
            for code in set(results['status_codes']):
                count = results['status_codes'].count(code)
                print(f"  - {code}: {count} times")
                all_status_codes[code] += count

        # Error messages
        if results['error_messages']:
            print(f"\nError Messages ({len(results['error_messages'])}): ")
            for msg in results['error_messages'][:5]:  # Show first 5
                print(f"  - {msg[:60]}...")
            if len(results['error_messages']) > 5:
                print(f"  ... and {len(results['error_messages']) - 5} more")

        total_endpoints += len(results['endpoints'])
        all_error_messages.extend(results['error_messages'])

    # Summary
    print(f"\n\n{'=' * 80}")
    print("AUDIT SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Router Files: {len(router_files)}")
    print(f"Total Endpoints: {total_endpoints}")
    print(f"Total Error Messages: {len(all_error_messages)}")
    print(f"\nStatus Code Distribution:")
    for code, count in sorted(all_status_codes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {code}: {count} occurrences")

    # Recommendations
    print(f"\n{'=' * 80}")
    print("RECOMMENDATIONS")
    print(f"{'=' * 80}")
    print(f"1. Extract {len(all_error_messages)} error messages to app/core/messages.py")
    print(f"2. Standardize status code usage (found {len(all_status_codes)} different codes)")
    print(f"3. Review {total_endpoints} endpoints for response format consistency")
    print(f"4. Verify OpenAPI spec compliance for all endpoints")


if __name__ == "__main__":
    main()
