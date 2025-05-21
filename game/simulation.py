import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QTextEdit, QPushButton, QGridLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer

from simu_back import SimuManager  # Make sure the filename matches

class SimuGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Computer vs Computer Simulation")
        self.resize(650, 650)
        self.manager = SimuManager()
        self.rounds_to_play = 100  # Total rounds to simulate
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 second per round
        self.timer.timeout.connect(self.play_round)
        
        # Store cell labels for updating
        self.cell_labels = []
        
        self.init_ui()
        self.setStyleSheet(self.main_style_sheet())
        self.run_simulation()

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        # Create main tab widget that takes up the whole window
        self.main_tabs = QTabWidget()
        
        # Create Simulation Tab
        self.simulation_tab = QWidget()
        simulation_layout = QVBoxLayout()

        self.status_label = QLabel("Initializing simulation...")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        simulation_layout.addWidget(self.status_label)

        # Status with score on the right
        status_layout = QHBoxLayout()
        
        self.round_score_label = QLabel("")
        self.round_score_label.setObjectName("RoundScoreLabel")
        self.round_score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self.round_score_label)
        
        simulation_layout.addLayout(status_layout)

        self.result_display = QTextEdit()
        self.result_display.setObjectName("ResultDisplay")
        self.result_display.setReadOnly(True)
        self.result_display.setFixedHeight(120)  # Changed from 250 to 120 pixels
        simulation_layout.addWidget(self.result_display)
        
        # History toggle button
        self.history_toggle_button = QPushButton("Hide History")
        self.history_toggle_button.setObjectName("ToggleHistoryButton")
        self.history_toggle_button.clicked.connect(self.toggle_history_display)
        simulation_layout.addWidget(self.history_toggle_button)

        # Game board layout
        board_layout = QHBoxLayout()
        
        # Grid container for the world grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        self.grid_container = QWidget()
        self.grid_container.setLayout(self.grid_layout)
        self.grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        board_layout.addWidget(self.grid_container, stretch=1)
        
        # Add controls on the side
        side_controls = QVBoxLayout()
        
        # Add pause/resume button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setObjectName("PauseButton")
        self.pause_button.clicked.connect(self.toggle_pause)
        side_controls.addWidget(self.pause_button)
        
        # Add spacing
        side_controls.addStretch()
        board_layout.addLayout(side_controls)
        
        simulation_layout.addLayout(board_layout)

        self.end_button = QPushButton("End Simulation")
        self.end_button.setObjectName("EndGameButton")
        self.end_button.clicked.connect(self.end_simulation)
        simulation_layout.addWidget(self.end_button)

        self.simulation_tab.setLayout(simulation_layout)

        # Create Matrices Tab
        self.matrices_tab = QWidget()
        matrices_layout = QVBoxLayout()
        
        # Create a section for the payoff matrix
        payoff_section = QVBoxLayout()
        payoff_label = QLabel("Payoff Matrix:")
        payoff_label.setObjectName("MatrixLabel")
        payoff_section.addWidget(payoff_label)
        
        # Create a table for the payoff matrix
        self.payoff_table = QTableWidget()
        self.payoff_table.setObjectName("MatrixTable")
        payoff_section.addWidget(self.payoff_table)
        
        # Create a section for the hider strategy
        hider_section = QVBoxLayout()
        hider_label = QLabel("Hider Strategy:")
        hider_label.setObjectName("MatrixLabel")
        hider_section.addWidget(hider_label)
        
        # Create a table for the hider strategy
        self.hider_table = QTableWidget()
        self.hider_table.setObjectName("MatrixTable")
        hider_section.addWidget(self.hider_table)
        
        # Create a section for the seeker strategy
        seeker_section = QVBoxLayout()
        seeker_label = QLabel("Seeker Strategy:")
        seeker_label.setObjectName("MatrixLabel")
        seeker_section.addWidget(seeker_label)
        
        # Create a table for the seeker strategy
        self.seeker_table = QTableWidget()
        self.seeker_table.setObjectName("MatrixTable")
        seeker_section.addWidget(self.seeker_table)
        
        # Add both sections to the matrices layout
        matrices_layout.addLayout(payoff_section)
        matrices_layout.addLayout(hider_section)
        matrices_layout.addLayout(seeker_section)
        
        self.matrices_tab.setLayout(matrices_layout)
        
        # Add both tabs to the main tab widget
        self.main_tabs.addTab(self.simulation_tab, "Simulation")
        self.main_tabs.addTab(self.matrices_tab, "Matrices")
        
        # Add the main tab widget to the layout
        self.layout.addWidget(self.main_tabs)
        
        self.setLayout(self.layout)

    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("Resume")
            self.status_label.setText("Simulation paused")
        else:
            self.timer.start()
            self.pause_button.setText("Pause")
            self.status_label.setText("Simulation running")

    def toggle_history_display(self):
        if self.result_display.isVisible():
            self.result_display.hide()
            self.history_toggle_button.setText("Show History")
        else:
            self.result_display.show()
            self.history_toggle_button.setText("Hide History")

    def update_matrices_display(self):
        """Update the matrices tab with payoff matrix and strategies"""
        if hasattr(self.manager, 'payoff_matrix') and self.manager.payoff_matrix is not None:
            # Display payoff matrix
            rows, cols = self.manager.rows, self.manager.cols
            size = rows * cols
            
            # Set up payoff table dimensions
            self.payoff_table.setRowCount(size)
            self.payoff_table.setColumnCount(size)
            
            # Fill payoff table with data
            for i in range(size):
                for j in range(size):
                    value = self.manager.payoff_matrix[i][j]
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.payoff_table.setItem(i, j, item)
            
            # Auto-resize columns to fit content
            self.payoff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.payoff_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Display hider strategy - modify this based on your actual attribute names
        if hasattr(self.manager, 'hider_strategy') and self.manager.hider_strategy is not None:
            # Display hider strategy
            size = len(self.manager.hider_strategy)
            rows = self.manager.rows
            cols = self.manager.cols
            
            # Set up strategy table dimensions
            self.hider_table.setRowCount(rows)
            self.hider_table.setColumnCount(cols)
            
            # Fill strategy table with data - reshape the 1D array to 2D grid
            for i in range(rows):
                for j in range(cols):
                    idx = i * cols + j
                    if idx < size:
                        value = self.manager.hider_strategy[idx]
                        item = QTableWidgetItem(f"{value:.4f}")  # Format to 4 decimal places
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.hider_table.setItem(i, j, item)
            
            # Auto-resize columns to fit content
            self.hider_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.hider_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Display seeker strategy - modify this based on your actual attribute names
        if hasattr(self.manager, 'seeker_strategy') and self.manager.seeker_strategy is not None:
            # Display seeker strategy
            size = len(self.manager.seeker_strategy)
            rows = self.manager.rows
            cols = self.manager.cols
            
            # Set up strategy table dimensions
            self.seeker_table.setRowCount(rows)
            self.seeker_table.setColumnCount(cols)
            
            # Fill strategy table with data - reshape the 1D array to 2D grid
            for i in range(rows):
                for j in range(cols):
                    idx = i * cols + j
                    if idx < size:
                        value = self.manager.seeker_strategy[idx]
                        item = QTableWidgetItem(f"{value:.4f}")  # Format to 4 decimal places
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.seeker_table.setItem(i, j, item)
            
            # Auto-resize columns to fit content
            self.seeker_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.seeker_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def update_round_score_display(self):
        round_num = len(self.manager.game_history)  # rounds played so far
        hider = self.manager.human_score  # Assume human_score is hider's score
        seeker = self.manager.computer_score  # Assume computer_score is seeker's score
        self.round_score_label.setText(f"Round {round_num} | Score: Hider {hider} - Seeker {seeker}")

    def run_simulation(self):
        self.manager.start_new_game(human_role=None)
        self.display_world()
        self.status_label.setText("Running simulation: Computer (Hider) vs Computer (Seeker)")
        self.result_display.append("Game started. Hider & Seeker strategies computed.\n")
        self.update_matrices_display()  # Initialize matrices display
        self.update_round_score_display()  # Initialize score display
        self.timer.start()

    def play_round(self):
        if self.manager.current_round >= self.rounds_to_play:
            self.timer.stop()
            self.status_label.setText("Simulation finished.")
            self.result_display.append("🎮 Simulation complete!\n")
            self.result_display.append(f"Final Score → Hider: {self.manager.human_score} | Seeker: {self.manager.computer_score}")
            return

        # Reset cell colors from previous round (if any)
        self.reset_cell_colors()
        
        self.manager.start_round()
        history = self.manager.game_history[-1]
        hider_idx = history["hider"]
        seeker_idx = history["seeker"]
        result = history["result"]

        hider_row, hider_col = hider_idx // self.manager.cols, hider_idx % self.manager.cols
        seeker_row, seeker_col = seeker_idx // self.manager.cols, seeker_idx % self.manager.cols
        
        hider_pos = (hider_row, hider_col)
        seeker_pos = (seeker_row, seeker_col)

        # Update the cells with H and S, and color them based on success/failure
        if hider_idx == seeker_idx:  # Seeker found the hider
            # Both on the same cell - show both letters and color green for seeker (success)
            self.cell_labels[hider_row][hider_col].setText("H,S")
            self.cell_labels[hider_row][hider_col].setStyleSheet(
                "border: 1px solid #666; background-color: #4CAF50; color: white; font-size: 18px; font-weight: bold; border-radius: 8px;"
            )
        else:
            # Hider not found - Hider succeeds (green) and Seeker fails (red)
            self.cell_labels[hider_row][hider_col].setText("H")
            self.cell_labels[hider_row][hider_col].setStyleSheet(
                "border: 1px solid #666; background-color: #4CAF50; color: white; font-size: 18px; font-weight: bold; border-radius: 8px;"
            )
            
            self.cell_labels[seeker_row][seeker_col].setText("S")
            self.cell_labels[seeker_row][seeker_col].setStyleSheet(
                "border: 1px solid #666; background-color: #F44336; color: white; font-size: 18px; font-weight: bold; border-radius: 8px;"
            )

        msg = f"🕹️ Round {history['round']}:\n"
        msg += f" - Hider at: {hider_pos}\n"
        msg += f" - Seeker chose: {seeker_pos}\n"
        msg += f" - {result}\n"
        msg += f"Score → Hider: {self.manager.human_score} | Seeker: {self.manager.computer_score}\n\n"
        self.result_display.append(msg)
        
        # Update the round and score display
        self.update_round_score_display()

    def reset_cell_colors(self):
        # Reset all cells to their original appearance
        for r in range(self.manager.rows):
            for c in range(self.manager.cols):
                cell_type = self.manager.world[r][c]
                type_map = {1: "E", 2: "N", 3: "H"}  # Modified to match game_manager.py
                val = type_map[cell_type]
                self.cell_labels[r][c].setText(val)
                self.cell_labels[r][c].setStyleSheet(
                    "border: 1px solid #666; background-color: #2e2e3e; color: white; font-size: 18px; border-radius: 8px;"
                )

    def display_world(self):
        type_map = {1: "E", 2: "N", 3: "H"}  # Modified to match game_manager.py
        world = self.manager.world
        rows, cols = self.manager.rows, self.manager.cols
        
        # Initialize the 2D list for cell labels
        self.cell_labels = []

        for r in range(rows):
            row_labels = []
            for c in range(cols):
                val = type_map[world[r][c]]
                cell = QLabel(val)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(80, 80)
                cell.setStyleSheet("border: 1px solid #666; background-color: #2e2e3e; color: white; font-size: 18px; border-radius: 8px;")
                self.grid_layout.addWidget(cell, r, c)
                row_labels.append(cell)
            self.cell_labels.append(row_labels)

    def end_simulation(self):
        self.timer.stop()
        final_msg = f"🛑 Simulation ended by user.\nFinal Score:\nHider: {self.manager.human_score} | Seeker: {self.manager.computer_score}"
        self.result_display.append(final_msg)
        self.status_label.setText("Simulation manually ended.")
        self.pause_button.setEnabled(False)

    def main_style_sheet(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
        }

        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #1e1e2f;
        }
        
        QTabBar::tab {
            background-color: #2e2e3e;
            color: white;
            padding: 1px 2px;
            border: 1px solid #444;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #3e3e5e;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #3a3a4a;
        }

        QTextEdit {
            background-color: #2c2c3c;
            border: 1px solid #444;
            padding: 1px;
        }

        #ResultDisplay {
            background-color: #2c2c3c;
            border: 1px solid #444;
            padding: 1px;
            font-size: 14px;
        }

        #PauseButton {
            background-color: #4a7c59;
            color: white;
            min-width: 120px;
            min-height: 40px;
            margin-left: 10px;
            padding: 8px 12px;
            font-size: 15px;
            border-radius: 5px;
        }

        #PauseButton:hover {
            background-color: #3a6c49;
        }

        #EndGameButton {
            padding: 10px;
            font-size: 15px;
            background-color: #a82323;
            color: white;
            border-radius: 6px;
            margin-top: 10px;
        }

        #EndGameButton:hover {
            background-color: #8c1c1c;
        }

        #ToggleHistoryButton {
            background-color: #666;
            color: white;
            padding: 8px 12px;
            font-size: 15px;
            border-radius: 5px;
        }

        #ToggleHistoryButton:hover {
            background-color: #555;
        }

        #StatusLabel {
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        #RoundScoreLabel {
            font-weight: bold;
            font-size: 14px;
            padding-right: 10px;
        }
        
        #MatrixLabel {
            font-weight: bold;
            margin-top: 5px;
            margin-bottom: 5px;
            font-size: 20px;
        }
        
        #MatrixTable {
            background-color: #2c2c3c;
            border: 1px solid #444;
            font-size: 16px;
        }
        
        #MatrixTable QHeaderView::section {
            background-color: #3c3c4c;
            color: white;
            padding: 1px;
            border: 1px solid #555;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimuGUI()
    window.show()
    sys.exit(app.exec())