import re

class InvalidInformationError(Exception):
    pass

class UserProfileError(Exception):
    pass

class UserProfile:
    def __init__(self, name, language="en"):
        self.name = name
        self.gender = None
        self.language = language

    def update_preferences(self, key, value):
        self.preferences[key] = value

    def get_preference(self, preference_key):
        if preference_key in self.preferences:
            return self.preferences[preference_key]
        elif preference_key == "language_code":
            return self.language
        else:
            return None

    def extract_personal_information(self, text):
        """
        Extract preferences from a given text using regex patterns.

        Args:
            text (str): A string containing preferences.

        Returns:
            dict: A dictionary with preference keys and their corresponding values.
        """

        patterns = {
            "language_code": r"(?<=language code: )\w{2}-\w{2}",
            "ssml_gender": r"(?<=ssml gender: )\w+",
            "speaking_rate": r"(?<=speaking rate: )\d+(\.\d+)?",
            "voice_pitch": r"(?<=voice pitch: )\d+(\.\d+)?",
            "volume_gain_db": r"(?<=volume gain: )\d+(\.\d+)?",
        }

        information = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                information[key] = match.group(0)

        # Convert speaking_rate, voice_pitch, and volume_gain_db to float
        for key in ["speaking_rate", "voice_pitch", "volume_gain_db"]:
            if key in information:
                information[key] = float(information[key])

        return information

    def update_information(self, text):
        extracted_information = UserProfile.extract_information(text)
        for key, value in extracted_information.items():
            self.update_preferences(key, value)
            
    @staticmethod
    def extract_information(text):
        information = {}


        # Define a list of dictionaries with information types and regex patterns
        patterns = [
        {'key': 'name', 'pattern': re.compile(r"(?:my name is|I am|I'm) (\w+)", re.IGNORECASE)},
        {'key': 'age', 'pattern': re.compile(r"I am (\d+) years? old", re.IGNORECASE)},
        {'key': 'location', 'pattern': re.compile(r"I live (?:in|at) ([\w\s]+)", re.IGNORECASE)},
        {'key': 'job', 'pattern': re.compile(r"I work as (?:a |an )?([\w\s]+)", re.IGNORECASE)},
        {'key': 'hobby', 'pattern': re.compile(r"My (?:hobby|hobbies) (?:is|are) ([\w\s]+)", re.IGNORECASE)},
        {'key': 'pet', 'pattern': re.compile(r"I have (?:a |an )?([\w\s]+) (?:dog|cat|bird|fish)", re.IGNORECASE)},
        {'key': 'favorite_food', 'pattern': re.compile(r"My (?:favorite|favourite) food is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_color', 'pattern': re.compile(r"My (?:favorite|favourite) color is (\w+)", re.IGNORECASE)},
        {'key': 'favorite_movie', 'pattern': re.compile(r"My (?:favorite|favourite) movie is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_music', 'pattern': re.compile(r"My (?:favorite|favourite) (?:music|genre|song|artist|band) is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'phone_number', 'pattern': re.compile(r"My phone number is (\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", re.IGNORECASE)},
        {'key': 'email', 'pattern': re.compile(r"my email (?:address)? is ([\w.-]+@[\w.-]+\.\w+)", re.IGNORECASE)},
        {'key': 'birthdate', 'pattern': re.compile(r"My (?:birth(?:date)?|birthday) is (\d{1,2}[-./]\d{1,2}[-./]\d{2,4})", re.IGNORECASE)},
        {'key': 'nationality', 'pattern': re.compile(r"I am (?:a |an )?([\w\s]+) (?:citizen|national)", re.IGNORECASE)},
        {'key': 'favorite_book', 'pattern': re.compile(r"My (?:favorite|favourite) book is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_sport', 'pattern': re.compile(r"My (?:favorite|favourite) sport (?:is|would be) (\w+)", re.IGNORECASE)},
        {'key': 'education', 'pattern': re.compile(r"I (?:studied|study) (?:at|in) ([\w\s]+)", re.IGNORECASE)},
        {'key': 'siblings', 'pattern': re.compile(r"I have (\d+) (?:brothers?|sisters?|siblings)", re.IGNORECASE)},
        {'key': 'marital_status', 'pattern': re.compile(r"I am (?:single|married|divorced|widowed|engaged|separated)", re.IGNORECASE)},
        {'key': 'children', 'pattern': re.compile(r"I have (\d+) (?:kids?|children)", re.IGNORECASE)},
        {'key': 'car', 'pattern': re.compile(r"I (?:own|drive) (?:a |an )?([\w\s]+) car", re.IGNORECASE)},
        {'key': 'height', 'pattern': re.compile(r"I am (\d+(?:\.\d+)?) (?:cm|feet|ft|meters|m)", re.IGNORECASE)},
        {'key': 'weight', 'pattern': re.compile(r"I weigh (\d+(?:\.\d+)?) (?:kg|pounds|lbs)", re.IGNORECASE)},
        {'key': 'university', 'pattern': re.compile(r"I (?:studied|study) at ([\w\s]+) (?:university|college)", re.IGNORECASE)},
        {'key': 'degree', 'pattern': re.compile(r"I have (?:a|an) ([\w\s]+) degree", re.IGNORECASE)},
        {'key': 'relationship', 'pattern': re.compile(r"I am (?:in a relationship|single|dating|married|divorced|widowed|engaged|separated)", re.IGNORECASE)},
        {'key': 'political_view', 'pattern': re.compile(r"My political view is (?:liberal|conservative|moderate|progressive|libertarian|socialist|green|other)", re.IGNORECASE)},
        {'key': 'religion', 'pattern': re.compile(r"My religion is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'exercise', 'pattern': re.compile(r"I (?:exercise|work out) (\d+)(?: times)? a (?:week|month)", re.IGNORECASE)},
        {'key': 'dream_job', 'pattern': re.compile(r"My dream job is (?:a |an )?([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_tv_show', 'pattern': re.compile(r"My (?:favorite|favourite) (?:TV show|series) is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_travel_destination', 'pattern': re.compile(r"My (?:favorite|favourite) (?:travel|vacation) destination is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_animal', 'pattern': re.compile(r"My (?:favorite|favourite) animal is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_season', 'pattern': re.compile(r"My (?:favorite|favourite) season is (?:spring|summer|fall|autumn|winter)", re.IGNORECASE)},
        {'key': 'favorite_quote', 'pattern': re.compile(r"My (?:favorite|favourite) quote is \"([\w\s]+)\"", re.IGNORECASE)},
        {'key': 'favorite_author', 'pattern': re.compile(r"My (?:favorite|favourite) author is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_actor', 'pattern': re.compile(r"My (?:favorite|favourite) actor is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_actress', 'pattern': re.compile(r"My (?:favorite|favourite) actress is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_director', 'pattern': re.compile(r"My (?:favorite|favourite) director is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_video_game', 'pattern': re.compile(r"My (?:favorite|favourite) video game is ([\w\s]+)", re.IGNORECASE)},
        {'key': 'favorite_subject', 'pattern': re.compile(r"My (?:favorite|favourite) subject (?:is|was) ([\w\s]+)", re.IGNORECASE)}
        ]



        # Loop through the patterns and search for matches in the text
        for pattern in patterns:
            if match := pattern['pattern'].search(text):
                # Store the matched information in the dictionary
                information[pattern['key']] = match.group(1)

        return information
