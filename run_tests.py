#!/usr/bin/env python3
"""
BDD Test Runner Script

This script provides a convenient way to run BDD tests with various options.
Usage: python run_tests.py [options]
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, env_vars=None):
    """Run shell command with optional environment variables"""
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, env=env)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description='BDD Test Runner')
    
    # Test execution options
    parser.add_argument('--tags', '-t', help='Tags to run (e.g., @smoke, @regression)')
    parser.add_argument('--browser', '-b', default='chrome', 
                       choices=['chrome', 'firefox', 'edge'],
                       help='Browser to use for testing')
    parser.add_argument('--headless', action='store_true', 
                       help='Run tests in headless mode')
    parser.add_argument('--environment', '-e', default='staging',
                       choices=['development', 'staging', 'production'],
                       help='Environment to test against')
    parser.add_argument('--parallel', '-p', type=int, default=1,
                       help='Number of parallel processes')
    parser.add_argument('--feature', '-f', help='Specific feature file to run')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--stop-on-failure', action='store_true',
                       help='Stop on first failure')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run (don\'t execute steps)')
    parser.add_argument('--format', default='pretty',
                       choices=['pretty', 'json', 'junit'],
                       help='Output format')
    
    # Report options
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate Allure report after test execution')
    parser.add_argument('--open-report', action='store_true',
                       help='Open Allure report in browser')
    
    # Setup options
    parser.add_argument('--install-deps', action='store_true',
                       help='Install dependencies before running tests')
    parser.add_argument('--setup-env', action='store_true',
                       help='Set up environment (copy .env.example to .env)')
    
    args = parser.parse_args()
    
    # Setup environment if requested
    if args.setup_env:
        if not os.path.exists('.env'):
            if os.path.exists('.env.example'):
                import shutil
                shutil.copy('.env.example', '.env')
                print("✅ Created .env file from .env.example")
                print("📝 Please edit .env file with your configuration")
            else:
                print("❌ .env.example file not found")
                return 1
        else:
            print("ℹ️  .env file already exists")
    
    # Install dependencies if requested
    if args.install_deps:
        print("📦 Installing dependencies...")
        result = run_command("pip install -r requirements.txt")
        if result != 0:
            print("❌ Failed to install dependencies")
            return 1
        print("✅ Dependencies installed successfully")
    
    # Build behave command
    command = ["behave"]
    
    # Add tags
    if args.tags:
        command.extend(["--tags", args.tags])
    
    # Add format
    if args.format != 'pretty':
        command.extend(["--format", args.format])
    
    # Add feature file
    if args.feature:
        command.append(args.feature)
    
    # Add other options
    if args.verbose:
        command.append("--verbose")
    
    if args.stop_on_failure:
        command.append("--stop")
    
    if args.dry_run:
        command.append("--dry-run")
    
    # Environment variables
    env_vars = {}
    
    if args.browser:
        env_vars['BROWSER'] = args.browser
    
    if args.headless:
        env_vars['HEADLESS'] = 'true'
    
    if args.environment:
        env_vars['ENVIRONMENT'] = args.environment
    
    if args.parallel > 1:
        env_vars['PARALLEL_PROCESSES'] = str(args.parallel)
        command.extend(["--processes", str(args.parallel)])
    
    # Add user data for behave
    user_data = []
    if args.browser:
        user_data.append(f"browser={args.browser}")
    if args.headless:
        user_data.append("headless=true")
    if args.environment:
        user_data.append(f"environment={args.environment}")
    
    if user_data:
        for data in user_data:
            command.extend(["-D", data])
    
    # Create directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports/screenshots", exist_ok=True)
    
    # Run tests
    print(f"🚀 Running BDD tests...")
    print(f"   Browser: {args.browser}")
    print(f"   Environment: {args.environment}")
    print(f"   Headless: {args.headless}")
    if args.tags:
        print(f"   Tags: {args.tags}")
    if args.feature:
        print(f"   Feature: {args.feature}")
    print()
    
    result = run_command(" ".join(command), env_vars)
    
    # Generate report if requested
    if args.generate_report:
        print("\n📊 Generating Allure report...")
        report_result = run_command("allure generate reports/allure --clean -o allure-report")
        if report_result == 0:
            print("✅ Allure report generated successfully")
            
            if args.open_report:
                print("🌐 Opening report in browser...")
                run_command("allure open allure-report")
        else:
            print("❌ Failed to generate Allure report")
    
    # Print summary
    if result == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {result}")
    
    return result

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)