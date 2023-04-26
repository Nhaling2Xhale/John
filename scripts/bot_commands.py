botcommands = [
    {
        "command_string": "create_task_list",
        "command_argument": "[CONTENT]",
        "command_description": "Your first command should be to create the task list. Replace '[CONTENT]' with the string content."
    },
    {
        "command_string": "no_command",
        "command_argument": "None",
        "command_description": "Used when you do not need to use a command"
    },
    {
        "command_string": "download_file",
        "command_argument": "url",
        "command_description": "Used to download a file or PDF other than html from a URL. Replace 'url' with the url and filename"
    },
    {
        "command_string": "create_pdf_from_html_markup",
        "command_argument": "Filename: [FILENAME] Content: [CONTENT]",
        "command_description": "Create PDF's by sending formatted HTML as the content along with any research data."
    },
    {
        "command_string": "create_python_script",
        "command_argument": "Filename: [FILENAME] Content: [CONTENT]",
        "command_description": "Write and save a formatted python script that does not require an API key to execute. Replace '[FILENAME]' with the desired filename and '[CONTENT]' with the formatted python script as a multiline string using triple backticks (```)."
    },
    {
        "command_string": "write_new_content_to_file",
        "command_argument": "Filename: [FILENAME] Content: [CONTENT]",
        "command_description": "Write and save formatted text content to a single file. Replace '[FILENAME]' with the desired filename and '[CONTENT]' with the content sent as a multiline string using triple backticks (```)."
    },
    {
        "command_string": "append_content_to_existing_file",
        "command_argument": "Filename: [FILENAME] Content: [CONTENT]",
        "command_description": "Append formatted content or formatted code to an existing file. Replace '[FILENAME]' with the desired filename and '[CONTENT]' with the file content sent as a multiline string using triple backticks (```)."
    },
    {
        "command_string": "read_content_from_file",
        "command_argument": "Filename: [FILENAME]",
        "command_description": "Reads formatted content from existing file."
    },
    {
        "command_string": "search_google",
        "command_argument": "[DETAILED QUERY]|[PAGENUMBER]",
        "command_description": "Creates a list of url's and snippets by passing a query and page number."
    },
    {
        "command_string": "scrape_website_url",
        "command_argument": "https://url|raw_html|max_length=#",
        "command_description": "Used to scrape the contents of a website with http or https. Use wget cmd for file ext. Example: https://example.com|raw_html|max_length=500"
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


