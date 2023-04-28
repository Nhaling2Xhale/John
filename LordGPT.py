# region ### IMPORTS ###
import os
import sys
import re
import time
import random
import json
import subprocess
import datetime
import ssl
import requests
import requests.exceptions
from time import sleep
from typing import Dict

from dotenv import load_dotenv
from termcolor import colored
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from unidecode import unidecode
from yaspin import yaspin
import pdfkit
import urllib.request

from scripts.bot_prompts import command_list, bot_prompt
from scripts.bot_commands import botcommands
from playwright.sync_api import sync_playwright
#endregion

current_path = os.getcwd()
working_folder = os.path.join(current_path, 'LordGPT_folder')
if not os.path.exists(working_folder):
    os.makedirs(working_folder)

# region GLOBAL VARIABLES
config_file = "config.json"
current_version = "1.2"
update_url = "https://thelordg.com/downloads/version.txt"
changelog_url = "https://thelordg.com/downloads/changelog.txt"
download_link = "https://thelordg.com/downloads/LordGPT.exe"
message_history = []
# endregion

# region GLOBAL FUNCTIONS
def debug_log(message, value=None):
    if debug_code:
        # Create the debug.txt file path
        debug_file_path = os.path.join(working_folder, "debug.txt")

        # Write the message and value to the debug.txt file
        with open(debug_file_path, "a") as debug_file:
            debug_file.write(f"{message}{value}\n")

    
def set_global_success(value):
    global success
    success = value

def check_for_updates():
    try:
        update_response = requests.get(update_url)
        update_response.raise_for_status()
        latest_version = update_response.text.strip()

        if latest_version != current_version:
            print(colored(
                f"A new version ({latest_version}) is available! Please visit {download_link} to download the update. Github: https://github.com/Cytranics/LordGPT", "red"))

            # Fetch the changelog
            changelog_response = requests.get(changelog_url)
            changelog_response.raise_for_status()
            changelog = changelog_response.text.strip()

            # Display the changelog
            print(colored("Changelog:", "yellow"))
            print(changelog)

    except requests.exceptions.RequestException as e:
        print("Error checking for updates:", e)
check_for_updates()

def prompt_user_for_config():
    api_key = input("Please enter your OPENAI API key: ")
    google_api_key = input("Please enter your Google API key: ")
    google_search_id = input("Please enter your Google Search ID: ")

    model = ""
    while model not in ["gpt-3.5-turbo", "gpt-4"]:
        print("Please select a model:")
        print("1. GPT-3.5")
        print("2. GPT-4")
        model_choice = input("Choose the number of the model you have access to: ")

        if model_choice == "1":
            model = "gpt-3.5-turbo"
        elif model_choice == "2":
            model = "gpt-4"
        else:
            print("Invalid selection. Please enter 1 or 2.")

    debug_code = int(input("Enable debug.txt in working folder? (1 for Enable, 2 for Disable): ")) == 1

    return {
        'API_FUNCTION': "OPENAI",
        'API_RETRY': 10,
        'API_THROTTLE': 10,
        'API_TIMEOUT': 90,
        'AZURE_URL': None,
        'AZURE_API_KEY': None,
        'AZURE_MODEL_NAME': None,
        'BD_ENABLED': False,
        'BD_PASSWORD': None,
        'BD_PORT': 22225,
        'BD_USERNAME': None,
        'CUSTOM_SEARCH_ENGINE_ID': google_search_id,
        'DEBUG_CODE': debug_code,
        'FREQUENCY_PENALTY': 0.0,
        'GOOGLE_API_KEY': google_api_key,
        'MAX_CONVERSATION': 5,
        'MAX_TOKENS': 800,
        'OPENAI_API_KEY': api_key,
        'OPENAI_MODEL_NAME': model,
        'OPENAI_URL': "https://api.openai.com/v1/chat/completions",
        'PRESENCE_PENALTY': 0.0,
        'TEMPERATURE': 0.8,
        'TOP_P': 0.0,
    }



def load_config_from_file(config_file):
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    return config_data


config_file = "config.json"


def load_variables(frozen):
    if frozen:
        print("Frozen Detected")
        if os.path.exists(config_file):
            config_data = load_config_from_file(config_file)
        else:
            config_data = prompt_user_for_config()
            print(
                "Configuration saved to config.json, edit the file to change advanced settings")

            with open(config_file, 'w') as f:
                json.dump(config_data, f)

        return config_data

    else:
        load_dotenv(override=True)
        return os.environ


