# region ### IMPORTS ###
import os
import sys
import re
import time
import random
import json
import subprocess
import datetime
import requests.exceptions
from time import sleep
from typing import Dict

from dotenv import load_dotenv
from termcolor import colored
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from unidecode import unidecode
import pdfkit
import requests

from scripts.bot_prompts import command_list, bot_prompt
from scripts.bot_commands import botcommands

load_dotenv(override=True)
current_path = os.getcwd()
working_folder = os.path.join(current_path, 'LordGPT_folder')
if not os.path.exists(working_folder):
    os.makedirs(working_folder)

# endregion
global api_key
global google_api_key
global google_search_id
global model
global debug_code
global api_count
global api_throttle
global api_retry
global api_timeout
# region ### GLOBAL FUNCTIONS ###
model = None
config_file = "config.json"
current_version = "1.1.1"
update_url = "https://thelordg.com/version.txt"
download_link = "https://github.com/Cytranics/LordGPT"
success = True
api_count = 0
api_type = None
message_history = []
debug_code = False



def debug_log(message):
    if debug_code:
        #print(message)

        # Create the debug.txt file path
        debug_file_path = os.path.join(working_folder, "debug.txt")

        # Write the message to the debug.txt file
        with open(debug_file_path, "a") as debug_file:
            debug_file.write(f"{message}\n")


def set_global_success(value):
    global success
    success = value


def check_for_updates():
    try:
        response = requests.get(update_url)
        response.raise_for_status()
        latest_version = response.text.strip()

        if latest_version != current_version:
            print(colored(
                f"A new version ({latest_version}) is available! Please visit {download_link} to download the update. Check the README.md for changes.", "red"))
    except requests.exceptions.RequestException as e:
        print("Error checking for updates:", e)


check_for_updates()


import os
import sys
import json

def prompt_user_for_config():

    api_key = input("Please enter your API key: ")
    google_api_key = input("Please enter your Google API key: ")
    google_search_id = input("Please enter your Google Search ID: ")

    model = ""
    while model not in ["gpt-3.5-turbo", "gpt-4"]:
        print("Please select a model:")
        print("1. gpt-3.5-turbo")
        print("2. gpt-4")
        model_choice = input("Enter the number corresponding to your choice: ")

        if model_choice == "1":
            model = "gpt-3.5-turbo"
        elif model_choice == "2":
            model = "gpt-4"
        else:
            print("Invalid selection. Please enter 1 or 2.")

    debug_code = int(input("Enable debug mode (1 for Enable, 2 for Disable): ")) == 1

    return {
        'api_key': api_key,
        'model': model,
        'google_api_key': google_api_key,
        'google_search_id': google_search_id,
        'debug_code': debug_code
    }

def load_config_from_file(config_file):
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    return config_data

config_file = "config.json"

if getattr(sys, 'frozen', False):
    print('Bundle Detected, asking user for variables.')
    
    if os.path.exists(config_file):
        config_data = load_config_from_file(config_file)
    else:
        config_data = prompt_user_for_config()
        print("Configuration saved to config.json, edit the file to change additional settings")

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

    api_function = config_data.get("api_function", "OPENAI")
    api_url = config_data.get("api_url", "https://api.openai.com/v1/chat/completions")
    max_tokens = config_data.get("max_tokens", 800)
    temperature = config_data.get("temperature", 0.8)
    frequency_penalty = config_data.get("frequency_penalty", 0.0)
    presence_penalty = config_data.get("presence_penalty", 0.0)
    top_p = config_data.get("top_p", 0.0)
    local_memory_file = config_data.get("local_memory_file", "memory.json")
    debug_code = config_data.get("debug_code", False)
    api_throttle = config_data.get("api_throttle", 10)
    api_retry = config_data.get("api_retry", 10)
    api_timeout = config_data.get("api_timeout", 90)
    api_count = config_data.get("api_count", 0)
    api_key = config_data.get("api_key")
    google_api_key = config_data.get("google_api_key")
    google_search_id = config_data.get("google_search_id")
    model = config_data.get("model")
