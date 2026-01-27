#!/usr/bin/env python3
"""
Requirements Verification Script
Checks that all dependencies are installed and have no conflicts
"""

import subprocess
import sys
from packaging import version

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def main():
    print("=" * 60)
    print("Python Requirements Verification")
    print("=" * 60)
    print()
    
    # Check Python version
    print("1. Python Version Check")
    print("-" * 60)
    python_version = sys.version.split()[0]
    print(f"   Python: {python_version}")
    if version.parse(python_version) < version.parse("3.8"):
        print("   ⚠️  WARNING: Python 3.8+ is recommended")
    else:
        print("   ✓ OK")
    print()
    
    # Check pip
    print("2. Pip Check")
    print("-" * 60)
    pip_output = run_command("pip --version")
    print(f"   {pip_output.strip()}")
    print()
    
    # Run pip check
    print("3. Dependency Conflict Check")
    print("-" * 60)
    check_output = run_command("pip check")
    if "No broken distributions found" in check_output or check_output.strip() == "":
        print("   ✓ No conflicts detected")
    else:
        print("   ⚠️  WARNING:")
        print(check_output)
    print()
    
    # List installed packages
    print("4. Installed Packages (Hasura Related)")
    print("-" * 60)
    
    critical_packages = {
        'httpx': 'Async HTTP client for Hasura',
        'fastapi': 'Web framework',
        'sqlalchemy': 'ORM for PDFDocument',
        'pydantic': 'Data validation',
        'pytorch': 'Deep learning framework',
        'transformers': 'AI model transformations',
        'sentence-transformers': 'Embeddings',
        'pymilvus': 'Milvus vector DB client',
        'pdf2image': 'PDF processing',
    }
    
    pip_list = run_command("pip list")
    for package, description in critical_packages.items():
        if package.lower() in pip_list.lower():
            # Extract version
            for line in pip_list.split('\n'):
                if package.lower() in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        pkg_name = parts[0]
                        pkg_version = parts[1]
                        print(f"   ✓ {pkg_name}: {pkg_version}")
                        print(f"     └─ {description}")
                    break
        else:
            print(f"   ✗ {package} NOT INSTALLED")
            print(f"     └─ {description}")
    
    print()
    
    # Test imports
    print("5. Import Tests")
    print("-" * 60)
    
    test_imports = [
        ("httpx", "Hasura async HTTP client"),
        ("fastapi", "Web framework"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("transformers", "Transformers library"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pymilvus", "Milvus client"),
    ]
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"   ✓ {module}: OK ({description})")
        except ImportError as e:
            print(f"   ✗ {module}: FAILED ({description})")
            print(f"     └─ Error: {str(e)}")
    
    print()
    print("=" * 60)
    print("Verification Complete")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. If all checks passed, proceed with Docker setup")
    print("2. Start containers: docker-compose up -d")
    print("3. Create database schema: See HASURA_SETUP.md")
    print("4. Test Hasura connection: python -c \"from services.hasura_client import HasuraClient\"")
    print()

if __name__ == "__main__":
    main()