def get_variable(env_data, variable_name, default_value=None, variable_type=None):
    value = env_data.get(variable_name, default_value)

    if variable_type == "int":
        return int(value)
    elif variable_type == "float":
        return float(value)
    elif variable_type == "bool":
        return value == "True"

    return value


config_file = "config.json"
frozen = getattr(sys, 'frozen', False)
env_data = load_variables(frozen)

api_function = get_variable(env_data, "API_FUNCTION", "OPENAI")
api_retry = get_variable(env_data, "API_RETRY", 10, "int")
api_throttle = get_variable(env_data, "API_THROTTLE", 10, "int")
api_timeout = get_variable(env_data, "API_TIMEOUT", 90, "int")
bd_enabled = get_variable(env_data, "BD_ENABLED", "False", "bool")
bd_password = get_variable(env_data, "BD_PASSWORD", None)
bd_port = get_variable(env_data, "BD_PORT", 22225, "int")
bd_username = get_variable(env_data, "BD_USERNAME")
debug_code = True
frequency_penalty = get_variable(env_data, "FREQUENCY_PENALTY", 0.0, "float")
google_api_key = get_variable(env_data, "GOOGLE_API_KEY")
google_search_id = get_variable(env_data, "CUSTOM_SEARCH_ENGINE_ID")
max_characters = get_variable(env_data, "MAX_CHARACTERS", 1000, "int")
max_conversation = get_variable(env_data, "MAX_CONVERSATION", 5, "int")
max_tokens = get_variable(env_data, "MAX_TOKENS", 800, "int")
presence_penalty = get_variable(env_data, "PRESENCE_PENALTY", 0.0, "float")
temperature = get_variable(env_data, "TEMPERATURE", 0.8, "float")
top_p = get_variable(env_data, "TOP_P", 0.0, "float")


api_count = 0
def alternate_api(number):
    global api_count
    global model
    global api_type
    global api_url
    global api_key

    if api_function == "ALTERNATE":
        api_count += 1
        if number % 2 == 0:
            api_url = get_variable(env_data, "AZURE_URL")
            api_key = get_variable(env_data, "AZURE_API_KEY")
            model = get_variable(env_data, "AZURE_MODEL_NAME")
            api_type = "AZURE"
        else:
            api_url = get_variable(env_data, "OPENAI_URL")
            api_key = get_variable(env_data, "OPENAI_API_KEY")
            model = get_variable(env_data, "OPENAI_MODEL_NAME")
            api_type = "OPENAI"
    elif api_function == "AZURE":
        api_url = get_variable(env_data, "AZURE_URL")
        api_key = get_variable(env_data, "AZURE_API_KEY")
        model = get_variable(env_data, "AZURE_MODEL_NAME")
        api_type = "AZURE"
    elif api_function == "OPENAI":
        api_url = get_variable(env_data, "OPENAI_URL")
        api_key = get_variable(env_data, "OPENAI_API_KEY")
        model = get_variable(env_data, "OPENAI_MODEL_NAME")
        api_type = "OPENAI"
    else:
        raise ValueError(
            "Invalid API_FUNCTION value. Supported values are 'AZURE', 'OPENAI', or 'ALTERNATE'."
        )

# Typing effect function
def typing_print(text, color=None):
    if text is None or len(text.strip()) == 0:
        return

    for char in text:
        print(colored(char, color=color) if color else char, end="", flush=True)
        time.sleep(0.003)  # adjust delay time as desired
    print()  # move cursor to the next line after printing the text

def remove_brackets(text):
    return re.sub(r'\[|\]', '', text)


