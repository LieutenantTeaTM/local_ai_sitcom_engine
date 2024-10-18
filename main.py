## note: This is an AI sitcom companion engine for Unity
# All this does is generate audio and scripts 

# RVC Python imports
from rvc_python.infer import infer_file, infer_files

# Bark TTS (slow) imports
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav


# Faster TTS (uses system TTS)
import pyttsx3
engine = pyttsx3.init()

# OS Flags for Bark
import os, time
# For Better Performance, set both to true
os.environ["SUNO_OFFLOAD_CPU"] = "True"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

# Ooba imports
import requests
import random
import re

# False will use system TTS (faster), True uses bark for quality (Slower)
use_bark = False

# Set as you wish for system TTS, in my opinion it's a bit fast
tts_rate = 40
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - tts_rate)

# Replace with your Oobabooga API port
localhost = "http://127.0.0.1:5000"
url = f"{localhost}/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

if use_bark == True:
    # Preload the models
    print("Loading bark models...")
    preload_models()

# Path to your Unity streaming assets folder (may need to create it manually)
# Tip: If it throws an error about this path trying assigning a full path with \\ instead of \
STREAMING_ASSETS_PATH = os.path.join("Assets\\StreamingAssets\\")

while True:
    # Attempts to try the whole generation, if any error occurs it will abort the generation and try again
    try:
        # Choose a random topic
        # These are user assigned, the more the more varied it will be, be creative!
        topics = ["replace me with", "topics you want the characters to", "act"]
        
        # Chooses a random number that is 0 to the length of the topic list
        random_num = random.randint(0, len(topics) - 1)
        # Chooses a topic based on the random number and the topic list
        chosen_topic = topics[random_num]


        # Debug print to alert the user of the chosen topic
        print(f"Chosen topic: {chosen_topic}")
        
        # Init Prompt for Ooba
        # You may have to play around with this depending on your LLM and franchise you want to make
        # This shouldn't change once it works for you!
        script_prompt = f"Write me a dialogue only script involving a conversation between Patrick and Spongebob from the show \"Spongebob Squarepants\" about {chosen_topic}. Do not explain the script, do not ask questions, do not ask for feedback, you are the script of the show."
        # Add the script prompt to the message history
        history = [{"role": "user", "content": script_prompt}]

        # Params, can leave mostly the same depending on model
        data = {
                "mode": "instruct",
                # Should be somewhat small or the LLM might make really big generations
                # that can take a while to parse into text
                # Also the idea is to have small conversations between the characters, not lore dumps
                "max_tokens": 256,
                # We add the history here
                "messages": history
        }

        # Debug print to alert the user that we are now attempting to generate the script
        # Depending on your LLM and gpu this will take the longest
        print("generating script")
        # Gather response from Ooba (make sure the api flag is set in Ooba!!)
        response = requests.post(url, headers=headers, json=data, verify=False)
        message = response.json()['choices'][0]['message']['content']

        # Debug print the generation then splits the message into a list
        print(message.splitlines())
        message_lines = message.splitlines()

        # Dictionaries for both characters, key is the order in the convo, value is the line
        # This system is meant for 2-ish characters, will need refactoring on both Python and Unity C#
        # if you want more than 2, also GPU usage will get worse as more RVC models are needed (more wait time)
        sponge_lines = {}
        pat_lines = {}

        # Ordered lines are the lines sorted after parsing them into a script
        ordered_sponge_lines = {}
        ordered_pat_lines = {}


        # Initial dialogue order number for keeping track of who is talking when
        dialogue_order_num = 0
        for m in message_lines:
            # Regex to remove the garbage and nonsense between ** and () for TTS reasons, if it does exist
            # Note: Some models may not need this but it's recommended
            m = re.sub(r"[\(\\*-].*?[\n\*\)]", "", m)
            
            # Check to see if the line is either of the characters talking
            # Omits any that do not begin with "SPONGEBOB:" or "PATRICK:" (or whoever your characters are), should only account for the first word, mentions of the names should pass!
            # Replace 'spongebob" with your chosen character
            if m.split(' ', 1)[0].lower() == "spongebob:":
                # Create a new dialogue dictionary entry for the character with the order in the conversation + the line **after** the speaker name
                sponge_lines[dialogue_order_num] = m.split(' ', 1)[1]

                ordered_sponge_lines[dialogue_order_num] = m.split(' ', 1)[1]
                # Updates the dialogue number
                dialogue_order_num += 1
            # Again replace with your chosen second character
            elif m.split(' ', 1)[0].lower() == "patrick:":
                # Create a new dialogue dictionary entry for the character with the order in the conversation + the line **after** the speaker name
                pat_lines[dialogue_order_num] = m.split(' ', 1)[1]

                ordered_pat_lines[dialogue_order_num] = m.split(' ', 1)[1]
                # Updates the dialogue number
                dialogue_order_num += 1

        ## Debug prints
        print("SPONGE LINES:\n")
        print(sponge_lines)
        print("PAT LINES:\n")
        print(pat_lines)

        ## Remove old generations from other runs (kinda a hack but oh well)
        # Removes the directory then creates a new empty one
        # You can rename these as you wish
        import shutil
        shutil.rmtree('./sponge_output')
        os.mkdir('./sponge_output') 
        shutil.rmtree('./pat_output')
        os.mkdir('./pat_output') 
        shutil.rmtree('./sponge_rvc_out')
        os.mkdir('./sponge_rvc_out') 
        shutil.rmtree('./pat_rvc_out')
        os.mkdir('./pat_rvc_out')

        ## BARK TTS (slower but high quality) ##
        if use_bark == True:
            ## generate audio from text for Spongebob
            for convo_index, line in sponge_lines.items():
                audio_array = generate_audio(line)
                write_wav(f"./sponge_output/{convo_index}_sponge.wav", SAMPLE_RATE, audio_array)
            print("Sponge lines saved")

            ## generate audio from text for Patrick
            for convo_index, line in pat_lines.items():
                audio_array = generate_audio(line)
                write_wav(f"./pat_output/{convo_index}_patrick.wav", SAMPLE_RATE, audio_array)
            print("Patrick lines saved")

        ## System TTS  (faster but lower quality) ##
        # This makes the AI more or less monotone, be warned (but rvc helps a lot)
        if use_bark == False:
            for convo_index, line in sponge_lines.items():
                engine.save_to_file(line , f"./sponge_output/{convo_index}_sponge.wav")
                engine.runAndWait()
            print("Sponge lines saved")

            for convo_index, line in pat_lines.items():
                engine.save_to_file(line , f"./pat_output/{convo_index}_pat.wav")
                engine.runAndWait()
            print("Pat lines saved")

        ## RVC, for character voices, you have to supply your own RVC models

        # Alert the user we are converting character 1's TTS
        print("Interfering Sponge voice")
        results = infer_files(
            dir_path="./sponge_output",  # Directory containing input audio files
            paths=[],
            opt_dir="./sponge_rvc_out",  # Directory where output files will be saved
            model_path="./FDG_Spongebob.pth", # Change for your RVC model path
            index_path="",  # Optional according to docs but this slows it to a crawl for some reason!
            device="cuda:0", # Use cpu or cuda (please use CUDA for this if possible)
            f0method="rmvpe",  # Choose between 'harvest', 'crepe', 'rmvpe', 'pm'
            # Adjust as needed for pitch
            # Recommended for sponge_ai sponge Bark: -7
            # Recommended for sponge_ai sponge System TTS 7
            f0up_key=7,  # Transpose/Pitch setting, change as desired or to your model
            index_rate=0.5,
            filter_radius=3,
            resample_sr=0,  # Set to desired sample rate or 0 for no resampling.
            rms_mix_rate=0.25,
            protect=0.33,
            version="v2",
            out_format="wav"
        )
        print("Sponge files converted to RVC")

        print("Interfering Patrick voice")
        results = infer_files(
            dir_path="./pat_output",  # Directory containing input audio files
            paths=[],
            opt_dir="./pat_rvc_out",  # Directory where output files will be saved
            model_path="./patrickstarnab2.pth", # Change with your RVC model path
            index_path="",  # Optional according to docs but this slows it to a crawl for some reason!
            device="cuda:0", # Use cpu or cuda (please use CUDA for this if possible)
            f0method="rmvpe",  # Choose between 'harvest', 'crepe', 'rmvpe', 'pm'
            # Adjust as needed for pitch
            # Recommended for sponge_ai patrick Bark: -8
            # Recommended for sponge_ai patrick System TTS 8
            f0up_key=8,  # Transpose/Pitch setting, change as desired or to your model
            index_rate=0.5,
            filter_radius=3,
            resample_sr=0,  # Set to desired sample rate or 0 for no resampling.
            rms_mix_rate=0.25,
            protect=0.33,
            version="v2",
            out_format="wav"
        )
        print("Patrick files converted to RVC")

        print("Results saved. Script finished.")

        # Begin writing output to a script txt file that we will send to Unity
        # It's formatted like
        #
        # 0
        # this is your characters dialogue
        # 2
        # this is your characters dialogue
        # 1
        # this is your characters dialogue
        # It is formatted out of order but Unity will do some heavy lifting for us
        print("Writing to file")
        f = open("script.txt", "w")
        for l in ordered_sponge_lines:
            f.write(str(l))
            f.write("\n")
            f.write(str(ordered_sponge_lines[l]))
            f.write("\n")
        for l in ordered_pat_lines:
            f.write(str(l))
            f.write("\n")
            f.write(str(ordered_pat_lines[l]))
            f.write("\n")
        f.close()

        
        SPONGE_RVC_PATH = os.path.join("./sponge_rvc_out")  # Folder with audio files
        PAT_RVC_PATH = os.path.join("./pat_rvc_out")
        TEXT_SRC_PATH = os.path.join("script.txt")  # Path to the text file

        # The Unity StreamingAssets path with the name of the file
        text_dest_path = os.path.join(STREAMING_ASSETS_PATH, "lines.txt")

        """Move all audio files to StreamingAssets/Audio."""
        # Audio folder inside Unity StreamingAssets
        audio_dest_path = os.path.join(STREAMING_ASSETS_PATH, "Audio")

        # Check if StreamingAssets\lines.txt currently exists
        if os.path.isfile(text_dest_path):
            try:
                # If it does we remove it
                os.remove(text_dest_path)
            except OSError:
                # If it doesn't we don't care
                pass


        # We try to remove all files in the StreamingAssets Audio file
        for filename in os.listdir(audio_dest_path):
            file_path = os.path.join(audio_dest_path, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                # If we failed to delete we alert the user
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Start moving the new audio (RVC output)
        for filename in os.listdir(SPONGE_RVC_PATH):
            if filename.endswith(".wav"):
                src = os.path.join(SPONGE_RVC_PATH, filename)
                dest = os.path.join(audio_dest_path)
                shutil.move(src, dest)
                print(f"Moved {filename} to {audio_dest_path}")
        for filename in os.listdir(PAT_RVC_PATH):
            if filename.endswith(".wav"):
                src = os.path.join(PAT_RVC_PATH, filename)
                dest = os.path.join(audio_dest_path)
                shutil.move(src, dest)
                print(f"Moved {filename} to {audio_dest_path}")

        # Move the script to StreamingAssets
        shutil.move(TEXT_SRC_PATH, text_dest_path)
        print(f"Moved lines.txt to {text_dest_path}")


        # Path to our communication file between Unity and Python
        # "singal_done.txt" is just a dummy file Unity and Python check to see if Unity has finished playing the 'episode'
        SIGNAL_FILE = os.path.join(STREAMING_ASSETS_PATH, "signal_done.txt")
        print("Waiting for Unity to complete playback...")
        # Infinite loop while we wait for Unity to tell us it's done
        while not os.path.exists(SIGNAL_FILE):
            time.sleep(1)

        # Now we have received the okay from Unity, we just delete it, which will put Unity in a waiting state
        # More on that in Unity
        print("Playback complete. Signal received from Unity.")
        os.remove(SIGNAL_FILE)
    except:
        # If something fatal happened we alert the user and try again
        print("Output failed... trying again")
        pass
