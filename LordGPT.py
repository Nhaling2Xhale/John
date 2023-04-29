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
import shutil
import requests.exceptions
from time import sleep
from typing import Dict
import debugpy
debugpy.listen(('0.0.0.0', 5678))

from dotenv import load_dotenv
from termcolor import colored
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from unidecode import unidecode
from yaspin import yaspin
from serpapi import GoogleSearch
from datetime import datetime

import pdfkit
import urllib.request

from scripts.bot_prompts import command_list, bot_prompt
from scripts.bot_commands import botcommands
from playwright.sync_api import sync_playwright
#endregion
import traceback


def log_exception(exc_type, exc_value, exc_traceback):
    with open("exceptions.log", "a") as f:
        f.write("\n\n" + "=" * 80 + "\n")
        f.write(f"Exception Timestamp: {datetime.now()}\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)


sys.excepthook = log_exception



current_path = os.getcwd()
working_folder = os.path.join(current_path, 'LordGPT_folder')
if not os.path.exists(working_folder):
    os.makedirs(working_folder)

# region GLOBAL VARIABLES
config_file = "config.json"
current_version = "1.3"
update_url = "https://thelordg.com/downloads/version.txt"
changelog_url = "https://thelordg.com/downloads/changelog.txt"
download_link = "https://thelordg.com/downloads/LordGPT.exe"
message_history = []
# endregion


# region GLOBAL FUNCTIONS
def debug_log(message, value=None):
    global current_datetime
    if debug_code:
        # Create the debug.txt file path
        debug_file_path = os.path.join(working_folder, "debug.txt")

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write the message and value to the debug.txt file
        with open(debug_file_path, "a") as debug_file:
            debug_file.write(f"[{current_datetime}] {message}{value}\n\n")


    
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
    api_key = input(
        "OPENAI API key:https://platform.openai.com/account/api-keys - Come to Discord for free GPT4 key:  ")
    serp_api_key = input("SERPAPI: https://serpapi.com - Come to Discord for free key: ")

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
        'DEBUG_CODE': debug_code,
        'FREQUENCY_PENALTY': 0.0,
        'MAX_CONVERSATION': 5,
        'MAX_TOKENS': 800,
        'OPENAI_API_KEY': api_key,
        'OPENAI_MODEL_NAME': model,
        'OPENAI_URL': "https://api.openai.com/v1/chat/completions",
        'PRESENCE_PENALTY': 0.0,
        'SERP_API': serp_api_key,
        'TEMPERATURE': 0.2,
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
bd_username = get_variable(env_data, "BD_USERNAME", None)
debug_code = True
frequency_penalty = get_variable(env_data, "FREQUENCY_PENALTY", 0.0, "float")
max_characters = get_variable(env_data, "MAX_CHARACTERS", 1000, "int")
max_conversation = get_variable(env_data, "MAX_CONVERSATION", 5, "int")
max_tokens = get_variable(env_data, "MAX_TOKENS", 800, "int")
presence_penalty = get_variable(env_data, "PRESENCE_PENALTY", 0.0, "float")
temperature = get_variable(env_data, "TEMPERATURE", 0.8, "float")
top_p = get_variable(env_data, "TOP_P", 0.0, "float")
serp_api_key = get_variable(env_data, "SERP_API", None)


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
            debug_log("API Alternate Type : ", api_type)
        else:
            api_url = get_variable(env_data, "OPENAI_URL")
            api_key = get_variable(env_data, "OPENAI_API_KEY")
            model = get_variable(env_data, "OPENAI_MODEL_NAME")
            api_type = "OPENAI"
            debug_log("API Alternate Type : ", api_type)
    elif api_function == "AZURE":
        api_url = get_variable(env_data, "AZURE_URL")
        api_key = get_variable(env_data, "AZURE_API_KEY")
        model = get_variable(env_data, "AZURE_MODEL_NAME")
        api_type = "AZURE"
        debug_log("API Static Type : ", api_type)
    elif api_function == "OPENAI":
        api_url = get_variable(env_data, "OPENAI_URL")
        api_key = get_variable(env_data, "OPENAI_API_KEY")
        model = get_variable(env_data, "OPENAI_MODEL_NAME")
        api_type = "OPENAI"
        debug_log("API Static Type : ", api_type)
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

#region ### TEXT PARSER ###
import re
from bs4 import BeautifulSoup

def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'ul', 'li']

    extracted_text = []
    for tag in allowed_tags:
        elements = soup.find_all(tag)
        for element in elements:
            extracted_text.append(element.get_text())

    cleaned_text = re.sub(r'\n|["\']', '', ' '.join(extracted_text))

    # Remove spaces greater than 2
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)

    return cleaned_text

#endregion

