UPDATE 5-1-2023
- New Debug code, Removed all old debug code.
- GPT4 and GPT3 now have seperate prompts. This makes it easier to change things without effecting other models.
- Moved alot of prompts into bot_prompts.py for ease.
- Unified command argument handing. Everything uses pipes now.
- Changed the way PDF generation is handled. LordGPT understands now he needs to send an HTML file to the command, not a string.
- Deleting Research, Debug and Exception logs at startup.
- Removed old leftover code.


UDPATE: 4-30-2023
- Added the option to choose between Google Search API and Serp
- Fixed a few more exceptions with unexpected data.

UPDATE 4-28-2023 10:30PM 
- Fixed all exceptions concerning illegal characters and invalid response response.
- Forcing a json message even if the lord doesnt respond with it.

UDPATE 4/28/2023
- New file operation code. Combined all file operations into one. Prompt uses less tokens now.
- New Search Engine, SERPA API. Sign up, free here serpaapi.com THis will allow us to tie into all sorts of search API's with a single function. (come to our discord and I'll give you a key for free to test.)
- Added ability to change lords direction if he's screwing up. Hit no and prompt him.
- Fixed ton's of illegal character exceptions from Browsing and Searching.
- Tweeked prompt to generate and save tasks after completion. Almost completes goals with ZERO conversation history. Memory? Blah...
- Playwright Browser code - We can do more options in the future like login to websites, ect.


UPDATE 4/27/2023
- Moved Browsing to Playwright and Chrome.
- pip install playwright
- playwright install

UPDATE: 4/27/2023
- Windows users now have all the options in config.json
- Prompt tweeks
- Windows bug fixes.



UPDATE: 4/26/2023
- Major Update:
- Reworked Prompt. I think its great, you be the judge.
- New Prompt enables almost 100% functionality with GPT3.5
- Fixed issue with invalid characters in Browse Web.
- New prompt fixes alot of issues with things.
- Debug flag now writes to the working folder as debug.txt.
- Reduced default max_token to 800
- Changed Json format, removed Goal % so he isnt forced to complete a goal. He was using it to skip things.
- Research is now saved to the working folder.
- Fixed message history
- The Lord now will complete task items and mark them complete.
- Throwback for the old school BBSers like me.