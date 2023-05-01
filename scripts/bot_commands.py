botcommands = [
    {
        "command_string": "create_task_list",
        "command_argument": "```[CONTENT]```",
        "command_description": "Used to create initial tasklist regenerate list with completed items. [CONTENT] must be the entire task list."
    },
    {
        "command_string": "create_pdf_from_html",
        "command_argument": "[FILENAME.pdf]|[HTML-TEMPLATE.html]",
        "command_description": "Used to generate PDF reports from an html file. HTML template must have complete data and no variables."
    },
    {
        "command_string": "file_operations",
        "command_argument": "filename.ext|```[CONTENT]```|operationtype",
        "command_description": "Used for all file operations, 'write', 'read', 'append', 'rename', 'move', 'delete'. For file rename and move operations, the content needs be the new name or destination path, respectively."
    },
    {
        "command_string": "search_engine",
        "command_argument": "[DETAILED SEARCH QUERY]",
        "command_description": "Search Engine Provides a list of url's for scraping or browsing."
    },
    {
        "command_string": "browse_website_url",
        "command_argument": "[URL]",
        "command_description": "Browse a single url."
    },
    {
        "command_string": "save_research",
        "command_argument": "[TITLE]|```[CONTENT]```",
        "command_description": "Saves data gathered from internet research."
    },
    {
        "command_string": "fetch_research",
        "command_argument": "",
        "command_description": "Fetch all research data to use in PDF report."
    },
    {
        "command_string": "run_shell_command",
        "command_argument": "[SHELLCOMMAND]",
        "command_description": "First determine which OS you are on, then send non interactive shell commands. Use Curl to download a non html file. Location Lookup: curl ifconfig.co/json"
    },
    {
        "command_string": "mission_accomplished",
        "command_argument": "Mission accomplishment message",
        "command_description": "This command is unavailable until all task items have been marked as completed."
    },
]