import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import time
from datetime import datetime, timedelta

class MetricsVisualizer:
    def __init__(self, window_size=60):
        self.window_size = window_size
        
        # Initialize data structures
        self.timestamps = deque(maxlen=window_size)
        self.rps = deque(maxlen=window_size)
        self.avg_request_time = deque(maxlen=window_size)
        self.operation_times = {
            'total_processing': deque(maxlen=window_size),
            'db_operations': deque(maxlen=window_size),
            'vector_store': deque(maxlen=window_size),
            'llm_processing': deque(maxlen=window_size),
            'message_queue': deque(maxlen=window_size)
        }
        
        # Set up the plot
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(15, 10))
        self.fig.suptitle('Bot Performance Metrics', fontsize=16)
        
        # Create subplots
        self.ax1 = plt.subplot(221)  # Requests per second
        self.ax2 = plt.subplot(222)  # Average request time
        self.ax3 = plt.subplot(212)  # Operation times
        
        # Initialize lines
        self.rps_line, = self.ax1.plot([], [], 'g-', label='Requests/sec')
        self.avg_time_line, = self.ax2.plot([], [], 'b-', label='Avg Request Time (s)')
        self.operation_lines = {
            op: self.ax3.plot([], [], label=op.replace('_', ' ').title())[0]
            for op in self.operation_times.keys()
        }
        
        # Set up axes
        self.ax1.set_title('Requests per Second')
        self.ax2.set_title('Average Request Time')
        self.ax3.set_title('Operation Times')
        
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.grid(True, alpha=0.3)
            ax.legend()
    
    def update_plot(self, frame):
        try:
            # Read the latest metrics
            with open('logs/detailed_metrics.json', 'r') as f:
                lines = f.readlines()
                if lines:
                    latest_metrics = json.loads(lines[-1])
                    
                    # Update data
                    self.timestamps.append(datetime.fromisoformat(latest_metrics['timestamp']))
                    self.rps.append(latest_metrics['requests_per_second'])
                    self.avg_request_time.append(latest_metrics['avg_request_time'])
                    
                    for op, times in latest_metrics['operation_times'].items():
                        self.operation_times[op].append(times['avg'])
                    
                    # Update plots
                    x_data = np.arange(len(self.timestamps))
                    
                    # Update RPS plot
                    self.rps_line.set_data(x_data, self.rps)
                    self.ax1.relim()
                    self.ax1.autoscale_view()
                    
                    # Update average time plot
                    self.avg_time_line.set_data(x_data, self.avg_request_time)
                    self.ax2.relim()
                    self.ax2.autoscale_view()
                    
                    # Update operation times plot
                    for op, line in self.operation_lines.items():
                        line.set_data(x_data, self.operation_times[op])
                    self.ax3.relim()
                    self.ax3.autoscale_view()
                    
                    # Update x-axis limits for all plots
                    for ax in [self.ax1, self.ax2, self.ax3]:
                        ax.set_xlim(max(0, len(self.timestamps) - self.window_size), len(self.timestamps))
            
            return self.rps_line, self.avg_time_line, *self.operation_lines.values()
        
        except Exception as e:
            print(f"Error updating plot: {str(e)}")
            return self.rps_line, self.avg_time_line, *self.operation_lines.values()
    
    def start(self):
        anim = FuncAnimation(
            self.fig, 
            self.update_plot,
            interval=1000,  # Update every second
            blit=True
        )
        plt.show()

if __name__ == "__main__":
    visualizer = MetricsVisualizer()
    visualizer.start() 