# src/ui/main_window.py

import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QLabel, QMessageBox, QLineEdit, QComboBox,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from core.autovid import VideoCreatorThread
from config.settings import TEMPLATE_DIR
import os

class StyledButton(QPushButton):
    def __init__(self, text, icon_path=None):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #6A5ACD;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #483D8B;
            }
            QPushButton:pressed {
                background-color: #7B68EE;
            }
        """)
        if icon_path:
            self.setIcon(QIcon(icon_path))

class VideoCreatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoVid by Stealthwork")
        self.setWindowIcon(QIcon("icons/logo.png"))
        self.setGeometry(100, 100, 700, 300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                font-size: 14px;
                color: #FFFFFF;
                margin-bottom: 5px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #6A5ACD;
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #6A5ACD;
                border-radius: 10px;
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
        """)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Logo
        # logo_label = QLabel()
        # pixmap = QPixmap("icons/logo.png")
        # scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # logo_label.setPixmap(scaled_pixmap)
        # logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # main_layout.addWidget(logo_label)

        # Template selection
        template_layout = QHBoxLayout()
        self.template_label = QLabel("Select Template:")
        self.template_dropdown = QComboBox()
        self.populate_template_dropdown()
        template_layout.addWidget(self.template_label)
        template_layout.addWidget(self.template_dropdown)
        main_layout.addLayout(template_layout)

        # Folder selection

        self.output_folder_button = StyledButton("Select Output Folder")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        main_layout.addWidget(self.output_folder_button)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        separator.setStyleSheet("background-color: #6A5ACD;")
        main_layout.addWidget(separator)

        self.manual_selection_label = QLabel("Batch Video Creation:")
        main_layout.addWidget(self.manual_selection_label)

        folder_selection_layout = QHBoxLayout()
        self.image_folder_button = StyledButton("Select Image Folder")
        self.image_folder_button.clicked.connect(self.select_image_folder)
        # main_layout.addWidget(self.image_folder_button)
        self.audio_folder_button = StyledButton("Select Audio Folder")
        self.audio_folder_button.clicked.connect(self.select_audio_folder)
        # main_layout.addWidget(self.audio_folder_button)
        folder_selection_layout.addWidget(self.image_folder_button)
        folder_selection_layout.addWidget(self.audio_folder_button)
        main_layout.addLayout(folder_selection_layout)

        # Bulk video creation
        self.create_video_button = StyledButton("Create Videos")
        self.create_video_button.clicked.connect(self.create_videos)
        main_layout.addWidget(self.create_video_button)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        separator.setStyleSheet("background-color: #6A5ACD;")
        main_layout.addWidget(separator)

        # Single video creation
        self.manual_selection_label = QLabel("Manual Selection:")
        main_layout.addWidget(self.manual_selection_label)

        file_selection_layout = QHBoxLayout()
        self.select_single_image_button = StyledButton("Select Image")
        self.select_single_image_button.clicked.connect(self.select_single_image)
        self.select_single_audio_button = StyledButton("Select Audio")
        self.select_single_audio_button.clicked.connect(self.select_single_audio)
        file_selection_layout.addWidget(self.select_single_image_button)
        file_selection_layout.addWidget(self.select_single_audio_button)
        main_layout.addLayout(file_selection_layout)

        self.artist_name_input = QLineEdit()
        self.artist_name_input.setPlaceholderText("Artist Name (optional)")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year (optional)")
        main_layout.addWidget(self.artist_name_input)
        main_layout.addWidget(self.year_input)

        self.create_single_video_button = StyledButton("Create Single Video")
        self.create_single_video_button.clicked.connect(self.create_single_video)
        main_layout.addWidget(self.create_single_video_button)

        # Status display
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold; color: #6A5ACD;")
        main_layout.addWidget(self.status_label)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initialize variables
        self.image_folder = ""
        self.audio_folder = ""
        self.output_folder = ""
        self.single_image = ""
        self.single_audio = ""

    def truncate(s):
        words = str(s).split() 
        output = []

        for word in words:
            if len(' '.join(output + [word])) > 15:
                break

            output.append(word)

        truncated = ' '.join(output)
        if len(truncated) < len(s):
            truncated += "..."

        return truncated

    def populate_template_dropdown(self):
        """Populate the template dropdown with available templates"""
        self.template_dropdown.addItem("No Template", "")
        for file in os.listdir(TEMPLATE_DIR):
            if file.endswith('.html'):
                self.template_dropdown.addItem(file, os.path.join(TEMPLATE_DIR, file))

    def select_image_folder(self):
        """Open a dialog to select the image folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.image_folder = folder
            self.image_folder_button.setText(f"Image Folder: {os.path.basename(folder)}")
            self.save_settings()

    def select_audio_folder(self):
        """Open a dialog to select the audio folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Audio Folder")
        if folder:
            self.audio_folder = folder
            self.audio_folder_button.setText(f"Audio Folder: {os.path.basename(folder)}")
            self.save_settings()

    def select_output_folder(self):
        """Open a dialog to select the output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_button.setText(f"Output Folder: {os.path.basename(folder)}")
            self.save_settings()

    def save_settings(self):
        """Save user settings to a JSON file"""
        settings = {
            "image_folder": self.image_folder,
            "audio_folder": self.audio_folder,
            "output_folder": self.output_folder
        }
        with open("user_settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        """Load user settings from a JSON file"""
        try:
            with open("user_settings.json", "r") as f:
                settings = json.load(f)
            self.image_folder = settings.get("image_folder", "")
            self.audio_folder = settings.get("audio_folder", "")
            self.output_folder = settings.get("output_folder", "")
            self.update_folder_buttons()
        except FileNotFoundError:
            pass  # If the file doesn't exist, use default values

    def update_folder_buttons(self):
        """Update labels with loaded settings"""
        if self.image_folder:
            self.image_folder_button.setText(f"Image Folder: {os.path.basename(self.image_folder)[:15]}")
        if self.audio_folder:
            self.audio_folder_button.setText(f"Audio Folder: {os.path.basename(self.audio_folder)[:15]}")
        if self.output_folder:
            self.output_folder_button.setText(f"Output Folder: {os.path.basename(self.output_folder)[:15]}")

    def select_single_image(self):
        """Open a dialog to select a single image file"""
        file, _ = QFileDialog.getOpenFileName(self, "Select Single Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file:
            self.single_image = file
            self.select_single_image_button.setText(f"Image: {os.path.basename(file)[:15]}")

    def select_single_audio(self):
        """Open a dialog to select a single audio file"""
        file, _ = QFileDialog.getOpenFileName(self, "Select Single Audio", "", "Audio Files (*.mp3)")
        if file:
            self.single_audio = file
            self.select_single_audio_button.setText(f"Audio: {os.path.basename(file)[:15]}")

    def create_videos(self):
        """Start the process of creating multiple videos"""
        if not self.image_folder or not self.audio_folder or not self.output_folder:
            QMessageBox.warning(self, "Error", "Please select image folder, audio folder, and output folder.")
            return

        self.status_label.setText("Creating videos...")
        self.create_video_button.setEnabled(False)

        selected_template = self.template_dropdown.currentData()
        self.thread = VideoCreatorThread(self.image_folder, self.audio_folder, selected_template, output_folder=self.output_folder)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.video_creation_finished)
        self.thread.start()

    def create_single_video(self):
        """Start the process of creating a single video"""
        if not self.single_image or not self.single_audio or not self.output_folder:
            QMessageBox.warning(self, "Error", "Please select an image, audio file, and output folder.")
            return

        artist_name = self.artist_name_input.text()
        year = self.year_input.text()

        self.status_label.setText("Creating single video...")
        self.create_single_video_button.setEnabled(False)

        selected_template = self.template_dropdown.currentData()
        self.thread = VideoCreatorThread(self.image_folder, self.audio_folder, selected_template,
                                         single_image=self.single_image, single_audio=self.single_audio,
                                         custom_artist=artist_name, custom_year=year, output_folder=self.output_folder)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.video_creation_finished)
        self.thread.start()

    def update_progress(self, message):
        """Update the status label with progress messages"""
        self.status_label.setText(message)

    def video_creation_finished(self, success, message):
        """Handle the completion of video creation"""
        self.create_video_button.setEnabled(True)
        self.create_single_video_button.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", f"Videos created successfully in:\n{self.output_folder}")
        else:
            QMessageBox.warning(self, "Error", message)
        self.status_label.setText("")