# Create JSON message function
def create_json_message(
    reasoning_80_words="[DETAILED REASONING]",
    command_string="[COMMAND]",
    command_argument="[ARGUMENT]",
    current_task="[CURRENT TASK]",
    self_prompt_action="[SUGGESTED NEXT TASK]",
):
    json_message = {
        "reasoning_80_words": reasoning_80_words,
        "command_string": command_string,
        "command_argument": command_argument,
        "current_task": current_task,
        "self_prompt_action": self_prompt_action,
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

def get_random_text_and_color(text_color_dict):
    key = random.choice(list(text_color_dict.keys()))
    return key, text_color_dict[key]

# endregion

# region ### API QUERY ###
text_color_dict = {
    "Unleashing hamsters..........": "light_green",
    "Firing up the potato cannons..": "light_yellow",
    "Summoning the data demons.....": "magenta",
    "Engaging turbo snail mode.....": "light_blue",
    "Sending carrier pigeons.......": "white",
    "Revving up the avocado engine.": "green",
    "Awakening the Kraken.........": "cyan",
    "Charging the laser chickens...": "yellow",
    "Summoning the dark lord.......": "red",
    "Brewing coffee for the servers.": "dark_grey"
}

def query_bot(messages, retries=api_retry):
        random_text, random_color = get_random_text_and_color(text_color_dict)
        alternate_api(api_count)    
        time.sleep(api_throttle) #type: ignore
        debug_log("Model: ", model)
        debug_log("API Key:", api_key)
        debug_log("Google API Key:", google_api_key)
        debug_log("Google Search ID:", google_search_id)
        debug_log("API Function:", api_function)
        debug_log("API Retry:", api_retry)
        debug_log("API Throttle:", api_throttle)
        debug_log("API Timeout:", api_timeout)
        debug_log("BD Enabled:", bd_enabled)
        debug_log("BD Password:", bd_password)
        debug_log("BD Port:", bd_port)
        debug_log("BD Username:", bd_username)
        debug_log("Debug Code:", debug_code)
        debug_log("Frequency Penalty:", frequency_penalty)
        debug_log("Max Characters:", max_characters)
        debug_log("Max Conversation:", max_conversation)
        debug_log("Max Tokens:", max_tokens)
        debug_log("Presence Penalty:", presence_penalty)
        debug_log("Temperature:", temperature)
        debug_log("Top P:", top_p)
        
        with yaspin(text=random_text, color=random_color) as spinner:
            for attempt in range(retries): #type: ignore
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
                    
                    debug_log("JSON Payload: ", json_payload)
                    headers = {
                        "api-key": api_key,
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    }
                    
                    # BRIGHT DATA PROXY
                    if bd_enabled:
                        
                        json_utf8 = json_payload.encode('utf-8')
                        session_id = random.random()
                        super_proxy_url = ('http://%s-session-%s:%s@zproxy.lum-superproxy.io:%d' %
                                    (bd_username, session_id, bd_password, bd_port))
                        proxy_handler = urllib.request.ProxyHandler({
                            'http': super_proxy_url,
                            'https': super_proxy_url,
                    })
                        
                        ssl._create_default_https_context = ssl._create_unverified_context
                        opener = urllib.request.build_opener(proxy_handler)
                        
                        req = urllib.request.Request(
                            api_url, data=json_utf8, headers=headers)  # type: ignore
                        

                        #BRIGHT DATA REQUEST                
                        request = opener.open(req, timeout=api_timeout) #type: ignore
                        
                        uresponse = request.read()
                        
                        utfresponse = uresponse.decode('utf-8')
                        botresponse = json.loads(utfresponse)
                        response_json = botresponse
                        
                        debug_log("Bot reply: ", botresponse)
                    else:
                        #STANDARD API REQUEST
                        
                        botresponse = requests.request("POST", api_url, headers=headers, data=json_payload, timeout=api_timeout) #type: ignore
                        
                        response_json = botresponse.json()
                        
                    debug_log("Bot reply: ", botresponse)
                    
                    # Handling error response
                    
                    if "error" in response_json:
                        error_message = response_json["error"]["message"]
                        print(f"Error: {error_message}")
                        print("max_tokens is too high.....GPT3.5 is limited, so change max_tokens to a lower value.")
                        continue
                
                
                    responseparsed = response_json["choices"][0]["message"]["content"]
                    
                    try:
                        debug_log(f"Parsed Choices Node: {responseparsed}")
                        responseformatted = json.loads(responseparsed)
                    except:
                        debug_log(f"Formatted non json response: {responseformatted}]")
                        responseformatted = create_json_message(responseformatted, "None", "None", "None", "None")
                   
                    
            
                    if responseformatted is not None:
                        if "current_task" in responseformatted:
                            current_task = responseformatted["current_task"]
                            reasoning = responseformatted["reasoning_80_words"]
                            command_string = responseformatted["command_string"]
                            command_argument = responseformatted["command_argument"]
                            self_prompt_action = responseformatted["self_prompt_action"]
                            
                            
                            return (
                                reasoning,
                                command_string,
                                command_argument,
                                current_task,
                                self_prompt_action,
                            )
                            
                        else:
                            
                            alternate_api(api_count)
                            return (
                                "No valid json, ensure you format your responses as the required json",
                                "None",
                                "None",
                                "Reformat reply as json",
                                "Continue where you left off",
                                "Unknown",
                            )
        
                except Exception as e:
                    if attempt < retries - 1: #type: ignore
                        print(f"API Exception: {str(e)}...Retrying...")
                        alternate_api(api_count)
                        time.sleep(2**attempt)
                    else:
                        raise e
        


# endregion

# region ### COMMANDS ###

# region ### GENERATE PDF ###


def convert_html_to_pdf(reasoning, command_string, command_argument, current_task, self_prompt_action):
    try:
        # Extract content between triple backticks
        content_match = re.search(r'```(.*?)```', command_argument, re.DOTALL)
        if not content_match:
            return create_json_message(
                "Error: Couldn't find content between triple backticks",
                command_string,
                command_argument,
                current_task,
                "Google Error",
            )

        content = content_match.group(1).strip()

        # Parse the input string to extract the filename and content
        parts = command_argument.split("Content:")
        filename_part = parts[0].strip()
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
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            self_prompt_action,
            
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
        self_prompt_action,
        
    )


