from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton,
    QLabel, QGridLayout, QMessageBox, QHBoxLayout, QTextEdit
)
from PyQt6.QtCore import Qt
import sys

from game_manager import GameManager


class GameGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hider vs Seeker Game")
        self.setFixedSize(650, 650)  
        self.manager = GameManager()
        self.cell_buttons = []
        self.init_ui()
        self.setStyleSheet(self.main_style_sheet())

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Top: Role selection and start button
        top_controls = QHBoxLayout()
        self.role_selector = QComboBox()
        self.role_selector.addItems(["Hider", "Seeker"])
        self.role_selector.setObjectName("RoleSelector")
        top_controls.addWidget(self.role_selector)

        self.start_button = QPushButton("Start New Game")
        self.start_button.setObjectName("StartButton")
        self.start_button.clicked.connect(self.start_game)
        top_controls.addWidget(self.start_button)
        self.layout.addLayout(top_controls)

        # Status message
        self.status_label = QLabel("Choose your role to start.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("StatusLabel")
        self.layout.addWidget(self.status_label)

        # Result message area (inside app)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setObjectName("ResultDisplay")
        self.layout.addWidget(self.result_display)

        # World matrix (game board)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        self.layout.addLayout(self.grid_layout)

        # End game button
        self.end_game_button = QPushButton("End Game")
        self.end_game_button.setObjectName("EndGameButton")
        self.end_game_button.clicked.connect(self.end_game)
        self.layout.addWidget(self.end_game_button)

        self.setLayout(self.layout)

    def start_game(self):
        role = self.role_selector.currentText().lower()
        if role not in ["hider", "seeker"]:
            QMessageBox.warning(self, "Invalid Role", "Please select a valid role.")
            return

        self.manager.start_new_game(role)
        self.status_label.setText(f"You are the {role.capitalize()}.")
        self.result_display.setText("Game started.\n")
        self.display_world()

        if role == "seeker":
            # Computer selects hiding spot
            try:
                self.manager.start_round()  # Just sets the hider_index
                self.result_display.append("Computer (Hider) has selected a position.\n")
                self.status_label.setText("Your turn to seek! Click a cell.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start round: {e}")


    def display_world(self):
        for btn in self.cell_buttons:
            btn.deleteLater()
        self.cell_buttons.clear()

        type_map = {1: "N", 2: "E", 3: "H"}
        world = self.manager.world
        rows, cols = self.manager.rows, self.manager.cols

        for r in range(rows):
            for c in range(cols):
                symbol = type_map[world[r][c]]
                btn = QPushButton(symbol)
                btn.setFixedSize(80, 80)
                btn.setObjectName("GridButton")
                btn.clicked.connect(lambda _, row=r, col=c: self.cell_clicked(row, col))
                self.grid_layout.addWidget(btn, r, c)
                self.cell_buttons.append(btn)

    def cell_clicked(self, row, col):
        role = self.manager.human_role
        try:
            if role == "hider" and self.manager.current_round == 0:
                self.manager.start_round(human_row=row, human_col=col)
                self.status_label.setText("Round started. Waiting for computer move...")
                self.display_computer_move()

            elif role == "seeker" and self.manager.seeker_index is None:
                self.manager.finish_round(human_row=row, human_col=col)
                self.display_computer_move()

                # Start the next round: computer chooses a new hiding spot
                try:
                    self.manager.start_round()
                    self.result_display.append("Computer (Hider) has selected a new position.\n")
                    self.status_label.setText("Next round started. Your turn to seek!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to start new round: {e}")

            elif role == "hider":
                self.manager.start_round(human_row=row, human_col=col)
                self.status_label.setText("Next round started. Waiting for computer move...")
                self.display_computer_move()
            else:
                QMessageBox.information(self, "Wait", "It's not your turn yet.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def display_computer_move(self):
        history = self.manager.game_history[-1]
        seeker = history["seeker"]
        hider = history["hider"]
        result = history["result"]

        seeker_pos = (seeker // self.manager.cols, seeker % self.manager.cols)
        hider_pos = (hider // self.manager.cols, hider % self.manager.cols)

        msg = f"🕹️ Round {history['round']}:\n"
        msg += f"Seeker chose: {seeker_pos}\n"
        msg += f"Hider was at: {hider_pos}\n"
        msg += f"{result}\n"
        msg += f"Score → You: {self.manager.human_score} | Computer: {self.manager.computer_score}\n\n"

        self.result_display.append(msg)

    def end_game(self):
        final_msg = f"🎮 Game Over!\nFinal Score:\nYou: {self.manager.human_score} | Computer: {self.manager.computer_score}"
        QMessageBox.information(self, "Game Ended", final_msg)
        self.status_label.setText("Game ended. Start a new one?")
        self.result_display.append("Game has been ended by user.\n")

    def main_style_sheet(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 16px;
        }

        #RoleSelector, #StartButton, #EndGameButton {
            padding: 8px 12px;
            font-size: 15px;
            border-radius: 5px;
        }

        #StartButton {
            background-color: #0078d7;
            color: white;
        }

        #StartButton:hover {
            background-color: #005fa3;
        }

        #EndGameButton {
            background-color: #a82323;
            color: white;
            margin-top: 10px;
        }

        #EndGameButton:hover {
            background-color: #8c1c1c;
        }

        #StatusLabel {
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        #ResultDisplay {
            background-color: #2c2c3c;
            border: 1px solid #444;
            padding: 8px;
            font-size: 14px;
            height: 150px;
        }

        QPushButton#GridButton {
            background-color: #2e2e3e;
            color: white;
            font-size: 20px;
            border-radius: 10px;
            border: 2px solid #444;
        }

        QPushButton#GridButton:hover {
            background-color: #3e3e5e;
            border: 2px solid #888;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameGUI()
    window.show()
    sys.exit(app.exec())
