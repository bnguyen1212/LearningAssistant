# PySide6-based GUI skeleton for Learning Assistant
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
import sys
import markdown
from main import process_user_input

class LearningAssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learning Assistant Chat")
        self.resize(600, 500)

        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(350)
        main_layout.addWidget(self.chat_display)

        # Loading indicator
        self.loading_label = QLabel("")
        main_layout.addWidget(self.loading_label)

        # User input area
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message...")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def send_message(self):
        message = self.user_input.text().strip()
        if message:
            self.display_message("You", message)
            self.user_input.clear()
            self.send_button.setDisabled(True)
            self.user_input.setDisabled(True)
            self.loading_label.setText("Processing...")
            # Run backend in main thread (blocking)
            output, status = process_user_input(message)
            self.on_backend_finished(output, status)

    def on_backend_finished(self, output, status):
        self.loading_label.setText("")
        if status == "exit":
            self.display_message("System", "Exiting...")
            self.user_input.setDisabled(True)
            self.send_button.setDisabled(True)
        elif status == "clear":
            self.display_message("System", output)
            self.chat_display.clear()
            self.user_input.setDisabled(False)
            self.send_button.setDisabled(False)
        else:
            self.display_message("Assistant", output)
            self.user_input.setDisabled(False)
            self.send_button.setDisabled(False)

    def display_message(self, sender, message):
        if sender == "Assistant":
            html = markdown.markdown(message)
            self.chat_display.append(f"<b>{sender}:</b> {html}")
        else:
            self.chat_display.append(f"<b>{sender}:</b> {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load QSS stylesheet
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = LearningAssistantGUI()
    window.show()
    sys.exit(app.exec())
