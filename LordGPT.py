# region ### IMPORTS ###
# Standard library imports
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
import traceback
import asyncio
from time import sleep
from typing import Dict

# Third-party imports
import requests
from requests.exceptions import ReadTimeout
from dotenv import load_dotenv
from termcolor import colored
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from unidecode import unidecode
from yaspin import yaspin
from serpapi import GoogleSearch
import pdfkit
import urllib.request
from playwright.sync_api import sync_playwright

# Local file imports
from scripts.bot_prompts import command_list, bot_prompt
from scripts.bot_commands import botcommands
# endregion


def log_exception(exc_type, exc_value, exc_traceback):
    with open("exceptions.log", "a") as f:
        f.write("\n\n" + "=" * 80 + "\n")
        f.write(f"Exception Timestamp: {datetime.datetime.now()}\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)


sys.excepthook = log_exception


current_path = os.getcwd()
working_folder = os.path.join(current_path, 'LordGPT_folder')
if not os.path.exists(working_folder):
    os.makedirs(working_folder)

# region GLOBAL VARIABLES
config_file = "config.json"
current_version = "1.6"
update_url = "https://thelordg.com/downloads/version.txt"
changelog_url = "https://thelordg.com/downloads/changelog.txt"
download_link = "https://thelordg.com/downloads/LordGPT.exe"
message_history = []
global api_type
# endregion

# region GLOBAL FUNCTIONS
def debug_log(message, value=None):
    global current_datetime
    if debug_code:
        # Create the debug.txt file path
        debug_file_path = os.path.join(working_folder, "debug.txt")

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write the message and value to the debug.txt file
        # Add the encoding parameter here
        with open(debug_file_path, "a", encoding="utf-8") as debug_file:
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
        "OPENAI API key:https://platform.openai.com/account/api-keys - Come to our discord and message Cytranic to borrow a key:  "
    )
    search_engine_choice = input(
        "Which search engine do you want to use? (1: Google, 2: SERP): ")

    if search_engine_choice == "1":
        google_api_key = input("Please enter your Google API key: ")
        google_search_id = input("Please enter your Google Search ID: ")
        search_engine_mode = "GOOGLE"
        serp_api_key = None

    elif search_engine_choice == "2":
        serp_api_key = input("Please enter your SERP API key: ")
        search_engine_mode = "SERP"
        google_api_key = None
        google_search_id = None
    else:
        print("Invalid choice. Please choose either '1' for Google or '2' for SERP.")

    model = ""
    while model not in ["gpt-3.5-turbo", "gpt-4"]:
        print("Please select a model:")
        print("1. GPT-3.5")
        print("2. GPT-4")
        model_choice = input(
            "Choose the number of the model you have access to: ")

        if model_choice == "1":
            model = "gpt-3.5-turbo"
        elif model_choice == "2":
            model = "gpt-4"
        else:
            print("Invalid selection. Please enter 1 or 2.")

    debug_code = int(input(
        "Enable debug.txt in working folder? (1 for Enable, 2 for Disable): ")) == 1

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
        'SEARCH_ENGINE_MODE': search_engine_mode,
        'GOOGLE_API_KEY': google_api_key,
        'CUSTOM_SEARCH_ENGINE_ID': google_search_id,
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
search_engine_mode = get_variable(env_data, "SEARCH_ENGINE_MODE", "GOOGLE")
serp_api_key = get_variable(env_data, "SERP_API", None)
google_api_key = get_variable(env_data, "GOOGLE_API_KEY", None)
google_search_id = get_variable(env_data, "CUSTOM_SEARCH_ENGINE_ID", None)


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


def print_bot_response(reasoning, command_string, command_argument, current_task, self_prompt_action):
    print(colored("LordGPT Thoughts: ", color="yellow"), end="")
    typing_print(str(reasoning))
    print(colored("Currently :       ", color="green"), end="")
    typing_print(str(current_task) + "")
    print(colored("Next Task:        ", color="blue"), end="")
    typing_print(str(self_prompt_action) + "")
    print(colored("Executing CMD:    ", color="red"), end="")
    typing_print(str(command_string))
    print(colored("CMD Argument:     ", color="red"), end="")
    typing_print(str(command_argument) + "\n\n")
    return


def remove_brackets(text):
    return re.sub(r'\[|\]', '', text)


