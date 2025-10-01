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

---


