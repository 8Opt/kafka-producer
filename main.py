from pathlib import Path
import cv2
import numpy as np
from kafka import KafkaProducer

from pytubefix import YouTube
from pytubefix.cli import on_progress


def download_youtube_video(url: str, dest: str):
    yt = YouTube(url, on_progress_callback=on_progress)
    ys = yt.streams.get_highest_resolution()
    res = ys.download(output_path=dest)
    return res

def np_to_bytes(arr: np.ndarray):
    return arr.tobytes()


def process_video_source(video_name):
    match video_name:
        case str() if video_name.startswith("rtsp://"):
            print("Running rtsp video")
            return video_name
        case str() if video_name.startswith("http"):
            if "youtube" in video_name:
                print("Running youtube video")
                video_name = download_youtube_video(video_name, "./")
                return video_name
            else:
                print("Running http video")
                return video_name
        case _:
            print("Running local video")
            return video_name

def main(vido_name: str, 
         topic: str = "VIDEO_STREAM",
         bootstrap_servers: list[str] = ["localhost:9092"]):
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    video_name = process_video_source(vido_name)
    cap = cv2.VideoCapture(video_name)
    print(f"Publishing video {video_name} to topic: {topic}")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Encode frame as JPEG and convert to bytes
        ret2, buffer = cv2.imencode('.jpg', frame)
        if not ret2:
            continue
        frame_bytes = np_to_bytes(buffer)
        producer.send(topic=topic, value=frame_bytes)    
    cap.release()
    producer.close()


if __name__ == "__main__":
    video_name = "https://www.youtube.com/watch?v=WvhYuDvH17I"
    main(video_name)