# endregion

#region ### WINDOWS COMMANDS ###

def run_win_shell_command(
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            self_prompt_action,
            
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
        self_prompt_action,
        
    )

#endregion

# region ### ALLOWS MODEL TO CONTINUE ###


def no_command(
    reasoning, command_string, command_argument, current_task, self_prompt_action
):
    response_string = json.dumps(command_argument)
    set_global_success(True)
    debug_log(f"reply String: {response_string}")
    return create_json_message(
        reasoning, command_string, command_argument, current_task, self_prompt_action
    )


# endregion

# region ### SAVE RESEARCH ###


def save_research(reasoning, command_string, command_argument, current_task, self_prompt_action):
    # Get the current datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the research entry with the datetime and content
    research_entry = f"DateTime: {current_time}\nContent: {command_argument.strip()}\n\n"

    # Save the research to a text file
    research_file_path = os.path.join(working_folder, "research.txt")

    try:
        with open(research_file_path, "a") as f:
            f.write(research_entry)
    except FileNotFoundError:
        return create_json_message(
            "Failed to save research, the file doesn't exist.",
            command_string,
            command_argument,
            current_task,
            self_prompt_action,
        )

    return create_json_message(
        "Research saved successfully",
        command_string,
        command_argument,
        current_task,
        self_prompt_action,
    )
# endregion

# region ### FETCH RESEARCH ###


def fetch_research(reasoning, command_string, command_argument, current_task, self_prompt_action):
    # Fetch the research.txt file from the working_folder
    research_file_path = os.path.join(working_folder, "research.txt")

    try:
        with open(research_file_path, "r") as f:
            formatted_research = f.read()
    except FileNotFoundError:
        return create_json_message(
            "Failed to fetch research data, the file doesn't exist.",
            command_string,
            command_argument,
            current_task,
            self_prompt_action,
        )
        
    return create_json_message(
        formatted_research,
        command_string,
        command_argument,
        current_task,
        self_prompt_action,
    )
# endregion

# region ### CREATE TASK LIST ###
# W Writes the task list to bots 2nd message so he always remembers


def create_task_list(
    reasoning, command_string, command_argument, current_task, self_prompt_action
):
    if command_argument is not None:
        message_handler(None, command_argument, "task")
    return create_json_message(
        "Task List Saved Successfully",
        command_string,
        command_argument,
        current_task,
        self_prompt_action,
        
    )


# endregion

# region ### CREATE PYTHON SCRIPT ###

def create_python_script(
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            f"Python code created and saved successfully: Filename: {filename}",
            command_string,
            command_argument,
            current_task,
            self_prompt_action,
            
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
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            self_prompt_action,
            
        )

    except Exception as e:
        set_global_success(False)
        debug_log(f"Error: {str(e)}")
        return create_json_message(
            f"Error: {str(e)}",
            command_string,
            command_argument,
            "Retry or Reserch Current Task",
            self_prompt_action,
            
        )


# endregion

# region ## APPEND CONTENT TO FILE ##

def append_content_to_existing_file(
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            self_prompt_action,
            
        )
    except Exception as e:
        set_global_success(False)
        debug_log(f"Error: {str(e)}")
        return create_json_message(
            f"Error: {str(e)}",
            command_string,
            command_argument,
            "Retry or Reserch Current Task",
            self_prompt_action,
            
        )