# Create JSON message function
def create_json_message(
    reasoning_80_words="[DETAILED REASONING]",
    command_string="[COMMAND]",
    command_argument="[ARGUMENT]",
    current_task="[CURRENT TASK]",
    self_prompt_action="[SELF PROMPT NEXT ACTION]",
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

# region ### TEXT PARSER ###


def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4',
                    'h5', 'h6', 'a', 'span', 'ul', 'li']

    extracted_text = []
    for tag in allowed_tags:
        elements = soup.find_all(tag)
        for element in elements:
            extracted_text.append(element.get_text())

    cleaned_text = re.sub(r'\n|["\']', '', ' '.join(extracted_text))

    # Remove spaces greater than 2
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)

    return cleaned_text

# endregion

# region ### API QUERY ###
text_color_dict = {
    "Questing with LordGPT............": "light_blue",
    "Hi, I'm autoGPT and I will generate a file..Hi, I'm autoGPT and I will generate a file...Hi, I'm autoGPT and I will generate a file..Hi, I'm autoGPT and I will generate a file.Hi, I'm autoGPT and I will generate a file.": "light_blue",
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
    time.sleep(api_throttle)  # type: ignore
    alternate_api(api_count)

    with yaspin(text=random_text, color=random_color) as spinner:
        for attempt in range(retries):  # type: ignore
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

                # BD PROXY REQUEST
                if bd_enabled:
                    try:
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
                            api_url, data=json_utf8, headers=headers)
                        # BRIGHT DATA REQUEST
                        request = opener.open(req, timeout=api_timeout)
                        uresponse = request.read()
                        utfresponse = uresponse.decode('utf-8')
                        botresponse = json.loads(utfresponse)
                        response_json = botresponse
                        debug_log("Bot reply: ", botresponse)

                    except Exception as e:
                        if attempt < retries - 1:  # type: ignore
                            print(f"Error occurred: {str(e)}...Retrying...")

                            time.sleep(2 ** attempt)
                else:
                    # STANDARD API REQUEST

                    if not bd_enabled:
                        try:
                            botresponse = requests.request(
                                "POST", api_url, headers=headers, data=json_payload, timeout=api_timeout)  # type: ignore
                            response_json = botresponse.json()
                        except ReadTimeout as e:
                            if attempt < retries - 1:  # type: ignore
                                print(
                                    f"ReadTimeout Error occurred: {str(e)}...Retrying...")
                                time.sleep(2 ** attempt)
                                continue
                            else:
                                return (
                                    "Error: API Timeout Error",
                                    " ",
                                    " ",
                                    "Starting with the first uncompleted task in the task list",
                                    "I will pickup where I left off and continue with the first uncompleted task"
                                )
                        except Exception as e:
                            print(f"Error occurred: {str(e)}")
                            return (
                                "Unknown API Error: Resend response in the correct json format",
                                " ",
                                " ",
                                "Starting with the first uncompleted task in the task list",
                                "I will respond using the required json format and continue with the first uncompleted task"
                            )

                debug_log("Bot reply: ", botresponse)
                # Handling error response
                if "error" in response_json:
                    error_message = response_json["error"]["message"]
                    print(f"Error: {error_message}")

                    return (
                        f"API error {error_message}",
                        " ",
                        " ",
                        "Starting with the first uncompleted task in the task list",
                        "I will respond using the required json format and continue with the first uncompleted task"
                    )

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
                        reasoning = responseformatted["reasoning_80_words"]
                        command_string = responseformatted["command_string"]
                        command_argument = responseformatted["command_argument"]
                        current_task = responseformatted["current_task"]
                        self_prompt_action = responseformatted["self_prompt_action"]

                        return (
                            reasoning,
                            command_string,
                            command_argument,
                            current_task,
                            self_prompt_action,
                        )

                    else:

                        return (
                            "Invalid JSON Format, please use the correct format.",
                            " ",
                            " ",
                            "Starting with the first uncompleted task in the task list",
                            "I will always respond using the required json format and continue with the first uncompleted task"
                        )

            except Exception as e:
                if attempt < retries - 1:  # type: ignore
                    print(
                        f"API Timeout, increase your timeout: {str(e)}...Retrying...")

                    time.sleep(2**attempt)
                else:
                    print("API Retries reached, insert another coin and try again...")
                    exit


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
                "I need to replace the entire ```[HTML MARKUP]``` with an actual HTML string formatted with backtiks.",
            )

        content = content_match.group(1).strip()

        # Check if content is [HTML MARKUP]
        if content.lower() == "```[HTML MARKUP]```":
            return create_json_message(
                "Error: Invalid Content. You must replace ```[HTML MARKUP]``` with the HTML string formatted with backtiks.",
                command_string,
                command_argument,
                current_task,
                "I need to replace the entire ```[HTML MARKUP]``` with an actual HTML string formatted with backtiks.",
            )

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
            "If success, Regenerate task list with task: " + current_task + " completed.",
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

