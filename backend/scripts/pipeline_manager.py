#!/usr/bin/env python3
"""Pipeline management script for KMS-V1 incremental ingestion."""

import asyncio
import sys
import json
import argparse
from pathlib import Path
import subprocess
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.incremental_ingestion import IncrementalIngestionPipeline
from src.pipeline.scheduler import PipelineScheduler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineManager:
    """Management interface for the incremental ingestion pipeline."""
    
    def __init__(self):
        self.pipeline = None
        self.scheduler = None
    
    async def run_single_sync(self, verbose: bool = False) -> None:
        """Run a single incremental sync operation."""
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info("🚀 Running single incremental sync...")
        
        self.pipeline = IncrementalIngestionPipeline()
        await self.pipeline.initialize()
        
        results = await self.pipeline.run_incremental_sync()
        
        print("\n📊 Sync Results:")
        print(json.dumps(results, indent=2))
        
        if results.get('status') == 'success':
            print("✅ Sync completed successfully!")
        else:
            print("⚠️ Sync completed with issues")
            return 1
        
        return 0
    
    async def check_health(self) -> None:
        """Check pipeline health status."""
        logger.info("🏥 Checking pipeline health...")
        
        self.pipeline = IncrementalIngestionPipeline()
        await self.pipeline.initialize()
        
        health = await self.pipeline.health_check()
        
        print("\n🏥 Health Status:")
        print(json.dumps(health, indent=2))
        
        if health.get('status') == 'healthy':
            print("✅ System is healthy!")
        else:
            print("❌ System health issues detected")
            return 1
        
        return 0
    
    async def start_scheduler(self, interval: int = 30, background: bool = False) -> None:
        """Start the pipeline scheduler."""
        if background:
            logger.info(f"🚀 Starting scheduler in background mode (interval: {interval} minutes)...")
            
            # Start as background process
            subprocess.Popen([
                sys.executable, __file__, "scheduler", "--interval", str(interval)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"✅ Scheduler started in background (PID will be logged)")
        else:
            logger.info(f"🚀 Starting scheduler in foreground mode (interval: {interval} minutes)...")
            
            self.scheduler = PipelineScheduler(interval_minutes=interval)
            await self.scheduler.initialize()
            await self.scheduler.start_scheduler()
    
    async def stop_scheduler(self) -> None:
        """Stop the pipeline scheduler."""
        logger.info("🛑 Stopping scheduler...")
        
        if self.scheduler:
            await self.scheduler.stop_scheduler()
        else:
            # Try to find and stop background process
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "pipeline_manager.py scheduler"],
                    capture_output=True, text=True
                )
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(["kill", "-TERM", pid])
                        print(f"✅ Sent TERM signal to process {pid}")
                else:
                    print("ℹ️ No scheduler processes found")
            except Exception as e:
                print(f"❌ Error stopping scheduler: {e}")
    
    async def check_scheduler_status(self) -> None:
        """Check scheduler status and statistics."""
        logger.info("📊 Checking scheduler status...")
        
        stats_file = "scheduler_stats.json"
        
        if Path(stats_file).exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
            
            print("\n📊 Scheduler Status:")
            print(json.dumps(stats, indent=2))
            
            if stats.get('run_history'):
                recent_runs = stats['run_history'][-10:]
                successful = len([r for r in recent_runs if r.get('status') == 'success'])
                
                print(f"\n📈 Recent Performance (last {len(recent_runs)} runs):")
                print(f"  Success rate: {successful}/{len(recent_runs)} ({successful/len(recent_runs)*100:.1f}%)")
                
                if recent_runs:
                    last_run = recent_runs[-1]
                    print(f"  Last run: {last_run.get('start_time', 'Unknown')}")
                    print(f"  Last status: {last_run.get('status', 'Unknown')}")
                    
                    if last_run.get('changes_detected'):
                        print(f"  Last changes: {last_run['changes_detected']}")
        else:
            print("❌ No scheduler stats found - scheduler may not be running")
            
        # Check if scheduler process is running
        try:
            result = subprocess.run(
                ["pgrep", "-f", "pipeline_manager.py scheduler"],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                print(f"\n🔄 Scheduler processes running: {len(pids)}")
                for pid in pids:
                    print(f"  PID: {pid}")
            else:
                print("\n⚠️ No scheduler processes found")
        except Exception as e:
            print(f"❌ Error checking processes: {e}")
    
    async def simulate_changes(self, num_cases: int = 5) -> None:
        """Simulate database changes for testing purposes."""
        logger.info(f"🧪 Simulating {num_cases} database changes for testing...")
        
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect("kms_v1_full.db")
        cursor = conn.cursor()
        
        # Get some existing cases to modify
        cursor.execute("SELECT case_number, case_internal_id FROM Cases LIMIT ?", (num_cases,))
        cases = cursor.fetchall()
        
        changes_made = 0
        
        for case_number, case_internal_id in cases:
            try:
                # Add a new case feed entry
                cursor.execute("""
                    INSERT INTO Case_Feed (
                        Parent_Id, Type_Text, Case_Feed_Internal_Id, Is_Deleted_Flag,
                        Created_Timestamp, Created_By_Id, Last_Modified_Timestamp,
                        System_Mod_Timestamp, Body_Text, Comment_Count, Title_Text,
                        Visibility_Text, Insert_GMT_Timestamp, Update_GMT_Timestamp,
                        Is_Rich_Text_Flag
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    case_internal_id, 'TextPost', f'TEST{case_internal_id}{datetime.now().microsecond}',
                    0, datetime.now().isoformat(), 'test_user', datetime.now().isoformat(),
                    datetime.now().isoformat(), 
                    f'Simulated update for case {case_number} - testing incremental sync',
                    0, f'Test Update - Case {case_number}', 'InternalUsers',
                    datetime.now().isoformat(), datetime.now().isoformat(), 0
                ))
                
                changes_made += 1
                
            except Exception as e:
                logger.error(f"❌ Error simulating change for case {case_number}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Simulated {changes_made} changes in the database")
        print("💡 Run 'sync' command to process these changes")

async def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="KMS-V1 Pipeline Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Run single incremental sync')
    sync_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Health command
    subparsers.add_parser('health', help='Check pipeline health')
    
    # Scheduler commands
    scheduler_parser = subparsers.add_parser('scheduler', help='Start scheduler daemon')
    scheduler_parser.add_argument('--interval', '-i', type=int, default=30, help='Sync interval in minutes')
    scheduler_parser.add_argument('--background', '-b', action='store_true', help='Run in background')
    
    subparsers.add_parser('stop', help='Stop scheduler daemon')
    subparsers.add_parser('status', help='Check scheduler status')
    
    # Testing commands
    test_parser = subparsers.add_parser('simulate', help='Simulate database changes for testing')
    test_parser.add_argument('--cases', '-c', type=int, default=5, help='Number of cases to modify')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = PipelineManager()
    
    try:
        if args.command == 'sync':
            return await manager.run_single_sync(verbose=args.verbose)
        elif args.command == 'health':
            return await manager.check_health()
        elif args.command == 'scheduler':
            await manager.start_scheduler(interval=args.interval, background=args.background)
        elif args.command == 'stop':
            await manager.stop_scheduler()
        elif args.command == 'status':
            await manager.check_scheduler_status()
        elif args.command == 'simulate':
            await manager.simulate_changes(num_cases=args.cases)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)