else:
    debug_log('Not running from PyInstaller bundle')

    api_function = os.getenv("API_FUNCTION", "default_api_function")
    max_tokens = int(os.getenv("MAX_TOKENS", "100"))
    temperature = float(os.getenv("TEMPERATURE", "0.8"))
    frequency_penalty = float(os.getenv("FREQUENCY_PENALTY", "0.0"))
    presence_penalty = float(os.getenv("PRESENCE_PENALTY", "0.0"))
    top_p = float(os.getenv("TOP_P", "1.0"))
    local_memory_file = os.getenv("LOCAL_MEMORY_FILE", "memory.json")
    debug_code = os.getenv("DEBUG_CODE", "False") == "True"
    api_throttle = int(os.environ.get("API_THROTTLE", 10))
    api_retry = int(os.environ.get("API_RETRY", 10))
    api_timeout = int(os.environ.get("API_TIMEOUT", 90))
    google_api_key = os.environ["GOOGLE_API_KEY"]
    google_search_id = os.environ["CUSTOM_SEARCH_ENGINE_ID"]
#endregion


# region ### FUNCTIONS ###
max_conversation = int(os.environ.get('MAX_CONVERSATION', 6))
max_characters = int(os.environ.get('MAX_CHARACTERS', 2000))
api_count = 0
def alternate_api(number):
    global api_count
    global model
    global api_type
    global api_url
    global api_key
    if getattr(sys, 'frozen', False):
        return api_url, api_key, model, api_type
    else:
        if api_function == "ALTERNATE":
            api_count += 1
            if number % 2 == 0:
                api_url = os.getenv("AZURE_URL")
                api_key = os.getenv("AZURE_API_KEY")
                model = os.getenv("AZURE_MODEL_NAME")
                api_type = "AZURE"
            else:
                api_url = os.getenv("OPENAI_URL")
                api_key = os.getenv("OPENAI_API_KEY")
                model = os.getenv("OPENAI_MODEL_NAME")
                api_type = "OPENAI"
        elif api_function == "AZURE":
            api_url = os.getenv("AZURE_URL")
            api_key = os.getenv("AZURE_API_KEY")
            model = os.getenv("AZURE_MODEL_NAME")
            api_type = "AZURE"
        elif api_function == "OPENAI":
            api_url = os.getenv("OPENAI_URL")
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL_NAME")
            api_type = "OPENAI"
        else:
            raise ValueError(
                "Invalid API_FUNCTION value. Supported values are 'AZURE', 'OPENAI', or 'ALTERNATE'."
            )
        debug_log(
            "\nAPI Count: "
            + str(api_count)
            + "\nAPI URL: "
            + api_url
            + "\nAPI Key: "
            + api_key
            + "\nAPI Model: "
            + model
            + "\nAPI Type: "
            + api_type
        )
    
    return api_url, api_key, model, api_type


# Typing effect function
def typing_print(text, color=None):
    if text is None or len(text.strip()) == 0:
        return

    for char in text:
        print(colored(char, color=color) if color else char, end="", flush=True)
        time.sleep(0.005)  # adjust delay time as desired
    print()  # move cursor to the next line after printing the text

def remove_brackets(text):
    return re.sub(r'\[|\]', '', text)


# Create JSON message function
def create_json_message(
    response_120_words="[DETAILED RESPONSE]",
    command_string="[COMMAND]",
    command_argument="[ARGUMENT]",
    current_task="[CURRENT TASK]",
    suggested_next_task="[SUGGESTED NEXT TASK]",
):
    json_message = {
        "response_120_words": response_120_words,
        "command_string": command_string,
        "command_argument": command_argument,
        "current_task": current_task,
        "suggested_next_task": suggested_next_task,
    }
    return json.dumps(json_message)


# Get random user agent function
def get_random_user_agent():
    ua = UserAgent()
    browsers = ["Firefox", "Chrome", "Safari", "Opera", "Internet Explorer"]
    operating_systems = ["Windows", "Macintosh", "Linux", "Android", "iOS"]
    browser = random.choice(browsers)
    operating_system = random.choice(operating_systems)

    try:
        user_agent = ua.data_randomize(
            f"{browser} {ua.random}, {operating_system}"
        )  # type: ignore
    except:
        user_agent = ua.random
    return user_agent


# endregion

# region ### API QUERY ###


