import os
import subprocess

def create_file_for_ffmpeg(root_path, section_path):
    # Sort the files based on the numbers in their filename
    files = sorted(os.listdir(path + "/Prologue"), key=lambda x: int(x.split(".")[0]))
    print(files)

    with open(section_path+"/files.txt", "a") as f:
        for file in files:
            f.write(f"file '{file}'\n")

def combine_wavs(filename, file_path):
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", section_path + "/" + filename, "-c", "copy", section_path + "/" + "output.wav"])

if __name__ == "__main__":
    path = os.getcwd()
    print(f"{path = }")
    section_path = path + "/Prologue"
    create_file_for_ffmpeg(path, section_path)
    combine_wavs("files.txt", section_path)
