# PySide6-based GUI skeleton for Learning Assistant
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextBrowser, QLineEdit, QPushButton, QLabel
)
import sys
import markdown
from multiprocessing import Process, Queue
from PySide6.QtCore import QTimer
from main import process_user_input

class BackendProcess:
    def __init__(self):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.process = Process(target=self.worker, args=(self.input_queue, self.output_queue))
        self.process.daemon = True
        self.process.start()

    @staticmethod
    def worker(input_queue, output_queue):
        while True:
            message = input_queue.get()
            if message == "__EXIT__":
                break
            output, status = process_user_input(message)
            output_queue.put((output, status))

    def send(self, message):
        self.input_queue.put(message)

    def get(self):
        if not self.output_queue.empty():
            return self.output_queue.get()
        return None

    def close(self):
        self.input_queue.put("__EXIT__")
        self.process.join()


class LearningAssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learning Assistant Chat")
        self.resize(600, 500)

        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Chat display area
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
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

        # Backend process
        self.backend = BackendProcess()
        # Timer to poll for backend results
        self.timer = QTimer()
        self.timer.setInterval(100)  # ms
        self.timer.timeout.connect(self.check_backend)

        # Maintain a list of messages for consistent formatting
        self.messages = []
        # Initialize chat display with blank HTML body
        self.chat_display.setHtml("<html><body></body></html>")
        # Show introductory message once on startup
        self.display_message("Assistant", "Welcome to Learning Assistant! How can I help you today?")

    def send_message(self):
        message = self.user_input.text().strip()
        if message:
            self.display_message("You", message)
            self.user_input.clear()
            self.send_button.setDisabled(True)
            self.user_input.setDisabled(True)
            self.loading_label.setText("Processing...")
            self.backend.send(message)
            self.timer.start()

    def check_backend(self):
        result = self.backend.get()
        if result:
            output, status = result
            self.on_backend_finished(output, status)
            self.timer.stop()

    def on_backend_finished(self, output, status):
        self.loading_label.setText("")
        if status == "exit":
            self.display_message("System", "Exiting...")
            self.user_input.setDisabled(True)
            self.send_button.setDisabled(True)
            self.backend.close()
            self.close()
        elif status == "clear":
            self.display_message("System", output)
            self.messages = []
            self.chat_display.setHtml("<html><body></body></html>")
            self.user_input.setDisabled(False)
            self.send_button.setDisabled(False)
            self.display_message("Assistant", "Welcome to Learning Assistant! How can I help you today?")
        else:
            self.display_message("Assistant", output)
            # Show confirmation if notes were saved
            if (isinstance(output, str) and ("note saved" in output.lower() or "notes saved" in output.lower())):
                self.display_message("System", "Your notes have been saved successfully.")
            self.user_input.setDisabled(False)
            self.send_button.setDisabled(False)
        # Always place cursor in text input after response
        self.user_input.setFocus()

    def display_message(self, sender, message):
        # Build HTML for the new message
        if sender == "You":
            html = (
                f'<div style="text-align: right; margin-bottom: 24px; margin-right: 8px; font-size: 16px;">'
                f'<b>{sender}:</b> {message}'
                f'</div>'
            )
        elif sender == "Assistant":
            msg = markdown.markdown(message).strip()
            # Remove leading/trailing <p> tags to avoid extra newlines
            if msg.startswith('<p>') and msg.endswith('</p>'):
                msg = msg[3:-4]
            html = (
                f'<div style="text-align: left; margin-bottom: 24px; font-size: 16px;">'
                f'<b>{sender}:</b> {msg}'
                f'</div>'
            )
        else:
            html = f'<div style="text-align: left; margin-bottom: 24px; font-size: 16px;"><b>{sender}:</b> {message}</div>'

        # Add the new message to the list
        self.messages.append(html)
        # Rebuild the chat display HTML from all messages
        all_html = "<html><body>" + "".join(self.messages) + "</body></html>"
        print(all_html)
        self.chat_display.setHtml(all_html)
        # Scroll to bottom after adding new message
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load QSS stylesheet
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = LearningAssistantGUI()
    window.show()
    sys.exit(app.exec())