def query_bot(messages, retries=20):
    alternate_api(api_count)    
    time.sleep(api_throttle)
    
    for attempt in range(retries):
        try:
            json_payload = json.dumps(
                {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "frequency_penalty": presence_penalty,
                    "presence_penalty": presence_penalty,
                }
            )
            debug_log(json_payload)
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            botresponse = requests.request(
                "POST", api_url, headers=headers, data=json_payload, timeout=api_timeout
            )
            debug_log(f"Returned Response from OpenAI: {botresponse.status_code}")
            debug_log(botresponse)
            
            # Handling error response
            response_json = botresponse.json()
            if "error" in response_json:
                error_message = response_json["error"]["message"]
                print(f"Error: {error_message}")
                continue
        

            responseparsed = response_json["choices"][0]["message"]["content"]
            debug_log(f"Parsed Choices Node: {responseparsed}")
            responseformatted = json.loads(responseparsed)

            if responseformatted is not None:
                if "current_task" in responseformatted:
                    current_task = responseformatted["current_task"]
                    response = responseformatted["response_120_words"]
                    command_string = responseformatted["command_string"]
                    command_argument = responseformatted["command_argument"]
                    suggested_next_task = responseformatted["suggested_next_task"]

                    return (
                        response,
                        command_string,
                        command_argument,
                        current_task,
                        suggested_next_task,
                    )
                else:
                    alternate_api(api_count)
                    return (
                        "No valid json, ensure you format your responses as the required json",
                        "None",
                        "None",
                        "Reformat Response as json",
                        "Continue where you left off",
                        "Unknown",
                    )
        except Exception as e:
            if attempt < retries - 1:
                print("API Exception...Retrying...")
                alternate_api(api_count)
                time.sleep(2**attempt)
            else:
                raise e


# endregion

# region ### COMMANDS ###

# region ### GENERATE PDF ###


def create_pdf_from_html_markup(
    response, command_string, command_argument, current_task, suggested_next_task
):
    try:
        # Parse the input string to extract the filename and content
        parts = command_argument.split("Content:")
        filename_part, content = parts[0].strip(), parts[1].strip()
        filename = filename_part.replace("Filename:", "").strip()

        # Concatenate the working_folder path with the filename
        output_path = os.path.join(working_folder, filename)

        # Set up PDFKit configuration (replace the path below with the path to your installed wkhtmltopdf)
        config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")

        if content.lower().endswith('.html'):
            # If content is an HTML file, read the content of the file and pass it to pdfkit
            html_file_path = os.path.join(working_folder, content)
            with open(html_file_path, 'r') as f:
                html_content = f.read()
            pdfkit.from_string(html_content, output_path, configuration=config)
        else:
            # Convert the HTML content to a PDF file using PDFKit
            pdfkit.from_string(content, output_path, configuration=config)

        return create_json_message(
            "PDF Created Successfully",
            command_string,
            command_argument,
            current_task,
            "Determine next task",
            
        )
    except Exception as e:
        debug_log(f"Error: {e}")
        return create_json_message(
            "Error: " + str(e),
            command_string,
            command_argument,
            current_task,
            "Google Error",
            
        )

# endregion

# region ### SHELL COMMANDS ###

