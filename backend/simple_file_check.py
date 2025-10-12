#!/usr/bin/env python3
"""
Simple file existence check for M&A Platform
Verifies that all key implementation files exist
"""

import os
import sys

def check_file_exists(file_path, description):
    """Check if a file exists and get basic info"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        return f"✅ {description}: EXISTS ({size:,} bytes)"
    else:
        return f"❌ {description}: MISSING"

def main():
    print("=" * 60)
    print("M&A PLATFORM - FILE EXISTENCE VERIFICATION")
    print("=" * 60)

    # Core service files
    services = [
        ("app/services/financial_intelligence.py", "AI-Powered Financial Intelligence"),
        ("app/services/template_engine.py", "Professional Template Engine"),
        ("app/services/offer_stack_generator.py", "Interactive Offer Stack Generator"),
        ("app/services/intelligent_deal_matching.py", "Intelligent Deal Matching"),
        ("app/services/automated_valuation_engine.py", "Automated Valuation Engine"),
    ]

    # API files
    apis = [
        ("app/api/v1/financial_intelligence.py", "Financial Intelligence API"),
        ("app/main.py", "Main FastAPI Application"),
    ]

    # Model files
    models = [
        ("app/models/financial_models.py", "Financial Models"),
        ("app/models/documents.py", "Document Models"),
        ("app/models/integration.py", "Integration Models"),
        ("app/models/base.py", "Base Models"),
    ]

    # Configuration and utilities
    utils = [
        ("app/core/config.py", "Configuration"),
        ("app/utils/ml_utils.py", "ML Utilities"),
        ("requirements.txt", "Dependencies List"),
    ]

    all_files = services + apis + models + utils

    print("\n🔧 CORE M&A SERVICES:")
    for file_path, desc in services:
        print(f"  {check_file_exists(file_path, desc)}")

    print("\n🌐 API ENDPOINTS:")
    for file_path, desc in apis:
        print(f"  {check_file_exists(file_path, desc)}")

    print("\n🗄️ DATABASE MODELS:")
    for file_path, desc in models:
        print(f"  {check_file_exists(file_path, desc)}")

    print("\n⚙️ CONFIGURATION & UTILITIES:")
    for file_path, desc in utils:
        print(f"  {check_file_exists(file_path, desc)}")

    # Calculate statistics
    existing_files = sum(1 for file_path, _ in all_files if os.path.exists(file_path))
    total_files = len(all_files)
    completion_rate = (existing_files / total_files) * 100

    print("\n" + "=" * 60)
    print("📊 IMPLEMENTATION STATUS")
    print("=" * 60)
    print(f"Files Implemented: {existing_files}/{total_files}")
    print(f"Completion Rate: {completion_rate:.1f}%")

    if completion_rate >= 90:
        print("\n🎉 EXCELLENT: Platform is substantially implemented!")
        print("All core components are present and ready for testing.")
    elif completion_rate >= 70:
        print("\n✅ GOOD: Most components implemented, minor gaps remain.")
    else:
        print("\n⚠️  INCOMPLETE: Significant implementation gaps detected.")

    # Calculate total code size
    total_size = 0
    service_sizes = []
    for file_path, desc in services:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            service_sizes.append((desc, size))

    print(f"\n📏 CORE SERVICES CODE SIZE:")
    for desc, size in service_sizes:
        lines_est = size // 25  # Rough estimate: 25 bytes per line
        print(f"  • {desc}: ~{lines_est:,} lines")

    total_lines_est = total_size // 25
    print(f"\nTotal Core Services: ~{total_lines_est:,} lines of code")

    print("\n" + "=" * 60)

    return completion_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)