def run_shell_command(
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

    debug_log("Shell response: ", shell_response)
    return create_json_message(
        "BASH Command Output: " + shell_response,
        command_string,
        command_argument,
        current_task,
        "If success, Regenerate task list and mark task " + current_task + " completed.",

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
        "If success, Regenerate task list and mark task " + current_task + " completed.",
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
    research_data = json.dumps(formatted_research)
    return create_json_message(
        research_data,
        command_string,
        command_argument,
        current_task,
        "If success, Regenerate task list and mark task " + current_task + " completed.",
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
        "Double check task list to ensure its detailed enough so only one command is issued per item.",

    )


# endregion

# region ### FILE OPERATION ###
def file_operations(reasoning, command_string, command_argument, current_task, self_prompt_action):
    try:
        # Use regex to split the command_argument
        match = re.match(r'([^|]+)\|(```[\s\S]*?```)\|(.+)', command_argument)
        if not match:
            return create_json_message("Error: Every argument must contain this format:(filename|```content```|operation) The filename is the name of the file you want to operate on. The content needs to be formatted text or formatted code as a multiline string using triple backticks (```). For file rename and move operations, the content needs be the new name or destination path, respectively. The following file operations are valid: 'write', 'read', 'append', 'rename', 'move', 'delete'. Read files to verify.", command_string, command_argument, current_task, "Retry using a valid file_operation format and operation")

        filename, content, operation = match.groups()
        content = content.strip("```")
        file_path = os.path.join(working_folder, filename)
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
                destination_path = os.path.join(
                    working_folder, destination_path)
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
                  current_task + "Complete: Regenerate task list with item completed and add the filename to the tasklist.")
        return create_json_message(operation_cleaned, command_string, command_argument, operation_cleaned, "If success, Regenerate task list and mark task " + current_task + " completed.")
    except ValueError:
        debug_log("File Operation Error : " + reasoning + command_string + command_argument +
                  current_task + self_prompt_action)
        return create_json_message("Error: Every argument must contain this format:(filename|```content```|operation) The filename is the name of the file you want to operate on. The content needs to be formatted text or formatted code as a multiline string using triple backticks (```). For file rename and move operations, the content needs be the new name or destination path, respectively. The following file operations are valid: 'write', 'read', 'append', 'rename', 'move', 'delete'. Read files to verify.", command_string, command_argument, current_task, "Retry using a valid file_operation format and operation")

# endregion

# region ### SEARCH ENGINE ###


# GOOGLE API
if search_engine_mode == "GOOGLE":
    def search_engine(
        reasoning, command_string, command_argument, current_task, self_prompt_action
    ):
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": google_api_key,
                "cx": google_search_id,
                "q": command_argument,
                "safe": "off",
                "num": 10,
            }

            google_response = requests.get(url, params=params)
            data = google_response.json()

            results = []
            if "items" in data:
                for item in data["items"]:
                    results.append(
                        {"title": item["title"], "link": item["link"]})
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
                formatted_results += f"Title: {result['title']}"
                formatted_results += f"Link: {result['link']}"

            searchresults = json.dumps(
                formatted_results.replace('\n', '').replace('\\n', ''))

            debug_log("Google Search: ", searchresults)
            set_global_success(True)
            # GOOGLE IMAGE RESULTS RETURNED
            return create_json_message(
                "Search Results: " + searchresults,  # type: ignore
                command_string,
                command_argument,
                current_task,
                "If success, Regenerate task list and mark task " + current_task + " completed."
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

# SERP API
elif search_engine_mode == "SERP":

    def search_engine(reasoning, command_string, command_argument, current_task, self_prompt_action):
        params = {
            "api_key": serp_api_key,
            "engine": "duckduckgo",
            "q": command_argument,
            "kl": "us-en",
            "safe": "-2",
            "num": 5
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        formatted_results = []

        loop_limit = 5

        for index, result in enumerate(results["organic_results"], start=1):
            if index <= loop_limit:
                title = result['title'].replace('\n', '').replace('\n', '')
                link = result['link'].replace('\n', '').replace('\n', '')
                formatted_results.append(
                    {"index": index, "title": title, "link": link})

        if not formatted_results:
            debug_log("SERP Error: ", formatted_results)
            return create_json_message(
                "Error: Search Error, try another search term.",
                command_string,
                command_argument,
                current_task,
                "Retry or choose another search term."
            )

        sanitized_results = json.dumps(formatted_results)
        debug_log("SERP Sanitized: ", sanitized_results)
        return create_json_message(
            "Search Results: " + sanitized_results,
            command_string,
            command_argument,
            current_task,
            "If success, Regenerate task list and mark task " + current_task + " completed."
        )


# endregion

# region ### BROWSE WEBSITE ###

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

    extracted_text = result

    # Keep only A-Z, a-z, and spaces
    extracted_text = re.sub(r'[^A-Za-z\s]', '', extracted_text)

    # Initialize sanitized_text to extracted_text
    sanitized_text = json.dumps(extracted_text)

    # type: ignore
    if max_characters is not None and len(extracted_text) > max_characters:
        sanitized_text = extracted_text[:max_characters]

        debug_log("Browse URL: ", sanitized_text)

    return create_json_message(
        "Website Content: " + sanitized_text,  # type: ignore
        "command_string",
        command_argument,
        current_task,
        "If success, Regenerate task list and mark task " + current_task + " completed.",
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
        while len(message_history) > max_conversation + 1:  # type: ignore
            message_history.pop(2)

    if len(message_history) == 0:
        message_history.insert(
            0, {"role": "system", "content": current_prompt})
    elif role == "system":
        message_history[0] = {"role": "system", "content": current_prompt}

    if message is not None:
        if role == "task":
            message_history.pop(1)
            message_history.insert(
                1, {"role": "assistant", "content": message})
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
        return create_json_message("The command_string " + command_string + " is not a valid command string.", command_string, command_argument, current_task, "Double check the command string and format")
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
# endregion


def openai_bot_handler(current_prompt, message, role):

    messages = message_handler(current_prompt, message, role)
    (reasoning, command_string, command_argument,
     current_task, self_prompt_action) = query_bot(messages)

    print(colored("LordGPT Thoughts: ", color="yellow"), end="")
    typing_print(str(reasoning))
    print(colored("Currently :       ", color="green"), end="")
    typing_print(str(current_task) + "")
    print(colored("Next Task:        ", color="blue"), end="")
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
    debug_file = os.path.join(working_folder, "debug.txt")

    if os.path.exists(research_file):
        os.remove(research_file)

    if os.path.exists(debug_file):
        os.remove(debug_file)

    print(colored("Tips: ", "green"))

    print(
        colored(
            "1. GPT-4 Works the best. GPT-3.5 has issues with hallucinations, but it does work most of the time." +
            "\n2. Example Goal: Determine my location, gather the 5 day forecast from the weather.gov website for my location, generate a professional looking PDF with the 5 day forecast." +
            "\n3. Report Issues: https://github.com/Cytranics/LordGPT/issues"
            "\n4. Discord: https://discord.gg/2jT32cM8", "yellow",
        )
    )

    user_goal = input("Goal: ")
    print(colored("Creating detailed plan to achive the goal....", "green"))
    if not user_goal:
        user_goal = "Determine my location, gather the 5 day forecast from the weather.gov website for my location, generate a professional looking PDF with the 5 day forecast."
        print(colored("Goal: " + user_goal, "green"))
    set_global_success(True)
    alternate_api(api_count)
    bot_send = openai_bot_handler(
        bot_prompt + user_goal, f"""{{"reasoning_80_words": "Respond with your detailed formatted task list for the goal by replacing [TASKLIST]", "command_string": "[COMMAND]", "command_argument": "[ARGUMENT]", "current_task": "[CURRENT TASK]", "self_prompt_action": "[SELF PROMPT NEXT ACTION]"}}""", "assistant")

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

        continue_choice = input(
            "Is LordG on the right track If not, select n? (y/n): ").lower()
        if continue_choice == "n":
            new_direction = input("Correct LordGPT: ")
            openai_bot_handler(
                bot_prompt, f"""{{"reasoning_80_words": "{new_direction}", "command_string": "[COMMAND]", "command_argument": "[ARGUMENT]", "current_task": "[CURRENT TASK]", "self_prompt_action": "Regenerate a new task list based on the direction given"}}""", "user")
            break


if __name__ == "__main__":
    bbs_ascii_lordgpt()
    main_loop()


# endregion
