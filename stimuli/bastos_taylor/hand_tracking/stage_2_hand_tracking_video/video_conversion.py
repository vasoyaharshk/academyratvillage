
import os
import subprocess

def extract_video_segment(input_path, start_time, end_time, output_path, width=1280, height=1024):
    """Extracts a segment from a video, converts resolution, removes audio, and optimizes for H.264."""
    # ffmpeg_cmd = [
    #     "ffmpeg", "-i", input_path, "-ss", str(start_time), "-to", str(end_time), "-vf",
    #     f"scale={width}:{height}", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an", output_path, "-y"
    # ]
    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path, "-ss", str(start_time), "-to", str(end_time),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an", output_path, "-y"
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Extracted and converted segment saved at: {output_path}")

# Process all videos in the current directory
current_directory = os.getcwd()
video_extensions = (".mp4", ".avi", ".mov", ".mkv")

for filename in os.listdir(current_directory):
    if filename.lower().endswith(video_extensions):
        input_video_path = os.path.join(current_directory, filename)

        # Define output filenames for each segment
        output_hands_open = os.path.join(current_directory, "hands_open.mp4")
        output_hands_close = os.path.join(current_directory, "hands_close.mp4")
        output_correct = os.path.join(current_directory, "correct.mp4")
        output_incorrect = os.path.join(current_directory, "incorrect.mp4")

        # Extract and convert each segment before renaming
        extract_video_segment(input_video_path, 11, 13, output_hands_open)
        extract_video_segment(input_video_path, 13, 14, output_hands_close)
        extract_video_segment(input_video_path, 14, 16, output_correct)
        extract_video_segment(input_video_path, 16, 18, output_incorrect)

        # Rename the original file if it exists and hasn't been renamed yet
        original_path = input_video_path.replace(".", "_original.", 1)
        if os.path.exists(input_video_path) and not os.path.exists(original_path):
            os.rename(input_video_path, original_path)
            print(f"Renamed original file to: {original_path}")

print("All video segments have been extracted and converted.")
