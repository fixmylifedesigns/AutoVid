# src/core/autovid.py

import os
import random
import traceback
import tempfile
import shutil
import base64
from io import BytesIO
import time
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import NAMES_FILE, TEMPLATE_DIR
from core.utils import load_names, load_tracking, save_tracking, sanitize_filename, parse_filename

class VideoCreatorThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, image_folder, audio_folder, html_template, single_image=None, single_audio=None, custom_artist=None, custom_year=None, output_folder=None):
        super().__init__()
        self.image_folder = os.path.abspath(image_folder)
        self.audio_folder = os.path.abspath(audio_folder)
        self.html_template = html_template
        self.single_image = single_image
        self.single_audio = single_audio
        self.custom_artist = custom_artist
        self.custom_year = custom_year
        self.output_folder = output_folder or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        self.temp_dir = tempfile.mkdtemp()
        self.screenshots_dir = os.path.join(self.output_folder, 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def run(self):
        try:
            # Load names and tracking data
            first_names, last_names = load_names(NAMES_FILE)
            tracking_data = load_tracking()

            # Setup Selenium WebDriver
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=service, options=options)

            # Get list of images and audio files
            if self.single_image and self.single_audio:
                image_files = [self.single_image]
                audio_files = [self.single_audio]
            else:
                # image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                image_files = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                audio_files = [os.path.join(self.audio_folder, f) for f in os.listdir(self.audio_folder) if f.lower().endswith('.mp3')]

            if not image_files or not audio_files:
                self.finished_signal.emit(False, "No image or audio files found.")
                return

            # Load HTML template if provided
            use_template = bool(self.html_template)
            template = None
            if use_template:
                with open(self.html_template, 'r') as file:
                    template = Template(file.read())

            # Create output and screenshots directories
            os.makedirs(self.output_folder, exist_ok=True)
            os.makedirs(self.screenshots_dir, exist_ok=True)

            # Process each audio file
            for audio in audio_files:
                self.progress_signal.emit(f"Processing {os.path.basename(audio)}")
                print(f"Debug - Processing audio: {audio}")  # Debug print

                # Generate or use provided metadata
                song_name, artist_name, year = self.generate_metadata(audio, first_names, last_names, tracking_data)

                # Select image and create video
                selected_image = self.select_image(image_files)
                print(f"Debug - Selected image: {selected_image}")  # Debug print
                self.create_video(driver, template, selected_image, audio, song_name, artist_name, year, use_template)

                # Update tracking data
                self.update_tracking(tracking_data, song_name, artist_name, year, selected_image)

            driver.quit()
            save_tracking(tracking_data)

            # Clean up
            shutil.rmtree(self.temp_dir)

            self.finished_signal.emit(True, f"Videos created successfully in: {self.output_folder}")
        except Exception as e:
            error_message = f"Error creating video: {str(e)}\n{traceback.format_exc()}"
            print(error_message)  # Print to console
            self.finished_signal.emit(False, error_message)

    def generate_metadata(self, audio, first_names, last_names, tracking_data):
        """Generate or retrieve metadata for the audio file"""
        song_name, _, _ = parse_filename(os.path.basename(audio))
        if not song_name:
            song_name = os.path.splitext(os.path.basename(audio))[0]

        if self.custom_artist:
            artist_name = self.custom_artist
        else:
            artist_name = f"{random.choice(first_names)} {random.choice(last_names)}"

        if self.custom_year:
            year = self.custom_year
        else:
            year = str(random.randint(1978, 1986))

        return song_name, artist_name, year

    def select_image(self, image_files):
        if self.single_image:
            return os.path.join(self.image_folder, self.single_image)
        return random.choice(image_files)  # image_files should already contain full paths

    def create_video(self, driver, template, image_path, audio_path, song_name, artist_name, year, use_template):
        print(f"Debug - Image path: {image_path}")  # Debug print
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # If using a template, ensure screenshot_path is correctly set
        if use_template and template is not None:
            screenshot_path = self.create_screenshot(driver, template, image_path, song_name, artist_name, year)
        else:
            screenshot_path = image_path
        
        print(f"Debug - Screenshot path: {screenshot_path}")  # Debug print
        """Create a video from the given image and audio"""
        if use_template and template is not None:
            screenshot_path = self.create_screenshot(driver, template, image_path, song_name, artist_name, year)
        else:
            screenshot_path = image_path

        audio_clip = AudioFileClip(audio_path)  # Make sure audio_path is the full path
        img_clip = ImageClip(screenshot_path).set_duration(audio_clip.duration)
        video_clip = img_clip.set_audio(audio_clip)

        output_video_name = f"{sanitize_filename(artist_name)}_{sanitize_filename(song_name)}_{year}.mp4"
        output_path = os.path.join(self.output_folder, output_video_name)

        video_clip.write_videofile(output_path, fps=24)

    def create_screenshot(self, driver, template, image_path, song_name, artist_name, year):
        """Create a screenshot using the HTML template"""

        # Dictionary to store base64-encoded images
        image_data = {}

        # Base64 encode template images (e.g., container_background, photo_background, logo)
        for img_name in ['container_background', 'photo_background', 'logo']:
            for ext in ['.png', '.jpg', '.jpeg']:
                img_path = os.path.join(TEMPLATE_DIR, f"{img_name}{ext}")
                if os.path.exists(img_path):
                    with open(img_path, "rb") as image_file:
                        image_data[img_name] = base64.b64encode(image_file.read()).decode()
                    break  # Stop after finding the first valid image

        # Base64 encode the selected image passed to the function
        with open(image_path, "rb") as image_file:
            main_image_data = base64.b64encode(image_file.read()).decode()

        # Render the HTML template with all the image data
        html_content = template.render(
            container_background=image_data.get('container_background', ''),
            photo_background=image_data.get('photo_background', ''),
            logo=image_data.get('logo', ''),
            image_base64=main_image_data,
            song_name=song_name,
            song_artist=artist_name,
            song_year=year
        )

        # Save the rendered HTML to a temporary file
        temp_html = os.path.join(self.temp_dir, 'temp.html')
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Load the HTML in the browser via Selenium
        driver.get(f"file://{os.path.abspath(temp_html)}")

        # Wait for the page to finish rendering
        driver.implicitly_wait(2)

        # Get the full size of the page content
        width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

        # Set the browser window size
        driver.set_window_size(width, height)

        # Wait for the resize to take effect
        time.sleep(1)

        # Take the screenshot
        screenshot = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))

        # Save the screenshot
        screenshot_path = os.path.join(self.screenshots_dir, f"{song_name}_{artist_name}_{year}.png")
        image.save(screenshot_path)

        # Maybe remove ?
        # Clean up the temporary HTML file
        os.remove(temp_html)
        screenshot_path = os.path.join(self.screenshots_dir, f"{song_name}_{artist_name}_{year}.png")
        print(f"Debug - Saving screenshot to: {screenshot_path}")  # Debug print
        image.save(screenshot_path)
        
        return screenshot_path

    def update_tracking(self, tracking_data, song_name, artist_name, year, image):
        """Update the tracking data"""
        if not self.single_audio:
            if 'songs' not in tracking_data:
                tracking_data['songs'] = []
            if 'combinations' not in tracking_data:
                tracking_data['combinations'] = []
            if 'images' not in tracking_data:
                tracking_data['images'] = []

            tracking_data['songs'].append(song_name)
            tracking_data['combinations'].append(f"{artist_name}_{song_name}_{year}")
            tracking_data['images'].append({
                'song': song_name,
                'artist': artist_name,
                'year': year,
                'image': os.path.basename(image)
            })