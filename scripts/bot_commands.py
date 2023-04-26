botcommands = [
    {
        "command_string": "create_task_list",
        "command_argument": "[TASKLIST]",
        "command_description": "Replace [TASKLIST] with your detailed numbered task list containg subtasks to acheive the goal."
    },

    {
        "command_string": "download_file",
        "command_argument": "url",
        "command_description": "Download file's from from a url using curl."
    },
    {
        "command_string": "create_pdf_from_html_markup",
        "command_argument": "Filename: [FILENAME] Content: [CONTENT]",
        "command_description": "Create PDF's by replacing [CONTENT] with formatted HTML."
    },
    {
        "command_string": "create_python_script",
        "command_argument": "Filename: [FILENAME] Content: ```[SCRIPT]```",
        "command_description": "Write and save a non-interactive formatted python script as a multiline string using triple backticks (```) and new lines. Replace '[FILENAME]' with filename.py and '[SCRIPT]' with the valid inner python script."
    },
    {
        "command_string": "write_new_content_to_file",
        "command_argument": "Filename: [FILENAME] Content: ```[CONTENT]```",
        "command_description": "Write and save formatted text content to a single file as a multiline string using triple backticks (```). Replace '[FILENAME]' with the desired filename and '[CONTENT]'"
    },
    {
        "command_string": "append_content_to_existing_file",
        "command_argument": "Filename: [FILENAME] Content: ```[CONTENT]```",
        "command_description": "Append formatted content or formatted code to an existing file as a multiline string using triple backticks (```).. Replace '[FILENAME]' with the desired filename and '[CONTENT]'"
    },
    {
        "command_string": "read_content_from_file",
        "command_argument": "Filename: [FILENAME]",
        "command_description": "Reads formatted content from existing file."
    },
    {
        "command_string": "search_google",
        "command_argument": "[DETAILED QUERY]|[PAGENUMBER]",
        "command_description": "Provides a list of url's for scraping or browsing."
    },
    {
        "command_string": "scrape_website_url",
        "command_argument": "https://url|raw_html|max_length=#",
        "command_description": "Scrape text or html based on raw_html variable. url|raw_html|character_return_length=number Example: https://example.com|false|character_return_length=3000"
    },
    {
        "command_string": "save_research",
        "command_argument": "Title: [CONTENT] ResearchContent: [CONTENT]",
        "command_description": "Saves data gathered from the internet and through research. Format argument as Title: '[CONTENT]' ResearchContent: '[CONTENT]'"
    },
    {
        "command_string": "fetch_research",
        "command_argument": "Title: [CONTENT] ResearchContent: [CONTENT]",
        "command_description": "Fetch all research data to use in PDF report."
    },
    {
        "command_string": "run_bash_shell_command",
        "command_argument": "[BASH COMMAND]",
        "command_description": "Execute non-interactive bash commands or python scripts to fully manage the system you are on. Pass the BASH COMMAND as a command_argument, determine if you are on linux."
    },
    {
        "command_string": "run_win_shell_command",
        "command_argument": "[WIN COMMAND]",
        "command_description": "Execute non-interactive windows commands or python scripts to fully manage the system you are on. Pass the WIN COMMAND as a command_argument, determine if you are on windows."
    },
    {
        "command_string": "mission_accomplished",
        "command_argument": "Mission accomplishment message",
        "command_description": "Use this command only after the entire goal has been verified and completed 100%."
    },
]