# region ### API QUERY ###
text_color_dict = {
    "Questing with LordGPT............": "light_blue",
    "Inserting coins for LordGPT......": "light_blue",
    "Restoring LordGPT save files.....": "light_blue",
    "LordGPT speedrunning loading.....": "light_blue",
    "Swapping LordGPT memory cards....": "light_blue",
    "Hunting LordGPT's Easter eggs....": "light_blue",
    "Entering LordGPT's cheat code....": "light_blue",
    "Powering up with LordGPT.........": "light_blue",
    "Recruiting LordGPT's party.......": "light_blue",
    "Crafting gear in LordGPT's realm.": "light_blue",
    "Racing LordGPT to the finish.....": "light_blue",
    "Leveling up with LordGPT.........": "light_blue",
    "Conquering LordGPT's leaderboard.": "light_blue",
    "Achieving LordGPT high scores....": "light_blue",
    "Exploring LordGPT's pixel world..": "light_blue",
    "Unlocking LordGPT's hidden levels": "light_blue",
    "Battling LordGPT's epic bosses...": "light_blue",
    "Diving into LordGPT's pixel sea..": "light_blue",
    "Linking with LordGPT's dimensions": "light_blue",
    "Jamming to LordGPT's retro tunes.": "light_blue"
}

def query_bot(messages, retries=api_retry):
        debug_log(messages)
        random_text, random_color = get_random_text_and_color(text_color_dict)
        alternate_api(api_count)    
        time.sleep(api_throttle) #type: ignore
        
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
                        alternate_api(api_count)
                        
                        continue
                
                    debug_log(response_json)    
                    responseparsed = response_json["choices"][0]["message"]["content"]
                    
                    try:
                        responseformatted = json.loads(responseparsed)
                        debug_log(f"Parsed Choices Node: {responseparsed}")
                        
                    except:
                        alternate_api(api_count)
                        debug_log(
                            f"Formatted non json response: {responseparsed}]")
                        responsebad = create_json_message(
                            responseparsed, "I need to always respond with the required json format", "No Command", "Current Task", "I need to respond in the required json format")
                        responseformatted = json.loads(responsebad)
                    
                    debug_log("API Count: ", api_count)
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