def run_bash_shell_command(
    response, command_string, command_argument, current_task, suggested_next_task
):
    process = subprocess.Popen(
        command_argument,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=working_folder  # Set the working directory here
    )

    try:
        # Set a timeout value (in seconds) for the command execution
        timeout_value = 120
        output, error = process.communicate(timeout=timeout_value)
    except subprocess.TimeoutExpired:
        process.kill()
        set_global_success(False)
        return create_json_message(
            "Command execution timed out.",
            command_string,
            command_argument,
            "I should research the error",
            suggested_next_task,
            
        )

    return_code = process.returncode
    debug_log(f"Return Code: {return_code}")

    shell_response = ""

    if "mkdir" in command_argument:
        if return_code == 0:
            set_global_success(True)
            shell_response = "Folder created successfully. " + command_argument
        elif (
            return_code == 1
            and "Folder already exists navigate to folder. " in error.decode("utf-8")
        ):
            set_global_success(True)
            shell_response = (
                "Folder already exists. Try switching to folder. " + command_argument
            )
        else:
            shell_response = f"Error creating folder, research the error: {error.decode('utf-8').strip()}"

    elif "touch" in command_argument:
        if return_code == 0:
            set_global_success(True)
            shell_response = "File created and saved successfully. " + command_argument
        else:
            set_global_success(False)
            shell_response = f"Error creating file, Research the error: {error.decode('utf-8').strip()}"

    else:
        if return_code == 0:
            set_global_success(True)
            # Add slicing to limit output length
            shell_response = (
                "Shell Command Output: "
                + f"{output.decode('utf-8').strip()}"[:max_characters]
            )
        else:
            set_global_success(False)
            # Add slicing to limit error length
            shell_response = f"Shell Command failed, research the error: {error.decode('utf-8').strip()}"[
                :max_characters
            ]

    debug_log(shell_response)
    return create_json_message(
        "BASH Command Output: " + shell_response,
        command_string,
        command_argument,
        "I should analyze the output to ensure success and research any errors",
        suggested_next_task,
        
    )


# endregion

#region ### WINDOWS COMMANDS ###

import subprocess

def run_win_shell_command(
    response, command_string, command_argument, current_task, suggested_next_task
):
    process = subprocess.Popen(
        command_argument,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=working_folder  # Set the working directory here
    )

    try:
        # Set a timeout value (in seconds) for the command execution
        timeout_value = 120
        output, error = process.communicate(timeout=timeout_value)
    except subprocess.TimeoutExpired:
        process.kill()
        set_global_success(False)
        return create_json_message(
            "Command execution timed out.",
            command_string,
            command_argument,
            "I should research the error",
            suggested_next_task,
            
        )

    return_code = process.returncode
    debug_log(f"Return Code: {return_code}")

    shell_response = ""

    if "mkdir" in command_argument.lower():
        if return_code == 0:
            set_global_success(True)
            shell_response = "Folder created successfully. " + command_argument
        elif (
            return_code == 1
            and "Folder already exists navigate to folder." in error.decode("utf-8")
        ):
            set_global_success(True)
            shell_response = (
                "Folder already exists. Try switching to folder. " + command_argument
            )
        else:
            shell_response = f"Error creating folder, research the error: {error.decode('utf-8').strip()}"

    elif "echo" in command_argument.lower() and ">" in command_argument:
        if return_code == 0:
            set_global_success(True)
            shell_response = "File created and saved successfully. " + command_argument
        else:
            set_global_success(False)
            shell_response = f"Error creating file, Research the error: {error.decode('utf-8').strip()}"

    else:
        if return_code == 0:
            set_global_success(True)
            # Add slicing to limit output length
            shell_response = (
                "Shell Command Output: "
                + f"{output.decode('utf-8').strip()}"[:max_characters]
            )
        else:
            set_global_success(False)
            # Add slicing to limit error length
            shell_response = f"Shell Command failed, research the error: {error.decode('utf-8').strip()}"[
                :max_characters
            ]

    debug_log(shell_response)
    return create_json_message(
        "Windows Command Output: " + shell_response,
        command_string,
        command_argument,
        "I should analyze the output to ensure success and research any errors",
        suggested_next_task,
        
    )

#endregion

# region ### ALLOWS MODEL TO CONTINUE ###


def no_command(
    response, command_string, command_argument, current_task, suggested_next_task
):
    response_string = json.dumps(command_argument)
    set_global_success(True)
    debug_log(f"Response String: {response_string}")
    return create_json_message(
        response, command_string, command_argument, current_task, suggested_next_task
    )


# endregion

# region ### SAVE RESEARCH ###

def save_research(response, command_string, command_argument, current_task, suggested_next_task):
    try:
        # Split the command argument into title and content
        title = command_argument.split("Title: ")[1].split(" ResearchContent: ")[0]
        content = command_argument.split("Title: ")[1].split(" ResearchContent: ")[1]
    except IndexError:
        return create_json_message(
            "Error: Invalid format! Please use 'Title: <title> ResearchContent: <content>'.",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )

    # Get the current datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a dictionary with the title, content, and datetime
    research = {"DateTime": current_time, "Title": title, "ResearchContent": content}

    # Save the research to a JSON node
    research_file_path = os.path.join(working_folder, "research.json")
    with open(research_file_path, "a") as f:
        f.write(json.dumps(research))
        f.write("\n")
    
    return create_json_message(
        "Research saved successfully",
        command_string,
        command_argument,
        current_task,
        suggested_next_task,
        
    )



