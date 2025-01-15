from collections import deque
import time
from datetime import datetime
import json
import asyncio
import logging
from typing import Dict, List, Deque
import statistics
import os

class PerformanceMetrics:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # Keep last 60 seconds of data
        self.request_times: Deque[float] = deque(maxlen=window_size)
        self.operation_times: Dict[str, Deque[float]] = {
            'total_processing': deque(maxlen=window_size),
            'db_operations': deque(maxlen=window_size),
            'vector_store': deque(maxlen=window_size),
            'llm_processing': deque(maxlen=window_size),
            'message_queue': deque(maxlen=window_size)
        }
        self.requests_per_second: Deque[int] = deque(maxlen=window_size)
        self.error_counts: Dict[str, int] = {}
        self.last_update = time.time()
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging - file only, no console output
        self.logger = logging.getLogger('performance_metrics')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Prevent propagation to root logger
        
        # File handler for continuous metrics
        metrics_handler = logging.FileHandler('logs/performance_metrics.log')
        metrics_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.logger.addHandler(metrics_handler)

    def add_request_time(self, duration: float):
        """Add a new request processing time"""
        self.request_times.append(duration)

    def add_operation_time(self, operation: str, duration: float):
        """Add processing time for a specific operation"""
        if operation in self.operation_times:
            self.operation_times[operation].append(duration)

    def log_error(self, error_type: str):
        """Log an error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def calculate_metrics(self) -> dict:
        """Calculate current performance metrics"""
        current_time = time.time()
        
        # Calculate requests per second
        requests_last_second = len([t for t in self.request_times 
                                  if current_time - t <= 1])
        self.requests_per_second.append(requests_last_second)

        metrics = {
            'timestamp': datetime.now().isoformat(),
            'requests_per_second': requests_last_second,
            'avg_request_time': statistics.mean(self.request_times) if self.request_times else 0,
            'operation_times': {
                op: {
                    'avg': statistics.mean(times) if times else 0,
                    'min': min(times) if times else 0,
                    'max': max(times) if times else 0
                }
                for op, times in self.operation_times.items()
            },
            'error_counts': self.error_counts.copy(),
            'avg_rps_window': statistics.mean(self.requests_per_second) if self.requests_per_second else 0
        }
        
        return metrics

    async def start_monitoring(self):
        """Start continuous monitoring and logging"""
        while True:
            try:
                metrics = self.calculate_metrics()
                
                # Log metrics to files only
                self.logger.info(json.dumps(metrics))
                
                # Save detailed metrics to a separate file for visualization
                with open('logs/detailed_metrics.json', 'a') as f:
                    json.dump(metrics, f)
                    f.write('\n')
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                # Log errors to file only
                self.logger.error(f"Error in monitoring: {str(e)}")
                await asyncio.sleep(1)

# Global instance
performance_metrics = PerformanceMetrics() 