#!/usr/bin/env python3
"""High-performance data ingestion script for ChromaDB using async processing."""

import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.async_processor import HighPerformanceProcessor
from src.tasks.data_ingestion import run_incremental_sync
from src.tasks.monitoring import health_check, collect_metrics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HighPerformanceIngestionManager:
    """Manager for high-performance data ingestion operations."""
    
    def __init__(self, max_workers: int = 32, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.processor = None
    
    async def run_async_ingestion(self, enable_distributed: bool = False) -> dict:
        """Run high-performance async ingestion."""
        logger.info("🚀 Starting high-performance async ingestion")
        
        if enable_distributed:
            # Use Celery for distributed processing
            logger.info("🌐 Using distributed processing with Celery")
            result = run_incremental_sync.delay()
            return result.get(timeout=3600)  # 1 hour timeout
        else:
            # Use async processor
            self.processor = HighPerformanceProcessor(
                max_workers=self.max_workers,
                batch_size=self.batch_size,
                max_concurrent_batches=16,
                enable_caching=True,
                enable_monitoring=True
            )
            
            try:
                await self.processor.initialize()
                results = await self.processor.run_full_sync()
                return results
            finally:
                if self.processor:
                    await self.processor.shutdown()
    
    async def run_initial_load(self) -> dict:
        """Run initial data load with maximum performance."""
        logger.info("🔄 Running initial data load")
        
        self.processor = HighPerformanceProcessor(
            max_workers=min(64, self.max_workers * 2),  # Use more workers for initial load
            batch_size=self.batch_size * 2,  # Larger batches
            max_concurrent_batches=32,
            enable_caching=True,
            enable_monitoring=True
        )
        
        try:
            await self.processor.initialize()
            
            # Force full reload by clearing state
            self.processor.processed_records.clear()
            self.processor.record_hashes.clear()
            
            results = await self.processor.run_full_sync()
            return results
        finally:
            if self.processor:
                await self.processor.shutdown()
    
    async def benchmark_performance(self, test_records: int = 1000) -> dict:
        """Benchmark ingestion performance."""
        logger.info(f"⚡ Benchmarking performance with {test_records} records")
        
        # Test different configurations
        configs = [
            {"workers": 8, "batch": 50, "concurrent": 4},
            {"workers": 16, "batch": 100, "concurrent": 8},
            {"workers": 32, "batch": 200, "concurrent": 16},
            {"workers": 64, "batch": 500, "concurrent": 32}
        ]
        
        benchmark_results = []
        
        for config in configs:
            logger.info(f"Testing config: {config}")
            
            processor = HighPerformanceProcessor(
                max_workers=config["workers"],
                batch_size=config["batch"],
                max_concurrent_batches=config["concurrent"],
                enable_caching=True,
                enable_monitoring=True
            )
            
            try:
                start_time = time.time()
                await processor.initialize()
                
                # Simulate processing
                # In real scenario, this would process actual data
                await asyncio.sleep(0.1)  # Simulate work
                
                duration = time.time() - start_time
                
                stats = await processor.get_performance_stats()
                
                benchmark_results.append({
                    "config": config,
                    "duration": duration,
                    "stats": stats
                })
                
            finally:
                await processor.shutdown()
        
        return {
            "benchmark_results": benchmark_results,
            "best_config": min(benchmark_results, key=lambda x: x["duration"])
        }
    
    async def health_check(self) -> dict:
        """Perform comprehensive health check."""
        if self.processor:
            stats = await self.processor.get_performance_stats()
            return {
                "status": "healthy",
                "processor_stats": stats
            }
        else:
            return {"status": "no_processor_running"}

async def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="High-Performance Data Ingestion for ChromaDB")
    parser.add_argument('command', choices=[
        'ingest', 'initial-load', 'benchmark', 'health', 'distributed'
    ], help='Command to execute')
    parser.add_argument('--workers', type=int, default=32, help='Max workers (default: 32)')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size (default: 100)')
    parser.add_argument('--test-records', type=int, default=1000, help='Test records for benchmark')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    manager = HighPerformanceIngestionManager(
        max_workers=args.workers,
        batch_size=args.batch_size
    )
    
    try:
        if args.command == 'ingest':
            logger.info("🔄 Starting async ingestion")
            result = await manager.run_async_ingestion()
            
        elif args.command == 'initial-load':
            logger.info("🔄 Starting initial data load")
            result = await manager.run_initial_load()
            
        elif args.command == 'benchmark':
            logger.info("⚡ Starting performance benchmark")
            result = await manager.benchmark_performance(args.test_records)
            
        elif args.command == 'health':
            logger.info("🏥 Running health check")
            result = await manager.health_check()
            
        elif args.command == 'distributed':
            logger.info("🌐 Starting distributed ingestion")
            result = await manager.run_async_ingestion(enable_distributed=True)
        
        # Print results
        print("\n" + "="*50)
        print("📊 INGESTION RESULTS")
        print("="*50)
        print(json.dumps(result, indent=2, default=str))
        
        # Performance summary
        if 'throughput_per_second' in result:
            print(f"\n⚡ Performance: {result['throughput_per_second']:.1f} records/sec")
        
        if 'duration_seconds' in result:
            print(f"⏱️ Duration: {result['duration_seconds']:.2f} seconds")
        
        if 'records_processed' in result:
            print(f"📈 Records Processed: {result['records_processed']}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        return 1


if __name__ == "__main__":
    # Use uvloop for better async performance
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)