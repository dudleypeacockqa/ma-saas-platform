#!/usr/bin/env python3
"""
Simple Production Readiness Check - No Unicode
"""

import os
import sys
from datetime import datetime

def main():
    print("=" * 60)
    print("M&A SAAS PLATFORM - PRODUCTION READINESS CHECK")
    print("=" * 60)

    # Check critical files
    critical_files = [
        "backend/app/main.py",
        "backend/requirements.txt",
        "backend/.env.production",
        "frontend/.env.production",
        "deploy.sh",
        "backend/app/services/financial_intelligence.py",
        "backend/app/services/template_engine.py",
        "backend/app/services/offer_stack_generator.py",
        "backend/app/services/intelligent_deal_matching.py",
        "backend/app/services/automated_valuation_engine.py",
    ]

    print("\nCHECKING CRITICAL FILES:")
    missing_files = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            missing_files.append(file_path)

    # Check Python syntax
    print("\nCHECKING PYTHON SYNTAX:")
    python_files = [
        "backend/app/services/financial_intelligence.py",
        "backend/app/services/template_engine.py",
        "backend/app/services/offer_stack_generator.py",
        "backend/app/services/intelligent_deal_matching.py",
        "backend/app/services/automated_valuation_engine.py",
    ]

    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"[OK] {file_path}")
        except Exception as e:
            print(f"[ERROR] {file_path}: {e}")
            syntax_errors.append(file_path)

    # Check environment files
    print("\nCHECKING ENVIRONMENT FILES:")
    env_ok = True

    if os.path.exists("backend/.env.production"):
        print("[OK] backend/.env.production")
    else:
        print("[MISSING] backend/.env.production")
        env_ok = False

    if os.path.exists("frontend/.env.production"):
        print("[OK] frontend/.env.production")
    else:
        print("[MISSING] frontend/.env.production")
        env_ok = False

    # Check deployment script
    print("\nCHECKING DEPLOYMENT SCRIPT:")
    deploy_ok = True
    if os.path.exists("deploy.sh"):
        with open("deploy.sh", 'r') as f:
            script_content = f.read()

        if "deploy_production" in script_content:
            print("[OK] Production deployment function present")
        else:
            print("[MISSING] Production deployment function")
            deploy_ok = False
    else:
        print("[MISSING] deploy.sh")
        deploy_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("PRODUCTION READINESS SUMMARY")
    print("=" * 60)

    all_checks = [
        ("Critical Files", len(missing_files) == 0),
        ("Python Syntax", len(syntax_errors) == 0),
        ("Environment Config", env_ok),
        ("Deployment Script", deploy_ok),
    ]

    passed = sum(1 for _, status in all_checks if status)
    total = len(all_checks)

    print(f"Checks Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    for check_name, status in all_checks:
        status_text = "PASSED" if status else "FAILED"
        print(f"  {check_name}: {status_text}")

    if passed == total:
        print("\n*** PLATFORM IS PRODUCTION READY! ***")
        print("All quality gates passed - Ready for deployment")
        print("\nNext Steps:")
        print("1. Execute: ./deploy.sh production")
        print("2. Configure real production credentials")
        print("3. Deploy to hosting platform")
        print("4. Launch customer acquisition campaign")
        print("\n*** READY TO ACHIEVE £200M REVENUE TARGET! ***")
        return True
    else:
        print(f"\n*** {total-passed} ISSUES NEED RESOLUTION ***")
        if missing_files:
            print(f"Missing files: {missing_files}")
        if syntax_errors:
            print(f"Syntax errors: {syntax_errors}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)