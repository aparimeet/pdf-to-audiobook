import os
import subprocess

def create_file_for_ffmpeg(audio_path):
    if not os.path.isdir("audio_files"):
        os.mkdir("audio_files")
    # Sort the files based on the numbers in their filename
    for file in os.listdir(audio_path):
        if not os.path.isdir(f"audio_files/{file}"):
            os.mkdir(f"audio_files/{file}")
        wavs = sorted(os.listdir(audio_path + "/" + file), key=lambda x: int(x.split(".")[0]))
    
        with open("audio_files"+"/"+file+"/files.txt", "w+") as f:
            for wav in wavs:
                f.write(f"file 'audio/{file}/{wav}'\n")

def combine_wavs(path):
    for file in os.listdir(path + "/audio_files"):
        section = path + "/audio_files" + "/" + file
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", section + "/" + "files.txt", "-c", "copy", section + "/" + "output.wav"])

def combine_combined_wavs(audio_path):
    with open("output.txt", "w+") as f:
        for file in os.listdir(audio_path):
            f.write(f"file 'audio_files/{file}/output.wav'\n")
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "output.txt", "-c", "copy", "audiobook.wav"])


if __name__ == "__main__":
    path = os.getcwd()
    print(f"{path = }")
    audio_path = path + "/audio"
    create_file_for_ffmpeg(audio_path)
    combine_wavs(path)
    #combine_combined_wavs(audio_path)
