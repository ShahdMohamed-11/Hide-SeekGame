from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton,
    QLabel, QGridLayout, QMessageBox, QHBoxLayout, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt
import sys
import copy

from game_manager import GameManager


class GameGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hider vs Seeker Game")
        self.resize(650, 650)  
        self.manager = GameManager()
        self.cell_buttons = []
        self.initial_world = None  # Store the initial world state
        self.round_finished = False  # Flag to track if a round has been completed
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

        # Status message with round and score on the right
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Choose your role to start.")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self.status_label)

        self.round_score_label = QLabel("")
        self.round_score_label.setObjectName("RoundScoreLabel")
        self.round_score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self.round_score_label)

        self.layout.addLayout(status_layout)

        # Result message area (inside app)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setObjectName("ResultDisplay")
        self.layout.addWidget(self.result_display)

        # History toggle button
        self.history_toggle_button = QPushButton("Hide History")
        self.history_toggle_button.setObjectName("ToggleHistoryButton")
        self.history_toggle_button.clicked.connect(self.toggle_history_display)
        self.layout.addWidget(self.history_toggle_button)

        # Game board layout with Next Round button alongside
        game_layout = QHBoxLayout()
        
        # World matrix (game board)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        self.grid_container = QWidget()
        self.grid_container.setLayout(self.grid_layout)
        self.grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        game_layout.addWidget(self.grid_container, stretch=1)
        
        # Add next round button beside the world grid
        side_controls = QVBoxLayout()
        self.next_round_button = QPushButton("Next Round")
        self.next_round_button.setObjectName("NextRoundButton")
        self.next_round_button.clicked.connect(self.refresh_world)
        self.next_round_button.setEnabled(False)  # Initially disabled until game starts
        side_controls.addWidget(self.next_round_button)
        side_controls.addStretch()  # Push the button to the top
        game_layout.addLayout(side_controls)
        
        self.layout.addLayout(game_layout)

        # End game button at the bottom
        self.end_game_button = QPushButton("End Game")
        self.end_game_button.setObjectName("EndGameButton")
        self.end_game_button.clicked.connect(self.end_game)
        self.layout.addWidget(self.end_game_button)

        self.setLayout(self.layout)

    def update_round_score_display(self):
        round_num = len(self.manager.game_history)  # rounds played so far
        human = self.manager.human_score
        computer = self.manager.computer_score
        self.round_score_label.setText(f"Round {round_num} | Score: You {human} - CPU {computer}")

    def start_game(self):
        role = self.role_selector.currentText().lower()

        self.manager.start_new_game(role)
        self.status_label.setText(f"You are the {role.capitalize()}.")
        self.result_display.setText("Game started.\n")
        
        # Store the initial world state
        self.initial_world = copy.deepcopy(self.manager.world)
        
        # Reset the round_finished flag
        self.round_finished = False
        
        self.display_world()
        self.update_round_score_display()
        self.next_round_button.setEnabled(True)  # Enable the next round button

        if role == "seeker":
            # Computer selects hiding spot
            try:
                self.manager.start_round()  # Just sets the hider_index
                self.result_display.append("Computer (Hider) has selected a position.\n")
                self.status_label.setText("Your turn to seek! Click a cell.")
                self.update_round_score_display()
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

    def refresh_world(self):
        """Refresh the world display to its initial state"""
        if self.initial_world is None:
            return
        
        # Reset all cells to their default appearance
        self.reset_cell_colors()
        
        # Re-display the initial world state
        type_map = {1: "N", 2: "E", 3: "H"}
        rows, cols = self.manager.rows, self.manager.cols
        
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx < len(self.cell_buttons):
                    symbol = type_map[self.initial_world[r][c]]
                    self.cell_buttons[idx].setText(symbol)
                    self.cell_buttons[idx].setStyleSheet("")  # Reset styling
        
        # Update status based on game state
        if len(self.manager.game_history) > 0:
            if self.manager.human_role == "seeker":
                self.status_label.setText("Your turn to seek! Click a cell.")
            else:
                self.status_label.setText("Choose a hiding spot! Click a cell.")
        
        # Reset the round_finished flag so player can interact with cells again
        self.round_finished = False
    def reset_cell_colors(self):
        # Reset all cells to their default color
        for btn in self.cell_buttons:
            btn.setStyleSheet("")

    def cell_clicked(self, row, col):
        role = self.manager.human_role
        
        # Check if round is finished and player needs to click Next Round
        if self.round_finished:
            QMessageBox.warning(self, "Next Round Required", 
                               "You must click 'Next Round' before making a new move!")
            return
            
        try:
            if role == "hider" and self.manager.current_round == 0:
                self.reset_cell_colors()
                self.manager.start_round(human_row=row, human_col=col)
                self.status_label.setText("Round started. Waiting for computer move...")
                
                # Set player position label to "P"
                index = row * self.manager.cols + col
                self.cell_buttons[index].setText("P")
                
                self.display_computer_move()
                # Set round_finished flag after move is complete
                self.round_finished = True
                self.status_label.setText("Round finished. Click 'Next Round' to continue.")

            elif role == "seeker" and self.manager.seeker_index is None:
                self.reset_cell_colors()
                result = self.manager.finish_round(human_row=row, human_col=col)
                
                # Process the result and update cell colors
                history = self.manager.game_history[-1]
                human_index = row * self.manager.cols + col
                
                # Always label the player's position as "P"
                self.cell_buttons[human_index].setText("P")
                
                if "Success" in history["result"]:
                    # Found it! Color the cell green
                    self.cell_buttons[human_index].setStyleSheet("background-color: green; color: white;")
                else:
                    # Missed it! Color the cell red
                    self.cell_buttons[human_index].setStyleSheet("background-color: #cc3232; color: white;")
                    
                    # Show where the hider actually was
                    hider_index = history["hider"]
                    if hider_index != human_index:  # Don't overwrite if same position
                        self.cell_buttons[hider_index].setStyleSheet("background-color: #4a7c59; color: white;")
                        self.cell_buttons[hider_index].setText("C")  # Computer position
                
                self.display_computer_move()

                # Start the next round: computer chooses a new hiding spot
                try:
                    self.manager.start_round()
                    self.result_display.append("Computer (Hider) has selected a new position.\n")
                    self.status_label.setText("Round finished. Click 'Next Round' to continue.")
                    self.update_round_score_display()
                    # Set round_finished flag after move is complete
                    self.round_finished = True
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to start new round: {e}")

            elif role == "hider":
                self.reset_cell_colors()
                self.manager.start_round(human_row=row, human_col=col)
                self.status_label.setText("Next round started. Waiting for computer move...")
                
                # Set player position label to "P"
                index = row * self.manager.cols + col
                self.cell_buttons[index].setText("P")
                
                self.display_computer_move()
                # Set round_finished flag after move is complete
                self.round_finished = True
                self.status_label.setText("Round finished. Click 'Next Round' to continue.")
            else:
                QMessageBox.information(self, "Wait", "It's not your turn yet.")
            
            self.update_round_score_display()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def display_computer_move(self):
        history = self.manager.game_history[-1]
        seeker = history["seeker"]
        hider = history["hider"]
        result = history["result"]

        seeker_row = seeker // self.manager.cols
        seeker_col = seeker % self.manager.cols
        hider_row = hider // self.manager.cols
        hider_col = hider % self.manager.cols
        
        seeker_pos = (seeker_row, seeker_col)
        hider_pos = (hider_row, hider_col)

        # Display results when player is hider
        if self.manager.human_role == "hider":
            # Computer is seeker
            computer_index = seeker
            # Label the computer position as "C"
            self.cell_buttons[computer_index].setText("C")
            
            if "Success" in result:
                # Computer found the player - show failure
                self.cell_buttons[computer_index].setStyleSheet("background-color: green; color: white;")
                # Mark the player's position as caught with red
                human_index = hider  # Player is the hider
                if human_index != computer_index:  # Don't overwrite if same position
                    self.cell_buttons[human_index].setStyleSheet("background-color: #cc3232; color: white;")
            else:
                # Computer missed - show success for player
                self.cell_buttons[computer_index].setStyleSheet("background-color: #cc3232; color: white;")
                # Mark the player's position as safe with green
                human_index = hider  # Player is the hider
                if human_index != computer_index:  # Don't overwrite if same position
                    self.cell_buttons[human_index].setStyleSheet("background-color: #4a7c59; color: white;")

        msg = f"🕹️ Round {history['round']}:\n"
        msg += f"Seeker chose: {seeker_pos}\n"
        msg += f"Hider was at: {hider_pos}\n"
        msg += f"{result}\n"
        msg += f"Score → You: {self.manager.human_score} | Computer: {self.manager.computer_score}\n\n"

        self.result_display.append(msg)
        self.update_round_score_display()

    def toggle_history_display(self):
        if self.result_display.isVisible():
            self.result_display.hide()
            self.history_toggle_button.setText("Show History")
        else:
            self.result_display.show()
            self.history_toggle_button.setText("Hide History")

    def end_game(self):
        final_msg = f"🎮 Game Over!\nFinal Score:\nYou: {self.manager.human_score} | Computer: {self.manager.computer_score}"
        QMessageBox.information(self, "Game Ended", final_msg)
        self.status_label.setText("Game ended. Start a new one?")
        self.result_display.append("Game has been ended by user.\n")
        self.next_round_button.setEnabled(False)  # Disable next round button when game ends
        self.round_finished = False  # Reset the flag
        self.update_round_score_display()

    def main_style_sheet(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 16px;
        }

        #RoleSelector, #StartButton, #EndGameButton, #ToggleHistoryButton, #NextRoundButton {
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

        #NextRoundButton {
            background-color: #4a7c59;
            color: white;
            min-width: 120px;
            min-height: 40px;
            margin-left: 10px;
        }

        #NextRoundButton:hover {
            background-color: #3a6c49;
        }

        #NextRoundButton:disabled {
            background-color: #555;
            color: #999;
        }

        #EndGameButton {
            background-color: #a82323;
            color: white;
            margin-top: 10px;
        }

        #EndGameButton:hover {
            background-color: #8c1c1c;
        }

        #ToggleHistoryButton {
            background-color: #666;
            color: white;
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