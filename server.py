from mcp.server.fastmcp import FastMCP
import json
import os
from typing import List, Dict, Any

# Initialize the server

mcp = FastMCP("WHeSvc")

@mcp.tool()
def get_top_cpu_processes(file_path: str = "sys_perf.json", top_n: int = 5) -> List[Dict[str, Any]]:

    try:
        # Resolve the file path relative to the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, file_path)
        
        with open(full_path, 'r') as f:
            perf_data = json.load(f)
        
        # Process all data to find processes with high CPU contention
        processes = {}
        
        for bucket in perf_data.get('buckets', []):
            # Get process metrics from LowLevelMetric if available
            bucket_processes = bucket.get('LowLevelMetric', {}).get('CpuMetric', {}).get('Processes', [])
            
            for proc in bucket_processes:
                proc_name = proc.get('ProcessName', 'Unknown')
                proc_id = proc.get('ProcessId', 0)
                key = f"{proc_name}:{proc_id}"
                
                cpu_time_ms = proc.get('CpuTimeMs', 0)
                ready_time_ms = proc.get('ReadyTimeMs', 0)
                
                # Calculate contention percentage
                contention_pct = 0
                if cpu_time_ms > 0:
                    contention_pct = (ready_time_ms / cpu_time_ms) * 100
                
                # If this process is already in our dictionary, update its metrics
                if key in processes:
                    processes[key]['TotalCpuTimeMs'] += cpu_time_ms
                    processes[key]['TotalReadyTimeMs'] += ready_time_ms
                    processes[key]['ContentionPct'] = (processes[key]['TotalReadyTimeMs'] / processes[key]['TotalCpuTimeMs'] * 100) if processes[key]['TotalCpuTimeMs'] > 0 else 0
                    processes[key]['Samples'] += 1
                else:
                    processes[key] = {
                        'ProcessName': proc_name,
                        'ProcessId': proc_id,
                        'TotalCpuTimeMs': cpu_time_ms,
                        'TotalReadyTimeMs': ready_time_ms,
                        'ContentionPct': contention_pct,
                        'Samples': 1
                    }
        
        # Filter processes that have ReadyTimeMsByPriority >= 25% of CPUTimeInMs
        high_contention_processes = [p for p in processes.values() if p['ContentionPct'] >= 25]
        
        # Sort by contention percentage (higher first)
        sorted_processes = sorted(high_contention_processes, key=lambda x: x['ContentionPct'], reverse=True)
        
        # Return top N results
        top_processes = sorted_processes[:top_n]
        
        if not top_processes:
            return [{"Message": "No processes found with CPU contention >= 25%"}]
            
        return top_processes
    except Exception as e:
        return [{"Error": f"Failed to process performance data: {str(e)}"}]

@mcp.tool()
def get_top_memory_processes(file_path: str = "sys_perf.json", top_n: int = 5) -> List[Dict[str, Any]]:

    try:
        # Resolve the file path relative to the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, file_path)
        
        with open(full_path, 'r') as f:
            perf_data = json.load(f)
        
        # Process all data to find processes with high memory usage
        processes = {}
        
        for bucket in perf_data.get('buckets', []):
            # Get memory metrics from LowLevelMetric if available
            memory_metrics = bucket.get('LowLevelMetric', {}).get('MemoryMetric', {})
            
            # Skip empty metrics
            if not memory_metrics:
                continue
                
            # Process each process entry in memory metrics
            for proc_key, proc_data in memory_metrics.items():
                # Skip non-process entries or entries without PeakWorkingSetSizeMiB
                if 'PeakWorkingSetSizeMiB' not in proc_data:
                    continue
                    
                # Extract process name and ID from the key if possible
                # Format can be like "OUTLOOK.EXE (24212)" or other formats
                proc_name = proc_key
                proc_id = 0
                
                # Try to extract process ID from keys like "process.exe (1234)"
                if '(' in proc_key and ')' in proc_key:
                    proc_parts = proc_key.split('(')
                    if len(proc_parts) > 1:
                        proc_name = proc_parts[0].strip()
                        proc_id_str = proc_parts[1].split(')')[0].strip()
                        try:
                            proc_id = int(proc_id_str)
                        except ValueError:
                            pass
                
                # Create unique key for the process
                unique_key = f"{proc_name}:{proc_id}"
                
                # Get memory metrics
                peak_working_set_mib = proc_data.get('PeakWorkingSetSizeMiB', 0)
                avg_working_set_mib = proc_data.get('AvgWorkingSetSizeMiB', 0)
                peak_commit_size_mib = proc_data.get('PeakCommitSizeMiB', 0)
                avg_commit_size_mib = proc_data.get('AvgCommitSizeMiB', 0)
                snapshot_count = proc_data.get('SnapshotCount', 0)
                
                # Store or update process info
                if unique_key in processes:
                    # Update with highest value
                    processes[unique_key]['PeakWorkingSetSizeMiB'] = max(
                        processes[unique_key]['PeakWorkingSetSizeMiB'], 
                        peak_working_set_mib
                    )
                    processes[unique_key]['Snapshots'] += snapshot_count
                else:
                    processes[unique_key] = {
                        'ProcessName': proc_name,
                        'ProcessId': proc_id,
                        'PeakWorkingSetSizeMiB': peak_working_set_mib,
                        'AvgWorkingSetSizeMiB': avg_working_set_mib,
                        'PeakCommitSizeMiB': peak_commit_size_mib,
                        'AvgCommitSizeMiB': avg_commit_size_mib,
                        'Snapshots': snapshot_count
                    }
        
        # Sort processes by PeakWorkingSetSizeMiB (higher first)
        sorted_processes = sorted(processes.values(), key=lambda x: x['PeakWorkingSetSizeMiB'], reverse=True)
        
        # Return top N results
        top_processes = sorted_processes[:top_n]
        
        if not top_processes:
            return [{"Message": "No processes found with memory usage data"}]
            
        return top_processes
    except Exception as e:
        return [{"Error": f"Failed to process memory performance data: {str(e)}"}]


if __name__ == "__main__":
    mcp.run(transport="stdio")