# src/ui/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QFileDialog, QLabel, QMessageBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from core.video_creator import VideoCreatorThread
from config.settings import OUTPUT_DIR, TEMPLATE_DIR
import os

class VideoCreatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Creator")
        self.setGeometry(100, 100, 500, 450)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        
        layout = QVBoxLayout()
        # Template selection
        self.template_label = QLabel("Select Template:")
        layout.addWidget(self.template_label)
        self.template_dropdown = QComboBox()
        self.populate_template_dropdown()
        layout.addWidget(self.template_dropdown)

        # Image folder selection
        self.image_folder_label = QLabel("Image Folder: Not selected")
        layout.addWidget(self.image_folder_label)
        self.select_image_folder_button = QPushButton("Select Image Folder")
        self.select_image_folder_button.clicked.connect(self.select_image_folder)
        layout.addWidget(self.select_image_folder_button)

        # Audio folder selection
        self.audio_folder_label = QLabel("Audio Folder: Not selected")
        layout.addWidget(self.audio_folder_label)
        self.select_audio_folder_button = QPushButton("Select Audio Folder")
        self.select_audio_folder_button.clicked.connect(self.select_audio_folder)
        layout.addWidget(self.select_audio_folder_button)



        # Bulk video creation
        self.create_video_button = QPushButton("Create Videos")
        self.create_video_button.clicked.connect(self.create_videos)
        layout.addWidget(self.create_video_button)

        # Single video creation
        self.manual_selection_label = QLabel("Manual Selection:")
        layout.addWidget(self.manual_selection_label)
        self.select_single_image_button = QPushButton("Select Single Image")
        self.select_single_image_button.clicked.connect(self.select_single_image)
        layout.addWidget(self.select_single_image_button)
        self.select_single_audio_button = QPushButton("Select Single Audio")
        self.select_single_audio_button.clicked.connect(self.select_single_audio)
        layout.addWidget(self.select_single_audio_button)
        self.artist_name_input = QLineEdit()
        self.artist_name_input.setPlaceholderText("Artist Name (optional)")
        layout.addWidget(self.artist_name_input)
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Year (optional)")
        layout.addWidget(self.year_input)
        self.create_single_video_button = QPushButton("Create Single Video")
        self.create_single_video_button.clicked.connect(self.create_single_video)
        layout.addWidget(self.create_single_video_button)

        # Status display
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize variables
        self.image_folder = ""
        self.audio_folder = ""
        self.single_image = ""
        self.single_audio = ""

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
            self.image_folder_label.setText(f"Image Folder: {folder}")

    def select_audio_folder(self):
        """Open a dialog to select the audio folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Audio Folder")
        if folder:
            self.audio_folder = folder
            self.audio_folder_label.setText(f"Audio Folder: {folder}")

    def select_single_image(self):
        """Open a dialog to select a single image file"""
        file, _ = QFileDialog.getOpenFileName(self, "Select Single Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file:
            self.single_image = file
            self.select_single_image_button.setText(f"Image: {os.path.basename(file)}")

    def select_single_audio(self):
        """Open a dialog to select a single audio file"""
        file, _ = QFileDialog.getOpenFileName(self, "Select Single Audio", "", "Audio Files (*.mp3)")
        if file:
            self.single_audio = file
            self.select_single_audio_button.setText(f"Audio: {os.path.basename(file)}")

    def create_videos(self):
        """Start the process of creating multiple videos"""
        if not self.image_folder or not self.audio_folder:
            QMessageBox.warning(self, "Error", "Please select image folder and audio folder.")
            return

        self.status_label.setText("Creating videos...")
        self.create_video_button.setEnabled(False)

        selected_template = self.template_dropdown.currentData()
        self.thread = VideoCreatorThread(self.image_folder, self.audio_folder, selected_template)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.video_creation_finished)
        self.thread.start()

    def create_single_video(self):
        """Start the process of creating a single video"""
        if not self.single_image or not self.single_audio:
            QMessageBox.warning(self, "Error", "Please select an image and audio file.")
            return

        artist_name = self.artist_name_input.text()
        year = self.year_input.text()

        self.status_label.setText("Creating single video...")
        self.create_single_video_button.setEnabled(False)

        selected_template = self.template_dropdown.currentData()
        self.thread = VideoCreatorThread(self.image_folder, self.audio_folder, selected_template,
                                         single_image=self.single_image, single_audio=self.single_audio,
                                         custom_artist=artist_name, custom_year=year)
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
            QMessageBox.information(self, "Success", f"Videos created successfully in:\n{OUTPUT_DIR}")
        else:
            QMessageBox.warning(self, "Error", message)
        self.status_label.setText("")