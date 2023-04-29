botcommands = [
    {
        "command_string": "create_task_list",
        "command_argument": "'[TASKLIST]'",
        "command_description": "Used to create initial tasklist and complete each task item. Replace '[TASKLIST]' with your initial task list, or regenereate task list with completed items."
    },
    {
        "command_string": "create_pdf_from_html",
        "command_argument": "Filename: [FILENAME] Content: ```[HTML MARKUP]```",
        "command_description": "Create PDF's from HTML by replacing [FILENAME] with the PDF name, and [HTML MARKUP] as a multiline string using triple backticks (```)."
    },
    {
        "command_string": "file_operations",
        "command_argument": "filename|```content```|operation",
        "command_description": "Used for all file operations, Every argument is required to conform to this format:(filename|```content```|operation) Filename is the name of file with ext. Content is a multiline string using triple backticks (```). For file rename and move operations, the content needs be the new name or destination path, respectively. The following file operations are valid: 'write', 'read', 'append', 'rename', 'move', 'delete'. Read files to verify."
    },
    {
        "command_string": "search_engine",
        "command_argument": "[SEARCH QUERY]|[PAGENUMBER]",
        "command_description": "Search Enginer Provides a list of url's for scraping or browsing."
    },
    {
        "command_string": "browse_website_url",
        "command_argument": "[URL]",
        "command_description": "Browse a single url."
    },
    {
        "command_string": "save_research",
        "command_argument": "Title: [CONTENT] ResearchContent: [CONTENT]",
        "command_description": "Saves data gathered from the internet and through research. Format argument as Title: '[CONTENT]' ResearchContent: '[CONTENT]'"
    },
    {
        "command_string": "fetch_research",
        "command_argument": "",
        "command_description": "Fetch all research data to use in PDF report."
    },
    {
        "command_string": "run_bash_shell_command",
        "command_argument": "[BASH COMMAND]",
        "command_description": "Execute non-interactive bash command. Use Curl to download a non html file. Location Lookup: curl ifconfig.co/json"
    },
    {
        "command_string": "run_win_shell_command",
        "command_argument": "[WIN COMMAND]",
        "command_description": "Execute non-interactive windows command. Use Curl to download a non html file. Location Lookup: curl ifconfig.co/json"
    },
    {
        "command_string": "mission_accomplished",
        "command_argument": "Mission accomplishment message",
        "command_description": "This command is unavailable until all task items have been marked as completed."
    },
]