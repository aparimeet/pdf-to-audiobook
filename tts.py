from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import os
from constants import AUDIO_CHUNKS_FOLDER_NAME, PARSED_TEXT_FOLDER_NAME

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
pipeline = KPipeline(lang_code='a') # <= make sure lang_code matches voice, reference above.

curr_dir = os.getcwd()
files = os.listdir(curr_dir + f"/{PARSED_TEXT_FOLDER_NAME}")
print(f"{files = }")
for file in files:
    filename_wo_extension = file.split(".")[0]
    print(f"Converting {file} to speech")
    with open(f"{curr_dir}/{PARSED_TEXT_FOLDER_NAME}/{file}", "r") as f:
        text = f.read()
    # Generate, display, and save audio files in a loop.
    generator = pipeline(
        text, voice='af_heart', # <= change voice here
        speed=1
    )

    os.makedirs(curr_dir + f"/{AUDIO_CHUNKS_FOLDER_NAME}/" + filename_wo_extension)
    for i, (gs, ps, audio) in enumerate(generator):
        print("\n")
        print(i)  # i => index
        print(gs) # gs => graphemes/text
        print(ps) # ps => phonemes
        display(Audio(data=audio, rate=24000, autoplay=i==0))
        sf.write(f'{curr_dir}/{AUDIO_CHUNKS_FOLDER_NAME}/{filename_wo_extension}/{i}.wav', audio, 24000) # save each audio file
        print("\n")
