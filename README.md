# 🎬 YoutubeDownloader

![version](https://img.shields.io/badge/version-1.0.0-blue.svg)  ![license](https://img.shields.io/badge/license-MIT-green.svg)  ![python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)  ![status](https://img.shields.io/badge/status-stable-brightgreen.svg)

A **powerful, beginner-friendly, and interactive YouTube downloader** built with [pytubefix](https://pypi.org/project/pytubefix/) and `ffmpeg`.
Download videos 🎥, extract audios 🎵, or merge them together seamlessly ✅.

---

## 🌹 Requirements

- 🐍 **Python**: `>=3.9`
- 📦 **Dependencies**:
  - [pytubefix](https://pypi.org/project/pytubefix/)
  - [tqdm](https://pypi.org/project/tqdm/)
  - [termcolor](https://pypi.org/project/termcolor/)
  - [ffmpeg-python](https://pypi.org/project/ffmpeg-python/)
- 🎬 **FFmpeg**: required for merging video and audio streams. Must be available in your system PATH.
- ✅ Supported OS: Linux, macOS, Windows

---

## 🎯 Objectives

- 🚀 Provide an **easy-to-use tool** for downloading YouTube videos and playlists.
- 🎥 Allow users to **choose video resolutions** (with size details).
- 🎵 Support both **progressive streams** (video+audio combined) and **separate streams** (video-only + audio).
- 🔗 Handle both **single video links** and full **playlists**.
- 🛠️ Automatically **merge audio + video** using `ffmpeg`.
- 🔄 Manage downloads using an **interactive download queue**.

### ✨ Features

- ✅ Download **single videos** or **full playlists**
- ✅ Interactive **resolution selection**
- ✅ Download **audio-only streams**
- ✅ Auto-create directories for videos, audios, and merged files
- ✅ Intelligent skipping if file already exists
- ✅ Automatic **merging** of separate audio/video tracks
- ✅ Easy **batch download** via `.txt` file with URLs
- ✅ **Download Queue**: Build a list of videos to download, choose to add to or clear the existing queue.
- ✅ **Interactive Queue Management**: Change resolution of items already in the queue before starting the download.
- ✅ **Duplicate Prevention**: Automatically skip adding the same video URL to the queue multiple times.

---

## ⚙️ Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/hosseingz/youtube_downloader.git
cd YoutubeDownloader
```

### 2️⃣ Create a Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing, manually install:

```bash
pip install pytubefix ffmpeg-python tqdm termcolor
```

### 4️⃣ Install FFmpeg

**Installation:**

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent for your distro

**Verification:** Run `ffmpeg -version` in your terminal. If it returns version information, FFmpeg is correctly installed and accessible.

---

## 🚀 Examples

### 🔹 Getting Started

```python
from src.downloader import YoutubeDownloader

app = YoutubeDownloader(
    video_dir_path="./downloads/videos",
    audio_dir_path="./downloads/audio",
    merged_dir_path="./downloads/merged"
)

urls = app.get_urls('''
https://www.youtube.com/watch?v=example_video_id_1
https://www.youtube.com/playlist?list=example_playlist_id
''')

app.build_queue(urls)
app.download()
# Optional: app.merge_all_videos() if needed for leftover files
```

### 🔹 Using a Text File of URLs

```python
from src.downloader import YoutubeDownloader

app = YoutubeDownloader(
    video_dir_path="./downloads/videos",
    audio_dir_path="./downloads/audio",
    merged_dir_path="./downloads/merged"
)

urls = app.get_urls_from_textFile("urls.txt")
app.build_queue(urls)
app.download()
```

📄 `urls.txt` example:

```text
https://www.youtube.com/watch?v=abcd1234
# This is a comment and will be ignored
https://www.youtube.com/playlist?list=PLexample123
```

### 🔹 Using the Download Queue

The downloader uses a persistent queue. When you call `app.build_queue(urls)`, it will prompt you if the queue is not empty:

- **Clear it and start fresh (c)**: Discards the current queue and starts a new one based on the provided URLs.
- **Add new URLs to existing queue (a)**: Adds the new URLs to the current queue.
- **Edit existing resolutions (e)**: Allows you to interactively change the resolution of videos already in the queue before downloading.

This allows for better management of multiple downloads and fine-tuning before execution.

### 🚀 Using in Google Colab

Before running the downloader in Google Colab, it's crucial to **mount your Google Drive**. Colab's runtime environment is temporary, meaning any files downloaded directly to the Colab instance (like `/content/downloads/videos` or `/content/downloads/audios`) will be **deleted** when the runtime disconnects or restarts. By mounting your Google Drive, you can save the final merged video files directly to your Drive, ensuring they persist.

1.  **Mount Google Drive:** Run the following code in a cell and follow the authorization steps.
    ```python
    from google.colab import drive
    drive.mount('/content/drive')
    ```

2.  **Configure and Run the Downloader:** Use the example code below. Ensure the `merged_dir_path` points to a folder within your mounted Drive (e.g., `/content/drive/MyDrive/YourFolder`). Files saved here will persist. Intermediate files (video-only, audio-only) can be saved to the local Colab storage (`/content/downloads/...`) if needed for the merge process.

    ```python
    from youtube_downloader.src.downloader import YoutubeDownloader
    from tqdm.notebook import tqdm
    from os.path import join

    # Define the base directory in Colab environment for temporary files
    BASE_DIR = '/content/downloads/'

    # Configure the downloader
    # Example: Save temporary video/audio locally, merged file to Drive
    app = YoutubeDownloader(
        video_dir_path=join(BASE_DIR, 'videos'),       # Local Colab storage (might be deleted)
        audio_dir_path=join(BASE_DIR, 'audios'),       # Local Colab storage (might be deleted)
        merged_dir_path=join('/content/drive/MyDrive/', 'YT_Downloads') # Persistent storage in Drive
    )

    # Example: Define your URLs (replace with actual YouTube links)
    # You can also use app.get_urls_from_textFile() if you have a file in Colab or Drive.
    urls = app.get_urls("""
    https://www.youtube.com/watch?v=example_video_id
    # https://www.youtube.com/playlist?list=example_playlist_id # Uncomment and add a real link if needed
    """)

    # Build the download queue
    app.build_queue(urls)

    # Start the download process
    app.download()

    # Optional: Merge any remaining separate video/audio files if necessary
    # This step is crucial if the download process was interrupted or if files were added separately.
    # app.merge_all_videos()

    print("Download process completed! Check your Google Drive for merged files.")
    ```

    For a detailed, ready-to-use notebook example, see the guide: [`youtube_downloader_colab_guide.ipynb`](youtube_downloader_colab_guide.ipynb).

---

## 🤝 Contributing

Contributions are welcome! 🎉
1. Fork the repo 🍴
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to your fork and submit a PR 🔥

---

## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.