# endregion

# region ### READ CONTENT FROM FILE ###


def read_content_from_file(
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            self_prompt_action,
            
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
def download_file(reasoning, command_string, command_argument, current_task, self_prompt_action):
    if not os.path.exists(working_folder):
        os.makedirs(working_folder)

    try:
        filename = command_argument.split("/")[-1]
        output_path = os.path.join(working_folder, filename)
        command_list = ["curl", "-o", output_path, command_argument]

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
            self_prompt_action,
            
        )
        else:
            return create_json_message(
            "Error downloading file",
            command_string,
            command_argument,
            current_task,
            self_prompt_action,
            
        )

    except subprocess.CalledProcessError as e:
        return create_json_message(
            f"Error: {e}",
            command_string,
            command_argument,
            current_task,
            self_prompt_action,
            
        )

#endregion        

# region ### SEARCH GOOGLE ###


def search_google(
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
            self_prompt_action,
            
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


def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Add the tags you want to extract text from in the list below
    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'ul', 'li']

    extracted_text = []
    for tag in allowed_tags:
        elements = soup.find_all(tag)
        for element in elements:
            extracted_text.append(element.get_text())

    return ' '.join(extracted_text)


def browse_website_url(reasoning, command_string, command_argument, current_task, self_prompt_action):
    def run(playwright):
        browser = playwright.chromium.launch()
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()

        page.goto(command_argument)
        html_content = page.content()

        browser.close()
        return html_content

    try:
        with sync_playwright() as playwright:
            result = run(playwright)
    except Exception as e:
        return create_json_message(
            f"Error: {str(e)}",
            command_string,
            command_argument,
            current_task,
            self_prompt_action,
        )

    extracted_text = extract_text(result)
    sanitized_text = sanitize_content(extracted_text)

    # type: ignore
    if max_characters is not None and len(sanitized_text) > max_characters:
        sanitized_text = sanitized_text[:max_characters]

        debug_log(sanitized_text)

    return create_json_message(
        "Website Content: " + sanitized_text,  # type: ignore
        command_string,
        command_argument,
        current_task,
        self_prompt_action,
    )


# endregion

# region ### MISSION ACCOMPLISHED ###


def mission_accomplished(
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
        while len(message_history) > max_conversation + 1: #type: ignore
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
    reasoning, command_string, command_argument, current_task, self_prompt_action
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
        reasoning, command_string, command_argument, current_task, self_prompt_action
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
        (reasoning, command_string, command_argument, current_task, self_prompt_action) = query_bot(messages)      

        
        print(colored("LordGPT Thoughts: ", color="green"), end="")
        typing_print(str(reasoning))
        print(colored("Currently :       ", color="blue"), end="")
        typing_print(str(current_task) + "")
        print(colored("Next Task:        ", color="magenta"), end="")
        typing_print(str(self_prompt_action) + "")
        print(colored("Executing CMD:    ", color="red"), end="")
        typing_print(str(command_string))
        print(colored("CMD Argument:     ", color="red"), end="")
        typing_print(str(command_argument) + "\n\n")
        handler_response = command_handler(
            reasoning, command_string, command_argument, current_task, self_prompt_action
        ) 

        if success == True:

            return handler_response
        return handler_response


# endregion

# region ### MAIN ###


def main_loop():

    print(colored("Tips: ", "green"))


    print(
        colored(
            "1. GPT3.5 & GPT4 Full Support!" +
            "\n2. Example Goal: Provide a 5 day weather forecast for my location using the weather.gov API and save it to a PDF" +
            "\n3. Report Issues: https://github.com/Cytranics/LordGPT/issues"
            "\n4. Discord: https://discord.gg/2jT32cM8", "yellow",
        )
)

    user_goal = input("Goal: ")
    print(colored("Creating detailed plan to achive the goal....", "green"))
    if not user_goal:
        user_goal = "Provide a 5 day weather forecast for my location using the weather.gov API and save it to a PDF"
        print(colored("Goal: " + user_goal, "green"))
    set_global_success(True)

    bot_send = openai_bot_handler(bot_prompt + user_goal, f"""{{"reasoning_80_words": "Respond with your detailed task list for the goal using using the required json format", "command_string": "[COMMAND]", "command_argument": "[ARGUMENT]", "current_task": "[CURRENT TASK]", "self_prompt_action": "[SUGGESTED NEXT TASK]"}}""", "assistant")


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