# endregion

# region ### FETCH RESEARCH ###


def fetch_research(response, command_string, command_argument, current_task, suggested_next_task):
    research_list = []
    
    # Fetch the research.json file from the working_folder
    research_file_path = os.path.join(working_folder, "research.json")
    with open(research_file_path, "r") as f:
        for line in f:
            research = json.loads(line)
            research_list.append(research)
            
    formatted_research = ""
    for research in research_list:
        formatted_research += f'DateTime: {research["DateTime"]}\nTitle: {research["Title"]}\nResearchContent: {research["ResearchContent"]}\n\n'
        
    return create_json_message(
        formatted_research,
        command_string,
        command_argument,
        current_task,
        suggested_next_task,
        
    )



# endregion

# region ### CREATE TASK LIST ###
# W Writes the task list to bots 2nd message so he always remembers


def create_task_list(
    response, command_string, command_argument, current_task, suggested_next_task
):
    if command_argument is not None:
        message_handler(None, command_argument, "task")
    return create_json_message(
        "Task List Saved Successfully",
        command_string,
        command_argument,
        current_task,
        suggested_next_task,
        
    )


# endregion

# region ### CREATE PYTHON SCRIPT ###

def create_python_script(
    response, command_string, command_argument, current_task, suggested_next_task
):
    try:
        filename = None
        content = None

        # Extract filename and content using regex
        regex_pattern = r'Filename:\s*(\S+)\s+Content:\s*```(.*?)```'
        match = re.search(regex_pattern, command_argument, re.DOTALL)

        if match:
            filename = match.group(1)
            content = match.group(2)
        else:
            set_global_success(False)
            return create_json_message(
                "Invalid args. Use the Format: Filename: [FILENAME] Content: ```[CONTENT]```",
                command_string,
                command_argument,
                current_task,
                "Try again using the correct arguments.",
                
            )

        os.makedirs(working_folder, exist_ok=True)
        file_path = os.path.join(working_folder, filename)

        with open(file_path, "w") as file:
            file.write(content)

        set_global_success(True)

        return create_json_message(
            f"Python code created and saved successfully:\nFilename: {filename}\nContent:\n```python\n{content}\n```",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )

    except Exception as e:
        set_global_success(False)
        debug_log(f"Error: {str(e)}")
        return create_json_message(
            f"Error: {str(e)}",
            command_string,
            command_argument,
            current_task,
            "Read the contents of the script to ensure its formatted correctly, or reserach the internet on the error.",
            
        )

# endregion

# region ### WRITE NEW CONTENT TO FILE ###


def write_new_content_to_file(
    response, command_string, command_argument, current_task, suggested_next_task
):
    try:
        filename = None
        content = None

        # Extract filename and content using regex
        regex_pattern = r'Filename:\s*(\S+)\s+Content:\s*```(.*?)```'
        match = re.search(regex_pattern, command_argument, re.DOTALL)
        os.makedirs(working_folder, exist_ok=True)
        if match:
            filename = match.group(1)
            content = match.group(2)
        else:
            set_global_success(False)
            return create_json_message(
                "Invalid args. Use the Format: Filename: [FILENAME] Content: ```[CONTENT]```",
                command_string,
                command_argument,
                current_task,
                "Try the command again using the correct arguments.",
                
            )

        if os.path.exists(os.path.join(working_folder, filename)):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"

        file_path = os.path.join(working_folder, filename)

        with open(file_path, "w") as file:
            file.write(content)

        set_global_success(True)
        return create_json_message(
            f"File {filename} created and saved successfully\n{content}",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )

    except Exception as e:
        set_global_success(False)
        debug_log(f"Error: {str(e)}")
        return create_json_message(
            f"Error: {str(e)}",
            command_string,
            command_argument,
            "Retry or Reserch Current Task",
            suggested_next_task,
            
        )


# endregion

# region ## APPEND CONTENT TO FILE ##

