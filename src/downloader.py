from pytubefix import YouTube, Playlist
from termcolor import colored
from tqdm import tqdm
import subprocess
import ffmpeg
import os
import re

from pytubefix.exceptions import PytubeFixError, VideoUnavailable, RegexMatchError
from urllib.error import URLError


class YoutubeDownloader:
    def __init__(self, video_dir_path:str, audio_dir_path:str, merged_dir_path:str):
        self.video_dir_path = video_dir_path
        self.audio_dir_path = audio_dir_path
        self.merged_dir_path = merged_dir_path

        self.pbar = None
        self.download_queue = []

        for path in [self.video_dir_path, self.audio_dir_path, self.merged_dir_path]:
            os.makedirs(path, exist_ok=True)

    def get_urls(self, urls:str):
        """Parses a string of URLs, ignoring empty lines and comments starting with #."""
        urls = [line.strip() for line in urls.split('\n') if line.strip() and not line.startswith('#')]
        results = []
        for url in urls:
            if 'playlist' in url:
                results.extend(self.get_playlist_urls(url))
            else:
                results.append(url)
        return results

    def get_playlist_urls(self, playlist_url:str) -> list:
        """Fetches all video URLs from a given playlist URL."""
        try:
            playlist = Playlist(playlist_url)
            return playlist.video_urls
        except Exception as e:
            print(colored(f"Error fetching playlist {playlist_url}: {e}", "red"))
            return []

    def get_urls_from_textFile(self, path:str):
        """Reads URLs from a text file and returns a list."""
        with open(path, 'r') as file:
            urls = file.read()
        return self.get_urls(urls)

    def get_videos(self):
        """Gets a list of video files in the video directory."""
        return [f for f in os.listdir(self.video_dir_path) if f.endswith('.mp4')]

    def on_progress(self, stream, chunk, bytes_remaining):
        """Callback for tqdm progress bar during download."""
        if self.pbar:
            current = stream.filesize - bytes_remaining
            self.pbar.update(current - self.pbar.n)

    def choose_resolution(self, yt_obj:YouTube):
        """Displays available resolutions and lets the user choose one."""
        try:
            streams = yt_obj.streams.filter(file_extension='mp4').order_by('resolution').desc()

            options = []
            for stream in streams:
                res = stream.resolution
                if not res:
                    continue
                filesize = stream.filesize
                kind = "progressive" if stream.is_progressive else "video-only"
                # Avoid adding duplicate resolution/kind combinations
                if (res, kind) not in [(s["res"], s["kind"]) for s in options]:
                    options.append({"res": res, "kind": kind, "stream": stream})
                    print(f"{len(options)}) {res} ({kind}) (~{filesize / (1024*1024):.2f} MB)")

            if not options:
                print(colored("No valid resolutions found.", "red"))
                return None

            try:
                choice = int(input("Choose resolution (number): "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]["stream"]
                else:
                    print(colored("Invalid choice.", "red"))
                    return None
            except ValueError:
                print(colored("Invalid input.", "red"))
                return None
        except Exception as e:
            print(colored(f"Error choosing resolution: {e}", "red"))
            return None

    def edit_queue_resolutions(self):
        """Allows the user to edit the resolution of items in the current download queue."""
        if not self.download_queue:
            print(colored("Download queue is empty. Nothing to edit.", "yellow"))
            return

        print(colored("\nCurrent Download Queue:", "cyan"))
        for i, item in enumerate(self.download_queue):
            progressive_status = "Progressive" if item["is_progressive"] else "Separated"
            print(f"{i + 1}) {item['filename']} - Resolution: {item['stream'].resolution} ({progressive_status})")

        while True:
            try:
                index_input = input("\nEnter the number of the video you want to change the resolution for (or 'q' to quit): ")
                if index_input.lower() == 'q':
                    break
                index = int(index_input) - 1
                if 0 <= index < len(self.download_queue):
                    current_item = self.download_queue[index]
                    print(f"\n{colored('Available resolutions for:', 'yellow')} {current_item['filename']}")
                    # Reload the YouTube object for this specific video URL
                    yt_obj = YouTube(current_item['yt'].watch_url, on_progress_callback=self.on_progress)
                    new_stream = self.choose_resolution(yt_obj)
                    if new_stream:
                        # Update the queue item with the new stream and its properties
                        self.download_queue[index]["stream"] = new_stream
                        self.download_queue[index]["is_progressive"] = new_stream.is_progressive
                        print(colored(f"Resolution updated for '{current_item['filename']}' to {new_stream.resolution}.", "green"))
                    else:
                        print(colored(f"Resolution was not changed for '{current_item['filename']}'.", "yellow"))
                else:
                    print(colored("Invalid number.", "red"))
            except ValueError:
                print(colored("Invalid input. Please enter a number or 'q'.", "red"))

    def _extract_video_id(self, url: str) -> str | None:
        """
        Extracts the video ID from a YouTube URL using regex.
        Handles various URL formats like youtu.be, watch?v=, embed, v=, etc.
        Returns the ID if found and valid, otherwise None.
        """
        # Regex pattern to match YouTube video IDs from various URL formats
        pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:embed|v|watch\?.*v=|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Optional: Re-validate the extracted ID (though regex already checks length and chars)
            if len(video_id) == 11 and re.fullmatch(r'[a-zA-Z0-9_-]{11}', video_id):
                return video_id
        return None

    def build_queue(self, urls:list[str]) -> list[dict]:
        """
        Builds the download queue based on URLs.
        If the queue is empty, it creates a new one.
        If the queue is not empty, it asks the user whether to clear it, add to it, or edit existing resolutions.
        """
        if self.download_queue:
            print(colored("Download queue already exists.", "yellow"))
            print(f"Current queue has {len(self.download_queue)} items.")
            choice = input("Queue is not empty. Clear it and start fresh (c),\nAdd new URLs to existing queue (a),\nor Edit existing resolutions (e)?\n(c/a/e): ").lower()

            if choice == 'c':
                print("Clearing existing queue...")
                self.download_queue = []
            elif choice == 'e':
                self.edit_queue_resolutions()
                return self.download_queue  # Return after editing, don't process new URLs
            elif choice == 'a':
                # Only add new URLs, do not re-prompt for existing ones
                pass # Continue to add new URLs
            else:
                print("Invalid choice. Cancelling build_queue.")
                return self.download_queue  # Return existing queue if invalid input

        # Remove duplicate URLs from the input list before processing
        # Also remove any URLs that are already in the current queue
        processed_video_ids = {item['id'] for item in self.download_queue} # Start with existing URLs
        unique_urls = []
        for url in urls:
            video_id = self._extract_video_id(url)
            if video_id and video_id not in processed_video_ids:
                processed_video_ids.add(video_id)
                unique_urls.append(url)

        # If no new unique URLs are provided after deduplication, exit
        if not unique_urls:
            if self.download_queue:
                print(colored("No new unique URLs provided to add to the existing queue.", "yellow"))
            else:
                # This case means the initial call had no valid new URLs
                print(colored("No valid URLs provided for a new queue.", "yellow"))
            
            return self.download_queue


        # Process only the new unique URLs
        for url in unique_urls:
            try:
                yt_obj = YouTube(url, on_progress_callback=self.on_progress)
                title = yt_obj.title
                filename = re.sub(r'[\\/*?:"<>|]', "_", title)

                print(f"\n{colored('Available resolutions for:', 'yellow')} {filename}")
                chosen_stream = self.choose_resolution(yt_obj)

                if not chosen_stream:
                    print(colored("Skipping video due to invalid resolution choice.", "red"))
                    continue

                video_path = os.path.join(self.video_dir_path, f'{filename}.mp4')
                audio_path = os.path.join(self.audio_dir_path, f'{filename}.m4a')
                merged_path = os.path.join(self.merged_dir_path, f'{filename}.mp4')

                # Add the new item to the queue
                self.download_queue.append({
                    "yt": yt_obj,
                    "id": self._extract_video_id(url),
                    "filename": filename,
                    "video_path": video_path,
                    "audio_path": audio_path,
                    "merged_path": merged_path,
                    "stream": chosen_stream,
                    "is_progressive": chosen_stream.is_progressive
                })

            except (URLError, PytubeFixError, VideoUnavailable, RegexMatchError, AttributeError) as e:
                print(colored(f"Error processing URL {url}: {e}", "red"))
                continue
            except Exception as e:
                print(colored(f"Unexpected error for URL {url}: {e}", "red"))
                continue

        return self.download_queue

    def download(self):
        """
        Downloads all items in the *current* download queue.
        This method only downloads. It does not modify the queue itself.
        It also merges video and audio files if they were downloaded separately.
        """
        if not self.download_queue:
            print(colored("Download queue is empty. Nothing to download.", "yellow"))
            return

        print(colored(f"\nStarting download for {len(self.download_queue)} items in the queue...", "green"))

        for task in self.download_queue:
            yt_obj = task["yt"]
            filename = task["filename"]
            stream = task["stream"]

            try:
                if task["is_progressive"]:
                    if not os.path.exists(task["merged_path"]):
                        print(f'{colored("Downloading progressive video+audio:", "cyan")} {filename}')
                        self.pbar = tqdm(total=stream.filesize, unit='B', unit_scale=True, desc='Video+Audio')
                        stream.download(output_path=self.merged_dir_path, filename=f'{filename}.mp4')
                        self.pbar.close()
                        print(f'{filename} {colored("downloaded ✓", "green")}\n')
                    else:
                        print(f'{filename} already exists in merged folder.')
                else:
                    needs_merge = False
                    video_downloaded = False
                    audio_downloaded = False

                    # Download video if it doesn't exist
                    if not os.path.exists(task["video_path"]):
                        print(f'{colored("Downloading video (no audio):", "cyan")} {filename}')
                        self.pbar = tqdm(total=stream.filesize, unit='B', unit_scale=True, desc='Video')
                        stream.download(output_path=self.video_dir_path, filename=f'{filename}.mp4')
                        self.pbar.close()
                        video_downloaded = True
                        needs_merge = True
                    else:
                        print(f'{filename} video already exists in video folder.')

                    # Download audio if it doesn't exist
                    if not os.path.exists(task["audio_path"]):
                        audio_stream = yt_obj.streams.get_audio_only()
                        if not audio_stream:
                             print(colored(f"Could not get audio stream for {filename}. Skipping.", "red"))
                             continue
                        print(f'{colored("Downloading audio:", "cyan")} {filename}')
                        self.pbar = tqdm(total=audio_stream.filesize, unit='B', unit_scale=True, desc='Audio')
                        audio_stream.download(output_path=self.audio_dir_path, filename=f'{filename}.m4a')
                        self.pbar.close()
                        audio_downloaded = True
                        needs_merge = True
                    else:
                        print(f'{filename} audio already exists in audio folder.')

                    # Merge if necessary
                    if needs_merge:
                        if not os.path.exists(task["merged_path"]):
                            print(f'{colored("Merging video and audio for:", "yellow")} {filename}')
                            self.combine(task["video_path"], task["audio_path"], task["merged_path"])
                            print(f'{filename} {colored("merged ✓", "green")}\n')
                        else:
                            print(f'{filename} already exists in merged folder.')
                    elif video_downloaded or audio_downloaded:
                         print(f'{filename} files already existed, no merge needed.')
                    else:
                        print(f'{filename} files already existed, no download or merge needed.')

            except Exception as e:
                print(f'{yt_obj.watch_url} / {colored("error", "red")} => {e}')

    def combine(self, video_path:str, audio_path:str, output_path:str):
        """Combines a video file and an audio file using ffmpeg."""
        try:
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_path)

            stream = ffmpeg.output(input_video, input_audio, output_path, vcodec='copy', acodec='aac')
            command = ffmpeg.compile(stream)

            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(colored(f"FFmpeg error during merge for {video_path} and {audio_path}: {e}", "red"))
        except Exception as e:
            print(colored(f"Unexpected error during merge for {video_path} and {audio_path}: {e}", "red"))

    def merge_all_videos(self):
        """
        Starts the merging process for all video/audio pairs that exist in the directories
        but do not have a corresponding merged file yet.
        """
        # Find all video files in the video directory
        for video_filename in self.get_videos():
            video_path = os.path.join(self.video_dir_path, video_filename)
            audio_filename = video_filename.replace('.mp4', '.m4a')
            audio_path = os.path.join(self.audio_dir_path, audio_filename)
            output_path = os.path.join(self.merged_dir_path, video_filename)

            # Check if corresponding audio exists and merged file does not
            if os.path.exists(audio_path) and not os.path.exists(output_path):
                print(f'{colored("Merging:", "yellow")} {video_filename} and {audio_filename}')
                self.combine(video_path, audio_path, output_path)
                print(f'{video_filename} {colored("merged ✓", "green")}')
            elif not os.path.exists(audio_path):
                print(f'{colored("Missing audio file for:", "red")} {video_filename}')
            # If merged file already exists, skip

        print(colored("\nAll possible merges completed.", "green"))
