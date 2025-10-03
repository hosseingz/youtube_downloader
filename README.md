# 🎬 YoutubeDownloader  

![version](https://img.shields.io/badge/version-1.0.0-blue.svg)  ![license](https://img.shields.io/badge/license-MIT-green.svg)  ![python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)  ![status](https://img.shields.io/badge/status-stable-brightgreen.svg)  

A **powerful, beginner-friendly, and interactive YouTube downloader** built with [pytubefix](https://pypi.org/project/pytubefix/) and `ffmpeg`.  
Download videos 🎥, extract audios 🎵, or merge them together seamlessly ✅.  

---

## 🌹 Requirements  

Before you begin, ensure you have the following installed:  

- 🐍 **Python**: `>=3.9`  
- 📦 **Dependencies**:  
  - [pytubefix](https://pypi.org/project/pytubefix/) (for YouTube handling)  
  - [tqdm](https://pypi.org/project/tqdm/) (progress bars)  
  - [termcolor](https://pypi.org/project/termcolor/) (colored terminal output)  
- 🎬 **FFmpeg**: required for merging video and audio streams  
  - [Download FFmpeg](https://ffmpeg.org/download.html) and ensure it's available in your system PATH  

✅ Supported OS: Linux, macOS, Windows  

---

## 🎯 Objectives  

The goal of **YoutubeDownloader** is to:  

- 🚀 Provide an **easy-to-use tool** for downloading YouTube videos and playlists.  
- 🎥 Allow users to **choose video resolutions** (with size details).  
- 🎵 Support both **progressive streams** (video+audio combined) and **separate streams** (video-only + audio).  
- 🔗 Handle both **single video links** and full **playlists**.  
- 🛠️ Automatically **merge audio + video** using `ffmpeg`.  
- 📝 Ignore comments (`# ...`) and empty lines when reading URLs from text files.  

### ✨ Features  

- ✅ Download **single videos** or **full playlists**  
- ✅ Interactive **resolution selection**  
- ✅ Download **audio-only streams**  
- ✅ Auto-create directories for videos, audios, and merged files  
- ✅ Intelligent skipping if file already exists  
- ✅ Automatic **merging** of separate audio/video tracks  
- ✅ Easy **batch download** via `.txt` file with URLs  

---

## ⚙️ Setup  

### 1️⃣ Clone the Repository  

```bash
git clone https://github.com/hosseingz/youtube_downloader.git
cd YoutubeDownloader
````

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
pip install pytubefix tqdm termcolor
```

### 4️⃣ Install FFmpeg

Make sure `ffmpeg` is installed and available in your system path:

```bash
ffmpeg -version
```

If this shows version info → ✅ you're good to go.

---

## 🚀 Examples

### 🔹 Getting Started

Here’s the quickest way to start downloading:

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

app.download(urls)
app.merge_all_videos()
```

### 🔹 Example Walkthrough

1. Paste your URLs in `urls` (supports videos + playlists).
2. When prompted, **choose a resolution** for each video.
3. If the video is **progressive**, it saves directly in `merged/`.
4. If not, it downloads video-only + audio, then later merges them.

### 🔹 Using a Text File of URLs

```python
urls = app.get_urls_from_textFile("urls.txt")
app.download(urls)
app.merge_all_videos()
```

📄 `urls.txt` example:

```text
https://www.youtube.com/watch?v=abcd1234
# This is a comment and will be ignored
https://www.youtube.com/playlist?list=PLexample123
```

---
### 🚀 Using in Google Colab

You can run this YouTube Downloader directly in a Google Colab notebook. This is especially useful for downloading larger files without worrying about local storage limits or internet connection stability during the download process.

1.  **Open a new Colab notebook.**
2.  **Run the following commands in separate cells to set up the environment:**


    **Clone the Repository:**

    ```bash
    !git clone https://github.com/hosseingz/youtube_downloader.git
    ```
    *(This command downloads the project code into your Colab environment.)*
    
    **Install Dependencies:**

    ```bash
    !pip install -r youtube_downloader/requirements.txt
    ```

3.  **Connect to Google Drive (Optional but Recommended):**

    To save your downloaded files directly to your Google Drive, first mount your Drive. Add and run this code in a cell:

    ```python
    from google.colab import drive
    drive.mount('/content/drive')
    ```
    *(Follow the instructions to authorize Colab to access your Drive.)*

4.  **Configure and Run the Downloader:**

    Create a new cell and configure the `YoutubeDownloader` instance. You can point the `merged_dir_path` (or other paths) to your Drive folder to save files there automatically.

    ```python
    from youtube_downloader.src.downloader import YoutubeDownloader
    from os.path import join

    # Define the base directory in Colab environment
    BASE_DIR = '/content/downloads/'

    # Configure the downloader
    # Example: Save videos and audio locally in Colab, merged files to Drive
    app = YoutubeDownloader(
        video_dir_path=join(BASE_DIR, 'videos'),       # Local Colab storage
        audio_dir_path=join(BASE_DIR, 'audios'),       # Local Colab storage
        merged_dir_path=join('/content/drive/MyDrive/', 'YT_Downloads') # Saves merged files to Drive
    )

    # Example: Define your URLs (replace with actual YouTube links)
    # You can also use app.get_urls_from_textFile() if you have a file in Colab or Drive.
    urls = app.get_urls("""
    https://www.youtube.com/watch?v=example_video_id
    # https://www.youtube.com/playlist?list=example_playlist_id # Uncomment and add a real playlist link if needed
    """)

    # Start the download process
    app.download(urls)

    # Merge audio and video files if necessary
    app.merge_all_videos()

    print("Download and merge process completed!")
    ```
    *(This code configures the downloader to use Colab's temporary storage for intermediate files and saves the final merged file to your specified Drive folder. Adjust paths as needed.)*

    **Important:** Files saved in the Colab environment's temporary storage (`/content/downloads/videos`, `/content/downloads/audios`) will be **deleted** when the Colab runtime disconnects. Files saved in your mounted Google Drive (`/content/drive/MyDrive/YT_Downloads` in the example) will persist. The `merge_all_videos` step is crucial to combine the temporary parts into the final file before the runtime ends.

---


## 🤝 Contributing

Contributions are welcome! 🎉
To contribute:

1. Fork the repo 🍴
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to your fork and submit a PR 🔥

---

## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.