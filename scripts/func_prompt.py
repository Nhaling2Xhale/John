from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

# Define the exit function
def exit_gracefully(event):
    event.app.exit()

# Create a KeyBindings instance and bind F5 to the exit function
key_bindings = KeyBindings()
key_bindings.add(Keys.F5)(exit_gracefully)

# Create a PromptSession with the custom key bindings
session = PromptSession(key_bindings=key_bindings)
session = PromptSession()