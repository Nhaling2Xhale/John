# LordGPT
Autonomous AI Assistant fully capable of performing tasks on its own.
JOIN US ON DISCORD: https://discord.gg/mhGtn6fb

LordGPT is an automated AI Assistant that can accomplish a wide range of tasks.
- Tracks his tasks to ensure completion.
- Browse Internet and Research. (Playwright Needed pip install playwright | playwirght install)
- Read, write, append, delete, rename, move local files.
- Generate Python Scripts, and even write its own commands to further is capabilities.
- Search Engine (Google) - Home Depot, Walkmart, DuckDuckGo, ebay, applestore, yelp, yahoo and more coming soon!
- Generate html formatted PDF Reports
- Use more than one API at a time. Options to flip between Azure and OpenAI for each call, reducing timeouts, and helping Azure and OpenAI out by spreading out requests.

LordGPT is different from other AI agents. I designed it not with code, but with prompt engineering. The code is simple as you can tell. The prompts are formatted to perform the tasks, not code. Hundreds of hours were spent on these prompts, and the slightest change will throw him off, keep that in mind.

KNOWN ISSUES:
1. Windows Binary Crashes sometimes. Working on exception coding.

REQUIREMENTS:
- Google Search API for searching.
- Deep pockets for tokens.

WINDOWS BINARY:
Easiest way for windows users is to use the EXE. Built with pyinstaller. You can build yourself using pip install pyinstaller if you prefer.
API Key Instructions here: https://tinyurl.com/LordGPT-Instructions

MANUAL WINDOWS INSTALL
1. Enable WSL dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
2. Install WSL by running the following command: wsl --install
3. Follow the on-screen instructions to install your desired Linux distribution from the Microsoft Store.
4. Launch the Linux terminal by searching for your distribution or type WSL in the cmd prompt.

RUN THESE BASH COMMANDS, COPY AND PASTE
1. ls /home/USERNAME you choose during installation to see the files in your home directory.
2. Type sudo apt update && sudo apt upgrade && sudo apt install pip && sudo apt install wkhtmltopdf
3. type git clone GITURL
4. cd LordGPT
5. pip install -r requirements.txt - Sorry for the long requirements, its my dev machine.
6. playwright install
7. python3 LordGPT.py

MAC USERS
1. Open Terminal
2. /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
3. export PATH="/usr/local/opt/python/libexec/bin:$PATH"
4. brew install python
5. pip3 install -r requirements.txt
14. Now setup your .env

ENV Setup
- Rename .env_template to .env
- Fill in the required info

WINDOWS EXE INSTRUCTIONS 
The Windows Binary is a prepacked Python bundle using PyInstaller. It's built with the latest version and includes everything you need to access LordGPT. The bundle still requires that you have an OpenAI and Google Search key.

https://thelordg.com/downloads/LordGPT.exe  

OPENAI API: 
- Sign up for OpenAI;  https://platform.openai.com/account/api-keys 
- Once logged in, click your profile in the upper right. 
- Choose "API Keys." 
- Generate an API key and save it somewhere; you won't be able to see it again. 

SERPAPI SEARCH API: 
- Sign up https://serpapi.com/ 
- Get your API key and save it. 
- Free for 100 searches a month. Or come to our discord and I’ll give you a key for free. 
- Paste that into Notepad.

LAUNCH LORDGPT.EXE: 
- Double-click on LordGPT.exe. 
- The first time it loads it has to download the browsers. Give it time. 
- Paste the api keys when asked.
- Choose "GPT-3.5-Turbo" unless you have GPT-4. Note: You’ll get errors if you try GPT-4 without access. 

