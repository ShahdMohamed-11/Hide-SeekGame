import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QTextEdit, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer

from simu_back import SimuManager  # Make sure the filename matches

class SimuGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Computer vs Computer Simulation")
        self.resize(700, 750)
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

        self.status_label = QLabel("Initializing simulation...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFixedHeight(250)
        self.layout.addWidget(self.result_display)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.end_button = QPushButton("End Simulation")
        self.end_button.clicked.connect(self.end_simulation)
        self.layout.addWidget(self.end_button)

        self.setLayout(self.layout)

    def run_simulation(self):
        self.manager.start_new_game(human_role=None)
        self.display_world()
        self.status_label.setText("Running simulation: Computer (Hider) vs Computer (Seeker)")
        self.result_display.append("Game started. Hider & Seeker strategies computed.\n")
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
                "border: 1px solid #666; background-color: #4CAF50; color: white; font-size: 18px; font-weight: bold;"
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

    def reset_cell_colors(self):
        # Reset all cells to their original appearance
        for r in range(self.manager.rows):
            for c in range(self.manager.cols):
                cell_type = self.manager.world[r][c]
                type_map = {1: "N", 2: "E", 3: "H"}
                val = type_map[cell_type]
                self.cell_labels[r][c].setText(val)
                self.cell_labels[r][c].setStyleSheet(
                    "border: 1px solid #666; background-color: #2e2e3e; color: white; font-size: 18px; border-radius: 8px;"
                )

    def display_world(self):
        type_map = {1: "N", 2: "E", 3: "H"}
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
                cell.setFixedSize(60, 60)
                cell.setStyleSheet("border: 1px solid #666; background-color: #2e2e3e; color: white; font-size: 18px; border-radius: 8px;")
                self.grid_layout.addWidget(cell, r, c)
                row_labels.append(cell)
            self.cell_labels.append(row_labels)

    def end_simulation(self):
        self.timer.stop()
        final_msg = f"🛑 Simulation ended by user.\nFinal Score:\nHider: {self.manager.human_score} | Seeker: {self.manager.computer_score}"
        self.result_display.append(final_msg)
        self.status_label.setText("Simulation manually ended.")

    def main_style_sheet(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 16px;
        }

        QTextEdit {
            background-color: #2c2c3c;
            border: 1px solid #444;
            padding: 8px;
        }

        QPushButton {
            padding: 10px;
            font-size: 15px;
            background-color: #a82323;
            color: white;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #8c1c1c;
        }

        QLabel {
            font-weight: bold;
            border-radius: 8px;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimuGUI()
    window.show()
    sys.exit(app.exec())