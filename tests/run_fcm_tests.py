#!/usr/bin/env python3
"""
Test runner script for FCM notification utility tests.

This script provides an easy way to run the FCM notification tests
with various options like coverage reporting.
"""

import subprocess
import sys
import os


def run_tests(with_coverage=True, verbose=True):
    """
    Run the FCM notification tests.
    
    Args:
        with_coverage (bool): Whether to include coverage reporting
        verbose (bool): Whether to run tests in verbose mode
    """
    # Change to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    VENV_DIR = ".venv"
    
    # Determine the Python executable (prefer virtual environment if available)
    python_exe = sys.executable
    if os.path.exists(VENV_DIR):
        if os.name == 'nt':  # Windows
            venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")
        else:  # Unix-like
            venv_python = os.path.join(VENV_DIR, "bin", "python")
        
        if os.path.exists(venv_python):
            python_exe = venv_python
    
    # Build the pytest command
    cmd = [python_exe, "-m", "pytest", "tests/test_send_fcm_notification.py"]
    
    if verbose:
        cmd.append("-v")
    
    if with_coverage:
        cmd.extend([
            "--cov=utils.send_fcm_notification",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/fcm_notification"
        ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run the tests
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ All FCM notification tests passed!")
        if with_coverage:
            print("📊 Coverage report generated in htmlcov/fcm_notification/")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run FCM notification tests")
    parser.add_argument(
        "--no-coverage", 
        action="store_true", 
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true", 
        help="Run tests in quiet mode"
    )
    
    args = parser.parse_args()
    
    run_tests(
        with_coverage=not args.no_coverage,
        verbose=not args.quiet
    ) 