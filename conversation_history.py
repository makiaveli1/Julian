import json
import os

class ConversationHistory:
    def __init__(self, conversation_history):
        self.conversation_history = conversation_history 
        self.conversation_history_length = len(conversation_history) 
        self.conversation_history_index = 0

    def save_conversation_history(self, file_path="conversation_history.json"):
        """
        Save conversation history to a JSON file.

        Args:
            file_path (str, optional): The path to the file to save the conversation history. Defaults to "conversation_history.json".
        """
        try:
            with open(file_path, "w") as outfile:
                json.dump(self.conversation_history, outfile)
        except IOError as e:
            print(f"Error while saving conversation history: {e}")

    def load_conversation_history(self, file_path="conversation_history.json"):
        """
        Load conversation history from a JSON file.

        Args:
            file_path (str, optional): The path to the file to load the conversation history from. Defaults to "conversation_history.json".

        Returns:
            list: A list of conversation history items.
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as infile:
                    self.conversation_history = json.load(infile)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error while loading conversation history: {e}")
                self.conversation_history = [{"role": "system", "content": "You are Julian, a helpful voice assistant."}]
        else:
            self.conversation_history = [{"role": "system", "content": "You are Julian, a helpful voice assistant."}]

        return self.conversation_history