def append_content_to_existing_file(
    response, command_string, command_argument, current_task, suggested_next_task
):
    try:
        # Extract filename and content using regex
        regex_pattern = r'Filename:\s*(\S+)\s+Content:\s*```(.*?)```'
        match = re.search(regex_pattern, command_argument, re.DOTALL)

        if match:
            filename = match.group(1)
            content = match.group(2)
        else:
            set_global_success(False)
            return create_json_message(
                "Invalid format. Use the Format: Filename: [FILENAME] Content: ```[CONTENT]```",
                command_string,
                command_argument,
                current_task,
                "Try again using the correct arguments.",
                
            )

        if not os.path.exists(working_folder):
            os.makedirs(working_folder)

        file_path = os.path.join(working_folder, filename)

        with open(file_path, "a") as file:
            file.write(content + "\n")

        return create_json_message(
            "File content successfully appended to " + filename,
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )
    except Exception as e:
        set_global_success(False)
        debug_log(f"Error: {str(e)}")
        return create_json_message(
            f"Error: {str(e)}",
            command_string,
            command_argument,
            "Retry or Reserch Current Task",
            suggested_next_task,
            
        )


# endregion

# region ### READ CONTENT FROM FILE ###


def read_content_from_file(
    response, command_string, command_argument, current_task, suggested_next_task
):
    try:
        filename = None
        max_characters = 1000  # define max_characters if not already defined

        args = command_argument.split()

        for i, arg in enumerate(args):
            if arg == "Filename:" and i + 1 < len(args):
                filename = args[i + 1]

        if not filename:
            set_global_success(False)
            debug_log(
                f"Invalid args. {command_argument} Use the Format: Filename: [FILENAME WITH EXT]"
            )
            return create_json_message(
                f"Invalid args. {command_argument} Use the Format: Filename: [FILENAME WITH EXT]",
                command_string,
                command_argument,
                current_task,
                "I will use to proper format and try again",
                
            )

        # Concatenate the working_folder path with the filename
        file_path = os.path.join(working_folder, filename)

        if not os.path.exists(file_path):
            set_global_success(False)
            debug_log(
                f"File not found. {command_argument} Use the Format: Filename: [FILENAME WITH EXT]"
            )
            return create_json_message(
                f"File not found. {command_argument} Use the Format: Filename: [FILENAME WITH EXT]",
                command_string,
                command_argument,
                current_task,
                "I will check that my file name is correct or fix the format of my argument",
                
            )

        with open(file_path, "r") as file:
            content = file.read()[:max_characters]
        set_global_success(True)
        return create_json_message(
            "File Content: " + f"{content}",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )
    except Exception as e:
        set_global_success(True)
        debug_log(f"Error: {str(e)}")
        return create_json_message(
            "Error: " + f"Error: {str(e)}",
            command_string,
            command_argument,
            current_task,
            "I will research the error",
            
        )


# endregion

