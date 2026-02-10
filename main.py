import sys
import struct
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QSpinBox, QListWidget, QTextEdit, QProgressBar,
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDoubleSpinBox, QInputDialog)
from PyQt6.QtCore import QThread, pyqtSlot, Qt
from PyQt6.QtGui import QColor

from external_sort import ExternalSort

class SortWorker(QThread):
    def __init__(self, sorter, input_file, output_file, chunk_size, delay):
        super().__init__()
        self.sorter = sorter
        self.input_file = input_file
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.delay = delay

    def run(self):
        self.sorter.sort(self.input_file, self.output_file, self.chunk_size, self.delay)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("External Sorting Visualization - Vo Quoc Thinh 22520006")
        self.resize(1200, 800)

        self.input_file = ""
        self.sorter = None
        self.worker = None
        self.run_cursors = {} # Track current index for each run

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Controls Area
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Generate Random Data")
        self.btn_generate.clicked.connect(self.generate_data)
        
        self.btn_select = QPushButton("Select Input File")
        self.btn_select.clicked.connect(self.select_file)
        
        self.lbl_file = QLabel("No file selected")
        
        self.spin_chunk = QSpinBox()
        self.spin_chunk.setRange(2, 1000)
        self.spin_chunk.setValue(10)
        self.spin_chunk.setPrefix("Chunk Size: ")
        
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.0, 5.0)
        self.spin_delay.setSingleStep(0.1)
        self.spin_delay.setValue(0.1)
        self.spin_delay.setPrefix("Delay (s): ")
        self.spin_delay.valueChanged.connect(self.update_delay)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setCheckable(True)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)

        self.btn_step = QPushButton("Next Step")
        self.btn_step.clicked.connect(self.next_step)
        self.btn_step.setEnabled(False)

        self.btn_sort = QPushButton("Start Sort")
        self.btn_sort.clicked.connect(self.start_sort)
        self.btn_sort.setEnabled(False)

        controls_layout.addWidget(self.btn_generate)
        controls_layout.addWidget(self.btn_select)
        controls_layout.addWidget(self.lbl_file)
        controls_layout.addWidget(self.spin_chunk)
        controls_layout.addWidget(self.spin_delay)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_step)
        controls_layout.addWidget(self.btn_sort)
        controls_group.setLayout(controls_layout)
        
        layout.addWidget(controls_group)

        # Visualization Area
        viz_layout = QHBoxLayout()
        
        # Original Data View
        original_group = QGroupBox("Original File (First 100)")
        original_layout = QVBoxLayout()
        self.list_original = QListWidget()
        original_layout.addWidget(self.list_original)
        original_group.setLayout(original_layout)
        
        # Runs View
        runs_group = QGroupBox("Sorted Runs (in Memory/Temp)")
        runs_layout = QVBoxLayout()
        self.table_runs = QTableWidget()
        self.table_runs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        runs_layout.addWidget(self.table_runs)
        runs_group.setLayout(runs_layout)
        
        # Output View
        output_group = QGroupBox("Merged Output")
        output_layout = QVBoxLayout()
        self.list_output = QListWidget()
        output_layout.addWidget(self.list_output)
        output_group.setLayout(output_layout)

        viz_layout.addWidget(original_group, 1)
        viz_layout.addWidget(runs_group, 2)
        viz_layout.addWidget(output_group, 1)
        
        layout.addLayout(viz_layout)

        # Logs/Status
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(100)
        layout.addWidget(self.status_log)

    def log(self, message):
        self.status_log.append(message)

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Binary File", "", "Binary Files (*.bin);;All Files (*)")
        if fname:
            self.input_file = fname
            self.lbl_file.setText(os.path.basename(fname))
            self.btn_sort.setEnabled(True)
            self.load_preview()

    def generate_data(self):
        count, ok = QInputDialog.getInt(self, "Generate Data", "Number of records:", 100, 10, 1000000, 10)
        if not ok:
            return
            
        fname, _ = QFileDialog.getSaveFileName(self, "Save Generated Data", "data.bin", "Binary Files (*.bin)")
        if fname:
            sorter = ExternalSort()
            sorter.generate_data(fname, count)
            self.log(f"Generated {count} records to {fname}")
            self.input_file = fname
            self.lbl_file.setText(os.path.basename(fname))
            self.btn_sort.setEnabled(True)
            self.load_preview()

    def load_preview(self):
        self.list_original.clear()
        try:
            with open(self.input_file, 'rb') as f:
                # Read first 100 doubles
                data = f.read(8 * 100)
                count = len(data) // 8
                values = struct.unpack(f'{count}d', data)
                for val in values:
                    self.list_original.addItem(f"{val:.4f}")
        except Exception as e:
            self.log(f"Error reading file: {e}")

    def update_delay(self, val):
        if self.sorter:
            self.sorter.set_delay(val)

    def toggle_pause(self):
        is_paused = self.btn_pause.isChecked()
        self.btn_pause.setText("Resume" if is_paused else "Pause")
        self.btn_step.setEnabled(is_paused)
        if self.sorter:
            self.sorter.set_paused(is_paused)

    def next_step(self):
        if self.sorter:
            self.sorter.next_step()

    def start_sort(self):
        if not self.input_file:
            return

        self.list_output.clear()
        self.table_runs.clear()
        self.table_runs.setColumnCount(0)
        self.table_runs.setRowCount(0)
        self.run_cursors = {}
        
        output_file = self.input_file.replace('.bin', '_sorted.bin')
        chunk_size = self.spin_chunk.value()
        delay = self.spin_delay.value()
        
        self.sorter = ExternalSort()
        self.sorter.progress_update.connect(self.log)
        self.sorter.run_created.connect(self.on_run_created)
        self.sorter.merge_step.connect(self.on_merge_step)
        
        self.worker = SortWorker(self.sorter, self.input_file, output_file, chunk_size, delay)
        # self.worker.run() - Removed to avoid blocking main thread
        self.worker.start()

        self.btn_sort.setEnabled(False)
        self.btn_pause.setEnabled(True)
        # Apply initial pause state if button is already checked (unlikely but good practice)
        if self.btn_pause.isChecked():
            self.sorter.set_paused(True)
            self.btn_step.setEnabled(True)

        self.worker.finished.connect(self.on_sort_finished)
        self.worker.finished.connect(lambda: self.log(f"Sort finished. Output: {output_file}"))

    def on_sort_finished(self):
        self.btn_sort.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_step.setEnabled(False)
        self.btn_pause.setChecked(False)
        self.btn_pause.setText("Pause")

    @pyqtSlot(int, list)
    def on_run_created(self, run_index, data):
        # Add column for this run
        col_idx = self.table_runs.columnCount()
        self.table_runs.insertColumn(col_idx)
        self.table_runs.setHorizontalHeaderItem(col_idx, QTableWidgetItem(f"Run {run_index}"))
        
        # Initialize cursor for this run
        self.run_cursors[run_index] = 0
        
        # Add data to rows
        if self.table_runs.rowCount() < len(data):
            self.table_runs.setRowCount(len(data))
            
        for row, val in enumerate(data):
            item = QTableWidgetItem(f"{val:.4f}")
            self.table_runs.setItem(row, col_idx, item)

    @pyqtSlot(float, int)
    def on_merge_step(self, val, run_index):
        # Add to output list
        self.list_output.addItem(f"{val:.4f}")
        self.list_output.scrollToBottom()

        # Highlight string in table
        row = self.run_cursors.get(run_index, 0)
        if row < self.table_runs.rowCount():
            item = self.table_runs.item(row, run_index)
            if item:
                item.setBackground(QColor("lightgreen"))
                self.table_runs.scrollToItem(item)
        
        self.run_cursors[run_index] = row + 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
