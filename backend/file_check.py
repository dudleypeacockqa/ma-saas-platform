#!/usr/bin/env python3
"""
Simple file existence check for M&A Platform
"""

import os

def check_file_exists(file_path, description):
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        return f"[EXISTS] {description}: {size:,} bytes"
    else:
        return f"[MISSING] {description}"

def main():
    print("=" * 60)
    print("M&A PLATFORM - FILE VERIFICATION")
    print("=" * 60)

    # Core service files
    services = [
        ("app/services/financial_intelligence.py", "AI Financial Intelligence"),
        ("app/services/template_engine.py", "Template Engine"),
        ("app/services/offer_stack_generator.py", "Offer Stack Generator"),
        ("app/services/intelligent_deal_matching.py", "Deal Matching"),
        ("app/services/automated_valuation_engine.py", "Valuation Engine"),
    ]

    print("\nCORE M&A SERVICES:")
    for file_path, desc in services:
        print(f"  {check_file_exists(file_path, desc)}")

    # Check main files
    main_files = [
        ("app/main.py", "Main FastAPI App"),
        ("app/models/financial_models.py", "Financial Models"),
        ("app/models/documents.py", "Document Models"),
        ("requirements.txt", "Dependencies"),
    ]

    print("\nMAIN APPLICATION FILES:")
    for file_path, desc in main_files:
        print(f"  {check_file_exists(file_path, desc)}")

    # Calculate stats
    all_files = services + main_files
    existing = sum(1 for file_path, _ in all_files if os.path.exists(file_path))
    total = len(all_files)

    print(f"\nSTATUS: {existing}/{total} files exist ({existing/total*100:.1f}%)")

    if existing == total:
        print("STATUS: ALL FILES IMPLEMENTED!")
    else:
        print(f"STATUS: {total-existing} files missing")

if __name__ == "__main__":
    main()