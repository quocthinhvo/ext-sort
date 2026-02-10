import struct
import random
import os
import heapq
import tempfile
import time
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QWaitCondition

class ExternalSort(QObject):
    # Signals to update GUI
    progress_update = pyqtSignal(str)  # General status messages
    run_created = pyqtSignal(int, list) # Run index, data (for visualization)
    merge_step = pyqtSignal(float, int) # Value, run_index_source

    def __init__(self):
        super().__init__()
        self.delay = 0.0
        self.paused = False
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()

    def set_delay(self, delay):
        self.delay = delay

    def set_paused(self, paused):
        self.paused = paused
        if not paused:
            self._wait_condition.wakeAll()

    def next_step(self):
        self._wait_condition.wakeAll()

    def _wait_if_paused(self):
        self._mutex.lock()
        if self.paused:
            self._wait_condition.wait(self._mutex)
        self._mutex.unlock()
        
        if self.delay > 0:
            time.sleep(self.delay)

    def generate_data(self, filename, count):
        """Generates a binary file with 'count' random double-precision floats."""
        with open(filename, 'wb') as f:
            for _ in range(count):
                # 8 bytes per double
                val = random.uniform(0, 1000)
                f.write(struct.pack('d', val))
        self.progress_update.emit(f"Generated {count} records in {filename}")

    def sort(self, input_file, output_file, chunk_size, delay=0.0):
        """
        Sorts the input_file into output_file using external merge sort.
        chunk_size: Number of doubles to read into memory at once.
        """
        self.delay = delay
        self.progress_update.emit("Starting sort...")
        
        # Phase 1: Create runs
        runs = self._create_runs(input_file, chunk_size)
        self.progress_update.emit(f"Created {len(runs)} runs. Starting merge...")

        # Phase 2: Merge runs
        self._merge_runs(runs, output_file)
        self.progress_update.emit("Sort complete.")
        
        # Cleanup temp files
        for run in runs:
            try:
                os.remove(run)
            except OSError:
                pass

    def _create_runs(self, input_file, chunk_size):
        runs = []
        with open(input_file, 'rb') as f:
            run_index = 0
            while True:
                # Read binary data
                bytes_read = f.read(chunk_size * 8)
                if not bytes_read:
                    break
                
                # Unpack doubles
                count = len(bytes_read) // 8
                data = list(struct.unpack(f'{count}d', bytes_read))
                
                # Sort in memory
                data.sort()
                
                # Write to temp file
                # Create a temp file for this run
                fd, temp_path = tempfile.mkstemp(prefix=f'run_{run_index}_')
                with os.fdopen(fd, 'wb') as temp_f:
                    # Write packed data
                     # Use 'd' for double, *data unpacks the list
                    temp_f.write(struct.pack(f'{len(data)}d', *data))
                
                runs.append(temp_path)
                
                # Emit signal for GUI (limit data size for visual stability if needed)
                # Ensure we emit a list so it can be handled by slot
                self.run_created.emit(run_index, data)
                run_index += 1
                
        return runs

    def _merge_runs(self, runs, output_file):
        # Open all run files
        files = [open(run, 'rb') for run in runs]
        
        # Min-heap for k-way merge
        # Heap elements: (value, run_index)
        heap = []
        
        # Initial population of heap
        for i, f in enumerate(files):
            bytes_read = f.read(8)
            if bytes_read:
                val = struct.unpack('d', bytes_read)[0]
                heapq.heappush(heap, (val, i))
        
        with open(output_file, 'wb') as out_f:
            while heap:
                self._wait_if_paused()

                # Get smallest value from heap
                val, run_idx = heapq.heappop(heap)
                
                # Write to output
                out_f.write(struct.pack('d', val))

                # Emit value and source run index
                self.merge_step.emit(val, run_idx)

                # Read next value from the same run
                bytes_read = files[run_idx].read(8)
                if bytes_read:
                    next_val = struct.unpack('d', bytes_read)[0]
                    heapq.heappush(heap, (next_val, run_idx))

        # Close all files
        for f in files:
            f.close()

if __name__ == '__main__':
    # Simple test
    sorter = ExternalSort()
    test_file = 'test_data.bin'
    out_file = 'sorted_data.bin'
    sorter.generate_data(test_file, 50)
    # chunk_size 10 -> 5 runs
    sorter.sort(test_file, out_file, 10)
    
    # Verify
    with open(out_file, 'rb') as f:
        data = f.read()
        count = len(data) // 8
        values = struct.unpack(f'{count}d', data)
        print("Is sorted:", all(values[i] <= values[i+1] for i in range(len(values)-1)))
        print(values)
