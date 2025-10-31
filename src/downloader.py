from pytubefix import YouTube, Playlist
from termcolor import colored
from tqdm import tqdm
import subprocess
import threading
import os
import re

from pytubefix.exceptions import PytubeFixError, VideoUnavailable, RegexMatchError
from urllib.error import URLError


class YoutubeDownloader:
    def __init__(self, video_dir_path: str, audio_dir_path: str, merged_dir_path: str):
        self.video_dir_path = video_dir_path
        self.audio_dir_path = audio_dir_path
        self.merged_dir_path = merged_dir_path

        self.pbar = None

        for path in [self.video_dir_path, self.audio_dir_path, self.merged_dir_path]:
            os.makedirs(path, exist_ok=True)

    def get_urls(self, urls: str):
        urls = [line.strip() for line in urls.split('\n') if line.strip() and not line.startswith('#')]

        results = []
        for url in urls:
            if 'playlist' in url:
                results.extend(self.get_playlist_urls(url))
            else:
                results.append(url)
        return results

    def get_playlist_urls(self, playlist_url: str) -> list:
        try:
            playlist = Playlist(playlist_url)
            return playlist.video_urls
        except Exception as e:
            print(colored(f"Error fetching playlist {playlist_url}: {e}", "red"))
            return []

    def get_urls_from_textFile(self, path: str):
        with open(path, 'r') as file:
            urls = file.read()

        return self.get_urls(urls)

    def get_videos(self):
        return [f for f in os.listdir(self.video_dir_path) if f.endswith('.mp4')]

    def on_progress(self, stream, chunk, bytes_remaining):
        if self.pbar:
            current = stream.filesize - bytes_remaining
            self.pbar.update(current - self.pbar.n)


    def choose_resolution(self, yt_obj: YouTube):
        try:
            streams = yt_obj.streams.filter(file_extension='mp4').order_by('resolution').desc()

            options = []
            for stream in streams:
                res = stream.resolution
                if not res:
                    continue
                filesize = stream.filesize
                kind = "progressive" if stream.is_progressive else "video-only"
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


    def build_queue(self, urls: list[str]) -> list[dict]:
        download_queue = []

        for url in urls:
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

                download_queue.append({
                    "yt": yt_obj,
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

        return download_queue


    def download(self, urls: list[str]):
        task_queue = self.build_queue(urls)

        for task in task_queue:
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
                    if not os.path.exists(task["video_path"]):
                        print(f'{colored("Downloading video (no audio):", "cyan")} {filename}')
                        self.pbar = tqdm(total=stream.filesize, unit='B', unit_scale=True, desc='Video')
                        stream.download(output_path=self.video_dir_path, filename=f'{filename}.mp4')
                        self.pbar.close()

                    if not os.path.exists(task["audio_path"]):
                        audio_stream = yt_obj.streams.get_audio_only()
                        print(f'{colored("Downloading audio:", "cyan")} {filename}')
                        self.pbar = tqdm(total=audio_stream.filesize, unit='B', unit_scale=True, desc='Audio')
                        audio_stream.download(output_path=self.audio_dir_path, filename=f'{filename}.m4a')
                        self.pbar.close()

                    print(f'{filename} {colored("ready for merge later ✓", "yellow")}\n')

            except Exception as e:
                print(f'{yt_obj.watch_url} / {colored("error", "red")} => {e}')


    def combine(self, video_path: str, audio_path: str, output_path: str):
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]

        subprocess.run(command)

    def merge_all_videos(self):
        for video in self.get_videos():
            output_path = os.path.join(self.merged_dir_path, video)

            if not os.path.exists(output_path):
                merge_thread = threading.Thread(target=self.combine,
                            args=(
                                os.path.join(self.video_dir_path, video),
                                os.path.join(self.audio_dir_path, video.replace('.mp4', '.m4a')),
                                output_path
                            )
                            )

                merge_thread.start()

                print(f'{video} {colored("Merging...", "cyan")}')

        print(colored("\nAll merges completed ✓", "green"))