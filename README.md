# Local AI Sitcom Engine
A 100% local AI sitcom like "ai_sponge" that uses Ooba and RVC as a backend, and Unity as a frontend. The goal of this was simplicity and also many similar projects rely on online APIs which can get pricy, and also has risks when using their APIs for something like this. It's designed to mimmick popular livestreams like sponge_ai but completely decentralized and local. It comes with costs like being extremely GPU consuming and also in betweeen scenes there is a large delay.

## How it works from a bird's eye view:

1) We start by using the Oobabooga WebUI api [See here](https://github.com/oobabooga/text-generation-webui) to generate a rough script, vaguely like a movie script, the LLM puppeters the whole story instead of instead of instancing the LLM per character, this is essentially how other implimentations do it, but with an online API
2) We then parse the data into per character lines, occasionally this fails and generates no lines, but in my testing it's fairly reliable. Each character gets assigned their own sorted lines and extra junk like content in [] or () gets removed through ReGex. It is designed around 2 characters for GPU reasons, but more than 2 characters is theoretically possible with some changes
3) After that we use a single TTS voice, either using [Bark](https://github.com/suno-ai/bark) or your system's TTS for both characters
4) The outputted TTS lines are converted using RVC (you must provide your own models) which quickly converts everything to sound more like the characters, it isn't 100% and the TTS is the most lacking thing in this project, but it's the price to pay for speed, as the GPU budget is tight
5) A Unity project receives the files into a streaming data folder it can read at runtime, then sorts the audio correctly in index order and plays them with moving characters and some optional Unity tools, giving the illusion of 2 characters from a show talking with random output, after that Unity sends a dummy file to Python telling the engine to regenerate, go back to step 1

The system isn't prefect, there are some failed generations, which if it happens it will try to regenerate so the loop doesn't break. It also is very slow. This also is not a drag and drop solution, a lot of it is DIY and per project. I just hope these tools will help someone with their toy project without relying on paid internet APIs

# ⚠️ DISCLAIMER ⚠️
Use these tools **responsibly**. There is an ethical debate to voice cloning especially when unregulated and local like this. I am also not responsible for sharing material made by this online through livestreams, videos, pictures, etc. and am not responsible for any platform bans. This project is for entertainment only.

# Setup Overview

Most functions in the code are well defined and documented and you can read it in plain English, so you will be able to swap values out based on your needs. It's preconfigured for an ai_sponge type sitcom (but doesn't provide all the pieces) but is easy to replace for another two characters from another show.

Also  **HIGHLY** recommend using Miniconda/Anaconda, the RVC package sometimes fails on base installs and venvs, I've only gotten it to work on Miniconda. Use on base Python as your own risk.

**Three things I cannot provide:**
1) 3D models, music, assets to copyrighted materials
2) In the code there are references to optional mp4 videos for transitions, you will have provide those yourself if you want them
3) RVC voice models for characters, these are easily found on sites like Huggingface, you will just have to look around

**Install Steps:**
1) Install Oobabooga WebUI, set up an LLM (tested with: https://huggingface.co/TheBloke/Kunoichi-7B-GGUF), and then set up Ooba's API (outside of the conda environment)
2) Start the WebUI and enable the API any time you want to launch this (outside of the conda environment)
3) Clone this repo
4) Create a conda environment: `conda create -n ai_sitcom_engine`
5) Activate the conda environment (and whenever you want to run the Python engine) `conda activate ai_sitcom_engine` 
6) Grab `requirements.txt` and run `pip install -r requirements.txt` while activated
7) Check `main.py` and replace every value in your use case, and *read through it*. There's not that much code
8) Add your RVC models and assign them in their respective areas
9) Create a new Unity Game Engine project, make sure it is in an easily writable folder that won't cause permission errors
10) Create your desired scene you want your characters to roam around in
11) Add your characters
12) (Optional if using wander AI) Bake NavMesh on the scene, and add` NavMesh Agent` components to your characters
13) Add the `.cs` files to your assets and *read through it*. Adjust values and comment code as desired
14) Create any needed scene data like audio sources, or text
15) In your assets folder create an empty folder called `StreamingAssets` and inside of it create an empty folder called `Audio`
16) Verify all paths in Unity and Python are correct
17) Test and change as needed

If configured correctly you can enable the conda environment and run `python main.py` then run the Unity scene in editor and the two projects should communicate

### Enjoy your entirely local AI sitcom (responsibly)!
