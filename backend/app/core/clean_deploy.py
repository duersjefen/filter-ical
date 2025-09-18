"""
Clean Deployment Detection and Handling
Detects clean deployment signals and triggers database reset
"""
import os
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta


def detect_clean_deployment_signal() -> bool:
    """
    Detect if this startup should trigger a clean deployment.
    Checks for clean deployment markers and git commit messages.
    
    Returns:
        True if this should be a clean deployment
    """
    try:
        # Check for environment variable override
        if os.getenv('FORCE_CLEAN_DEPLOY', '').lower() == 'true':
            print("🧹 FORCE_CLEAN_DEPLOY environment variable detected")
            return True
        
        # Check if we're in a containerized environment (production)
        if not os.path.exists('/.dockerenv'):
            print("🔍 Not in container - skipping clean deployment detection")
            return False
        
        # Check recent git commits for clean deployment signal
        return check_recent_clean_deploy_commit()
        
    except Exception as e:
        print(f"❌ Error detecting clean deployment signal: {e}")
        return False


def check_recent_clean_deploy_commit() -> bool:
    """
    Check if recent git commits contain clean deployment signal.
    
    Returns:
        True if recent commit indicates clean deployment
    """
    try:
        # Get the latest commit message
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%s%n%b'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("⚠️  Could not get git commit message")
            return False
        
        commit_message = result.stdout.strip()
        
        # Check for clean deployment signal
        clean_signals = [
            '🧹 CLEAN_DEPLOY',
            'CLEAN_DEPLOY:',
            '[CLEAN_DEPLOY]',
            'clean deployment',
            'database reset'
        ]
        
        for signal in clean_signals:
            if signal.lower() in commit_message.lower():
                print(f"✅ Clean deployment signal detected: {signal}")
                return True
        
        return False
        
    except subprocess.TimeoutExpired:
        print("⚠️  Git command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking git commit: {e}")
        return False


def mark_clean_deploy_completed():
    """
    Mark that clean deployment has been completed.
    Creates a marker file to prevent repeated clean deployments.
    """
    try:
        marker_file = Path("/tmp/clean_deploy_completed")
        marker_file.write_text(f"Clean deployment completed at {datetime.now().isoformat()}")
        print("✅ Clean deployment marked as completed")
    except Exception as e:
        print(f"⚠️  Could not create clean deployment marker: {e}")


def was_clean_deploy_recently_completed() -> bool:
    """
    Check if clean deployment was recently completed to avoid repeating it.
    
    Returns:
        True if clean deployment was completed in the last hour
    """
    try:
        marker_file = Path("/tmp/clean_deploy_completed")
        if not marker_file.exists():
            return False
        
        # Check if marker is recent (within last hour)
        stat = marker_file.stat()
        marker_time = datetime.fromtimestamp(stat.st_mtime)
        age = datetime.now() - marker_time
        
        if age < timedelta(hours=1):
            print(f"📋 Clean deployment recently completed {age.total_seconds():.0f}s ago")
            return True
        else:
            # Remove old marker
            marker_file.unlink()
            return False
            
    except Exception as e:
        print(f"⚠️  Error checking clean deployment marker: {e}")
        return False


def trigger_clean_deployment() -> bool:
    """
    Trigger clean deployment by resetting database and marking completion.
    
    Returns:
        True if clean deployment was successful
    """
    try:
        print("🧹 Starting clean deployment process...")
        
        # Import here to avoid circular imports
        from ..database import reset_database
        from .domain_setup import ensure_domain_calendars_exist
        from .demo_data import seed_demo_data, should_seed_demo_data
        
        # 1. Reset database
        print("🗄️  Resetting database...")
        if reset_database():
            print("✅ Database reset successful")
        else:
            print("❌ Database reset failed")
            return False
        
        # 2. Ensure domain calendars exist
        print("🏗️  Creating domain calendars...")
        ensure_domain_calendars_exist()
        
        # 3. Seed demo data if needed
        if should_seed_demo_data():
            print("🎭 Seeding demo data...")
            if seed_demo_data():
                print("✅ Demo data seeded successfully")
            else:
                print("⚠️  Demo data seeding failed")
        else:
            print("📋 Demo data already exists")
        
        # 4. Mark completion
        mark_clean_deploy_completed()
        
        print("🎉 Clean deployment completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Clean deployment failed: {e}")
        return False