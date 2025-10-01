# Example usage of the YoutubeDownloader class
# This script demonstrates how to use the downloader with various options

from src.downloader import YoutubeDownloader

# Initialize the downloader with directory paths
# video_dir_path: where video-only files will be stored
# audio_dir_path: where audio-only files will be stored  
# merged_dir_path: where final merged video+audio files will be stored
app = YoutubeDownloader(
    video_dir_path="./downloads/videos",
    audio_dir_path="./downloads/audio", 
    merged_dir_path="./downloads/merged"
)

# Define the URLs to download - can include both individual videos and playlists
# Lines starting with # will be ignored, empty lines are also ignored
urls = app.get_urls('''
https://www.youtube.com/watch?v=example_video_id_1
https://www.youtube.com/watch?v=example_video_id_2
https://www.youtube.com/playlist?list=example_playlist_id
# This is a comment and will be ignored
https://www.youtube.com/watch?v=example_video_id_3
''')

# Start the download process
# For each video, you'll be prompted to select a resolution
# Progressive streams (video+audio) will be downloaded directly to merged folder
# Non-progressive streams (video-only) will be downloaded separately with audio, then merged later
app.download(urls)

# After all downloads are complete, merge any separate video and audio files
# This step combines video-only files with their corresponding audio files
app.merge_all_videos()

print("Download and merge process completed!")