#region ### DOWNLOAD FILES ###
def download_file(response, command_string, command_argument, current_task, suggested_next_task):
    if not os.path.exists(working_folder):
        os.makedirs(working_folder)

    try:
        filename = command_argument.split("/")[-1]
        output_path = os.path.join(working_folder, filename)
        command_list = ["wget", "-O", output_path, command_argument]

        process = subprocess.run(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        if process.returncode == 0:
            return create_json_message(
            "File downloaded successfully and saved to local folder",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )
        else:
            return create_json_message(
            "Error downloading file",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )

    except subprocess.CalledProcessError as e:
        return create_json_message(
            f"Error: {e}",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )
#endregion        

# region ### SEARCH GOOGLE ###


def search_google(
    response, command_string, command_argument, current_task, suggested_next_task
):
    try:
        args = command_argument.split("|")

        query = args[0].strip()
        start_index = (
            int(args[1].strip()) if len(args) > 1 and args[1].strip() else None
        )
        num_results = (
            int(args[2].strip()) if len(args) > 2 and args[2].strip() else None
        )
        search_type = args[3].strip() if len(args) > 3 and args[3].strip() else None
        file_type = args[4].strip() if len(args) > 4 and args[4].strip() else None
        site_search = args[5].strip() if len(args) > 5 and args[5].strip() else None
        date_restrict = args[6].strip() if len(args) > 6 and args[6].strip() else None

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": google_search_id,
            "q": query,
            "safe": "off",
            "num": 10,
        }

        if num_results:
            params["num"] = min(num_results, 30)

        if start_index:
            params["start"] = start_index

        if search_type:
            params["searchType"] = search_type

        if file_type:
            params["fileType"] = file_type

        if site_search:
            params["siteSearch"] = site_search

        if date_restrict:
            params["dateRestrict"] = date_restrict

        google_response = requests.get(url, params=params)
        data = google_response.json()

        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({"title": item["title"], "link": item["link"]})
        else:
            set_global_success(False)
            return create_json_message(
                "No Search Results Returned",
                command_string,
                command_argument,
                current_task,
                "I will choose another search term",
                
            )

        formatted_results = ""
        for result in results:
            formatted_results += f"Google Image Search Results:\n"
            formatted_results += f"Title: {result['title']}\n"
            formatted_results += f"Link: {result['link']}\n\n"
        searchresults = json.dumps(formatted_results)
        debug_log(searchresults)
        set_global_success(True)
        # GOOGLE IMAGE RESULTS RETURNED
        return create_json_message(
            "Search Results: " + searchresults,
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
            
        )
    except Exception as e:
        debug_log(f"Error: {str(e)}")
        set_global_success(False)
        return create_json_message(
            "No Search Results Returned" + f"Error: {str(e)}",
            command_string,
            command_argument,
            current_task,
            "I will double check my arguments or move to next task.",
            
        )


# endregion

# region ### BROWSE WEBSITE ###


def sanitize_content(content):
    content = unidecode(content)
    content = content.encode("ascii", "ignore").decode("ascii")
    return content


def scrape_website_url(response, command_string, command_argument, current_task, suggested_next_task):
    try:
        url, raw_html, max_length = command_argument.split('|')
        max_length = int(max_length.split('=')[1])
        responsehtml = requests.get(url, timeout=30)
        responsehtml.raise_for_status()
    except requests.RequestException as e:
        return create_json_message(
            "Error: " + f"Error: {str(e)}",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
        )

    try:
        if raw_html.lower() == 'true':
            content = responsehtml.text
        else:
            soup = BeautifulSoup(responsehtml.text, "html.parser")
            content = soup.get_text()

        content = content.replace("\n", " ")
        debug_log(content)
        content_cleaned = sanitize_content(content)[:max_length]
        content_json_escaped = json.dumps(content_cleaned)

    except Exception as e:
        return create_json_message(
            "Error: " + str(e) +
            "Check your argument or move on to another url.",
            command_string,
            command_argument,
            current_task,
            suggested_next_task,
        )

    return create_json_message(
        "URL: " + url + "\nContent: " + content_json_escaped,
        command_string,
        command_argument,
        current_task,
        suggested_next_task,
    )



# endregion

# region ### MISSION ACCOMPLISHED ###


def mission_accomplished(
    response, command_string, command_argument, current_task, suggested_next_task
):
    set_global_success(True)
    print("Mission accomplished:", command_argument)
    sys.exit()


# endregion
# endregion

# region ### MESSAGE HANDLER ###


def message_handler(current_prompt, message, role):
    def update_message_history(role, content):
        try:
            message_history.append({"role": role, "content": content})
        except Exception as e:
            message_history.append(
                {
                    "role": role,
                    "content": "Command did not return anything, let admin know",
                }
            )
            print(
                f"Error occurred while appending message: Check logs, message set to None {e}"
            )

    def limit_message_history():
        while len(message_history) > max_conversation + 1:
            message_history.pop(2)


    if len(message_history) == 0:
        message_history.insert(
            0, {"role": "system", "content": current_prompt})
    elif role == "system":
        message_history[0] = {"role": "system", "content": current_prompt}

    if message is not None:
        if role == "task":
            message_history.pop(1)
            message_history.insert(1, {"role": "assistant", "content": message})
            return
        else:
            update_message_history(role, message)

    limit_message_history()
    return message_history


# endregion

# region ### COMMAND HANDLER ###


