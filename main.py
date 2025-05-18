from pathlib import Path
import cv2
import numpy as np
from kafka import KafkaProducer

from .utils import download_youtube_video

def np_to_bytes(arr: np.ndarray):
    return arr.tobytes()


def filter_video_name(video_name: str): 
    if not video_name: 
        raise ValueError("Video name is required")

    match video_name: 
        case video_name.startswith("rtsp://"):
            print("Running rtsp video")
            return video_name
        case video_name.startswith("http"): 
            if "youtube" in video_name: 
                print("Running youtube video")
                download_youtube_video(video_name, "./")    # TODO: Can you another libraries for reading youtube video with openCV?
                return Path(video_name.split("/")[-1]).name
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
    video_name = filter_video_name(vido_name)
    cap = cv2.VideoCapture(video_name)
    
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
    video_name = ""
    main(video_name)
