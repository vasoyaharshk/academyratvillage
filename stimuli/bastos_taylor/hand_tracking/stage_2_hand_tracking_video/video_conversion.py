import os
import subprocess

def convert_video(input_path, output_path, width=1280, height=1024):
    """Converts video resolution, removes audio, and optimizes for H.264."""
    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path, "-vf",
        f"scale={width}:{height}", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an", output_path, "-y"
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Converted video saved at: {output_path}")
    
    # Rename the original file
    original_path = input_path.replace(".", "_original.", 1)
    os.rename(input_path, original_path)
    print(f"Renamed original file to: {original_path}")

# Process all videos in the current directory
current_directory = os.getcwd()
video_extensions = (".mp4", ".avi", ".mov", ".mkv")

for filename in os.listdir(current_directory):
    if filename.lower().endswith(video_extensions):
        input_video_path = os.path.join(current_directory, filename)
        output_video_path = os.path.join(current_directory, filename)  # Keep the same name for output
        convert_video(input_video_path, output_video_path)

print("All videos have been converted.")