def command_handler(
    response, command_string, command_argument, current_task, suggested_next_task
):
    if not command_string:  # Check if the command_string is empty or None
        return create_json_message(
            "task",
            "command_string Executed Successfully",
            command_string,
            command_argument,
            "Verify Task was executed",
        )

    function = globals().get(command_string)
    if function is None:
        debug_log(
            "Invalid command_string. "
            + command_string
            + " is not a valid command_string."
        )
        return create_json_message(
            "failed",
            "The command_string is invalid, send commands in json format like this: "
            + create_json_message(),
        )
    return function(
        response, command_string, command_argument, current_task, suggested_next_task
    )


# endregion

# region ### ROUTING HANDLER ###

# region ### OLD SCHOOL THROWBACK ##
def bbs_ascii_lordgpt():
    letters = {
        'L': ["██╗",
              "██║",
              "██║",
              "██║",
              "███"],
        'O': ["██████",
              "██╔═██╗",
              "██║ ██║",
              "██║ ██║",
              "██████"],
        'R': [" █████╗",
              "██╔═██╗",
              "█████╔╝",
              "██╔═██╗",
              " ██║ ██"],
        'D': [" █████╗",
              "██╔═██╗",
              "██║ ██║",
              "██║ ██║",
              " ██████"]}

    word = "LORD"
    for row in range(5):
        line = ""
        for letter in word:
            line += letters[letter][row] + " "
        print(line)
#endregion


def openai_bot_handler(current_prompt, message, role):
    messages = message_handler(current_prompt, message, role)
    (
        response,
        command_string,
        command_argument,
        current_task,
        suggested_next_task,
        
    ) = query_bot(
        messages
    )  # type: ignore

    print(colored("LordGPT Thoughts: ", color="green"), end="")
    typing_print(str(response))
    print(colored("Currently :       ", color="blue"), end="")
    typing_print(str(current_task) + "")
    print(colored("Next Task:        ", color="magenta"), end="")
    typing_print(str(suggested_next_task) + "")
    print(colored("Executing CMD:    ", color="red"), end="")
    typing_print(str(command_string))
    print(colored("CMD Argument:     ", color="red"), end="")
    typing_print(str(command_argument) + "\n\n")

    handler_response = command_handler(
        response, command_string, command_argument, current_task, suggested_next_task
    )

    if success == True:
        return handler_response
    return handler_response


# endregion

# region ### MAIN ###


def main_loop():
    # Ask the user for the goal of the bot
    print(colored("Tips: ", "green"))


    print(
        colored(
            "1. We are constantly refining GPT3.5. Its hit or miss. LordGPT works best with GPT4." +
            "\n2. Example Goal: Determine my location, gather weather data for my location and create a PDF report with the information." +
            "\n3. Report Issues: https://github.com/Cytranics/LordGPT/issues"
            "\n4. Discord: https://discord.gg/2jT32cM8", "yellow",
        )
)

    user_goal = input("Goal: ")
    print(colored("Creating detailed plan to achive the goal....", "green"))
    if not user_goal:
        user_goal = "Find my location, Gather the 5 day weather forecast for my location, save the detailed results of each day to a PDF."
        print(colored("Goal: " + user_goal, "green"))
    set_global_success(True)

    bot_send = openai_bot_handler(bot_prompt + user_goal, f"""{{"response_120_words": "Respond with your detailed task list", "command_string": "[COMMAND]", "command_argument": "[ARGUMENT]", "current_task": "[CURRENT TASK]", "suggested_next_task": "[SUGGESTED NEXT TASK]"}}""" + user_goal, "assistant")

    while True:
        num_input = input(
            "Enter the amount of responses you want to process automatically (Default 1): "
        )
        try:
            num_iterations = int(num_input) if num_input.strip() else 1
        except ValueError:
            print("Invalid input. Using default value of 1.")
            num_iterations = 1

        for _ in range(num_iterations):
            loop = bot_send
            bot_send = openai_bot_handler(bot_prompt, loop, "assistant")
            loop = bot_send

        continue_choice = input("Is LordG on the right track If not, select n? (y/n): ").lower()
        if continue_choice == "n":
            break


if __name__ == "__main__":
    bbs_ascii_lordgpt()
    main_loop()


# endregion