#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime

class ProductionManager:
    def __init__(self):
        self.app_name = "smartslide"
        self.service_name = f"{self.app_name}.service"
        self.app_dir = f"/opt/{self.app_name}"
        self.log_dir = f"/var/log/{self.app_name}"
    
    def run_command(self, cmd, check=True):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {e.stderr}")
            if check:
                sys.exit(1)
            return None
    
    def status(self):
        print("🔍 SmartSlide Generator Status")
        print("=" * 40)
        
        print("\n📋 Service Status:")
        service_status = self.run_command(f"systemctl is-active {self.service_name}", check=False)
        print(f"   Status: {service_status}")
        
        if service_status == "active":
            self.run_command(f"systemctl status {self.service_name} --no-pager -l")
        
        print("\n🌐 Nginx Status:")
        nginx_status = self.run_command("systemctl is-active nginx", check=False)
        print(f"   Status: {nginx_status}")
        
        print("\n🔌 Port Check:")
        port_check = self.run_command("netstat -tlnp | grep :5002", check=False)
        if port_check:
            print(f"   Port 5002: Active")
        else:
            print(f"   Port 5002: Not active")
        
        print("\n💾 Disk Usage:")
        disk_usage = self.run_command(f"du -sh {self.app_dir}")
        print(f"   App directory: {disk_usage}")
        
        print("\n🧠 Memory Usage:")
        memory_usage = self.run_command("ps aux | grep gunicorn | grep -v grep", check=False)
        if memory_usage:
            print("   Gunicorn processes:")
            for line in memory_usage.split('\n'):
                if line.strip():
                    parts = line.split()
                    cpu = parts[2]
                    mem = parts[3]
                    print(f"     CPU: {cpu}%, MEM: {mem}%")
    
    def start(self):
        print("🚀 Starting SmartSlide Generator...")
        self.run_command(f"systemctl start {self.service_name}")
        print("✅ Service started successfully")
        
        import time
        time.sleep(2)
        self.status()
    
    def stop(self):
        print("🛑 Stopping SmartSlide Generator...")
        self.run_command(f"systemctl stop {self.service_name}")
        print("✅ Service stopped successfully")
    
    def restart(self):
        print("🔄 Restarting SmartSlide Generator...")
        self.run_command(f"systemctl restart {self.service_name}")
        print("✅ Service restarted successfully")
        
        import time
        time.sleep(2)
        self.status()
    
    def logs(self, lines=50, follow=False):
        print(f"📋 SmartSlide Generator Logs (last {lines} lines)")
        print("=" * 50)
        
        cmd = f"journalctl -u {self.service_name} -n {lines}"
        if follow:
            cmd += " -f"
        
        if follow:
            print("Following logs (Press Ctrl+C to stop)...")
            try:
                subprocess.run(cmd, shell=True)
            except KeyboardInterrupt:
                print("\n👋 Stopped following logs")
        else:
            self.run_command(cmd)
    
    def update(self):
        print("📥 Updating SmartSlide Generator...")
        
        self.stop()
        
        backup_dir = f"{self.app_dir}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📦 Creating backup: {backup_dir}")
        self.run_command(f"cp -r {self.app_dir} {backup_dir}")
        
        print("📡 Pulling latest changes...")
        self.run_command(f"cd {self.app_dir} && sudo -u {self.app_name} git pull origin main")
        
        print("📚 Updating dependencies...")
        self.run_command(f"cd {self.app_dir} && sudo -u {self.app_name} ./venv/bin/pip install -r requirements.txt")
        
        self.run_command("systemctl daemon-reload")
        
        self.start()
        
        print("✅ Update completed successfully")
    
    def health_check(self):
        print("🔍 Performing health check...")
        
        try:
            import requests
            response = requests.get("http://localhost:5002/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Timestamp: {data.get('timestamp')}")
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def config(self):
        print("⚙️ Configuration Information")
        print("=" * 40)
        
        env_file = f"{self.app_dir}/.env"
        if os.path.exists(env_file):
            print(f"\n📄 Environment file: {env_file}")
            with open(env_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key = line.split('=')[0]
                        if 'KEY' in key or 'SECRET' in key:
                            print(f"   {key}=***hidden***")
                        else:
                            print(f"   {line}")
        else:
            print(f"❌ Environment file not found: {env_file}")

def main():
    parser = argparse.ArgumentParser(description="SmartSlide Generator Production Manager")
    parser.add_argument('action', choices=['status', 'start', 'stop', 'restart', 'logs', 'update', 'health', 'config'],
                        help='Action to perform')
    parser.add_argument('--lines', type=int, default=50, help='Number of log lines to show')
    parser.add_argument('--follow', '-f', action='store_true', help='Follow logs in real-time')
    
    args = parser.parse_args()
    
    if args.action in ['start', 'stop', 'restart', 'update'] and os.geteuid() != 0:
        print("❌ This operation requires root privileges. Use sudo.")
        sys.exit(1)
    
    manager = ProductionManager()
    
    if args.action == 'status':
        manager.status()
    elif args.action == 'start':
        manager.start()
    elif args.action == 'stop':
        manager.stop()
    elif args.action == 'restart':
        manager.restart()
    elif args.action == 'logs':
        manager.logs(args.lines, args.follow)
    elif args.action == 'update':
        manager.update()
    elif args.action == 'health':
        manager.health_check()
    elif args.action == 'config':
        manager.config()

if __name__ == "__main__":
    main()