def create_pdf_from_html(reasoning, command_string, command_argument, current_task, self_prompt_action):
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
            and "Folder already exists navigate to folder. " in error.decode("utf-8", errors='replace')
        ):
            set_global_success(True)
            shell_response = (
                "Folder already exists. Try switching to folder. " + command_argument
            )
        else:
            shell_response = f"Error creating folder, research the error: {error.decode('utf-8', errors='replace').strip()}"

    elif "touch" in command_argument:
        if return_code == 0:
            set_global_success(True)
            shell_response = "File created and saved successfully. " + command_argument
        else:
            set_global_success(False)
            shell_response = f"Error creating file, Research the error: {error.decode('utf-8', errors='replace').strip()}"

    else:
        if return_code == 0:
            set_global_success(True)
            # Add slicing to limit output length
            shell_response = (
                "Shell Command Output: "
                + f"{output.decode('utf-8', errors='replace').strip()}"[:max_characters]
            )
        else:
            set_global_success(False)
            # Add slicing to limit error length
            shell_response = f"Shell Command failed, research the error: {error.decode('utf-8', errors='replace').strip()}"[
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
    shell_cleaned = json.dumps(shell_response)
    debug_log(shell_cleaned)
    return create_json_message(
        "Windows Command Output: " + shell_cleaned,
        command_string,
        command_argument,
        "I should analyze the output to ensure success and research any errors",
        self_prompt_action,
        
    )

#endregion

# region ### ALLOWS MODEL TO CONTINUE ###


def self_prompt(
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
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

# region ### FILE OPERATION ###


import os
import shutil

def file_operations(reasoning, command_string, command_argument, current_task, self_prompt_action):
    try:
        filename, content, operation = command_argument.split("|")
        content = content.strip("```")
        file_path = os.path.join(working_folder, filename)
    
        command_string = "file_operations"
        command_argument = operation
        current_task = "File Management"
        self_prompt_action = "Performing " + operation.capitalize()
        operation_result = ""
    
        try:
            if operation == "write":
                with open(file_path, "w") as file:
                    file.write(content)
                operation_result = "File Written Successfully"
            elif operation == "read":
                with open(file_path, "r") as file:
                    read_content = file.read()
                operation_result = "File Content: " + read_content
            elif operation == "append":
                with open(file_path, "a") as file:
                    file.write(content)
                operation_result = "File Content appended successfully"
            elif operation == "rename":
                new_name = content.strip()
                new_path = os.path.join(working_folder, new_name)
                os.rename(file_path, new_path)
                operation_result = "File Renamed: " + new_name
            elif operation == "move":
                destination_path = content.strip()
                destination_path = os.path.join(working_folder, destination_path)
                shutil.move(file_path, destination_path)
                operation_result = "File Moved: " + destination_path
            elif operation == "delete":
                os.remove(file_path)
                operation_result = "File Deleted: " + file_path
            else:
                return create_json_message("Invalid file operation: Every argument must contain this format:(filename|```content```|operation) The filename is the name of the file you want to operate on. The content needs to be formatted text or formatted code as a multiline string using triple backticks (```). For file rename and move operations, the content needs be the new name or destination path, respectively. The following file operations are valid: 'write', 'read', 'append', 'rename', 'move', 'delete'. Read files to verify.", command_string, command_argument, current_task, "Retry using a valid file_operation format and operation")
        except FileNotFoundError:
            debug_log("File Operation Error : Folder does not exist" + command_string + command_argument +
                      current_task + self_prompt_action)
            return create_json_message("Error: Folder does not exist. Please make sure the folder exists before performing file operations.", command_string, command_argument, current_task, "Retry with an existing folder")
    
        operation_cleaned = json.dumps(operation_result)
        debug_log("File Operation : " + operation_cleaned + command_string + command_argument +
                  current_task + self_prompt_action)
        return create_json_message(operation_cleaned, command_string, command_argument, operation_cleaned, "Task Successful")
    except ValueError:
        debug_log("File Operation Error : " + reasoning + command_string + command_argument +
                  current_task + self_prompt_action)
        return create_json_message("Error: Every argument must contain this format:(filename|```content```|operation) The filename is the name of the file you want to operate on. The content needs to be formatted text or formatted code as a multiline string using triple backticks (```). For file rename and move operations, the content needs be the new name or destination path, respectively. The following file operations are valid: 'write', 'read', 'append', 'rename', 'move', 'delete'. Read files to verify.", command_string, command_argument, current_task, "Retry using a valid file_operation format and operation")
    
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

# region ### SEARCH ENGINE ###


def search_engine(reasoning, command_string, command_argument, current_task, self_prompt_action):
    params = {
        "api_key": serp_api_key,
        "engine": "duckduckgo",
        "q": command_argument,
        "kl": "us-en",
        "safe": "-2",
        "num": "5"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    formatted_results = "Organic Results:\n"

    loop_limit = 5

    for index, result in enumerate(results["organic_results"], start=1):
        if index <= loop_limit:
            formatted_results += f"{index}. Title: {result['title']}, Link: {result['link']} "
        else:
            break
    debug_log("Search Engine Raw: ", formatted_results)
    sanitized_results = json.dumps(formatted_results)
    debug_log("Search Enginer Sanitized: ", sanitized_results)
    return create_json_message(
        "Search Results: " + sanitized_results,  # type: ignore
        command_string,
        command_argument,
        current_task,
        self_prompt_action
    )

# endregion

# region ### BROWSE WEBSITE ###

import re

import re

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

    # Keep only A-Z, a-z, and spaces
    extracted_text = re.sub(r'[^A-Za-z\s]', '', extracted_text)

    sanitized_text = extracted_text  # Initialize sanitized_text to extracted_text

    # type: ignore
    if max_characters is not None and len(extracted_text) > max_characters:
        sanitized_text = extracted_text[:max_characters]

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
    function = globals().get(command_string)
    if function is None:
        debug_log(
            "LordGPT Send an invalid command_string : "
            + command_string
            + " is not a valid command_string."
        )
        return create_json_message("The command_string " + command_string + " is not a valid command string.", command_string, command_argument, current_task, self_prompt_action)
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
    research_file = os.path.join(working_folder, "research.txt")

    if os.path.exists(research_file):
        os.remove(research_file)
        print(colored("research.txt file deleted.", "green"))

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
        user_goal = "Browse 10 websites and save the data to a CSV file"
        print(colored("Goal: " + user_goal, "green"))
    set_global_success(True)

    bot_send = openai_bot_handler(bot_prompt + user_goal, f"""{{"reasoning_80_words": "Respond with your detailed formatted task list for the goal by replacing [TASKLIST]", "command_string": "[COMMAND]", "command_argument": "[ARGUMENT]", "current_task": "[CURRENT TASK]", "self_prompt_action": "[SUGGESTED NEXT TASK]"}}""", "assistant")


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
            new_direction = input("Correct LordGPT: ")
            openai_bot_handler(
                bot_prompt, f"""{{"reasoning_80_words": "{new_direction}", "command_string": "[COMMAND]", "command_argument": "[ARGUMENT]", "current_task": "[CURRENT TASK]", "self_prompt_action": "[SUGGESTED NEXT TASK]"}}""", "user")
            break
    


if __name__ == "__main__":
    bbs_ascii_lordgpt()
    main_loop()


# endregion