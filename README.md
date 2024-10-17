# Video Creator

This application automates the creation of videos by combining images and MP3 files, with optional custom metadata and HTML templating.

## Setup

1. Clone the repository:
git clone https://github.com/yourusername/video-creator.git
cd video-creator
Copy
2. Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
Copy
3. Install the required packages:
pip install -r requirements.txt
Copy
4. Ensure you have the `names.json` file in the `resources` directory.

## Usage

Run the application:
python src/main.py
Copy
Follow the on-screen instructions to select image and audio folders, choose a template, and create videos.

## Features

- Bulk video creation from folders of images and audio files
- Single video creation with manual file selection
- Custom HTML templating for video frames
- Random or custom metadata generation

## Project Structure

- `src/`: Source code
  - `main.py`: Entry point
  - `ui/`: User interface
  - `core/`: Core functionality
  - `config/`: Configuration and settings
  - `template/`: HTML templates
  - `output/`: Generated videos
- `resources/`: Resource files
- `requirements.txt`: Python dependencies
- `README.md`: This file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.