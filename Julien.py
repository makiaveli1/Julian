import io
import os
import openai
import speech_recognition as sr
import pyttsx3
import pydub
import logging
import simpleaudio as sa
import tempfile
import json

from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech
from user_profile import UserProfile, InvalidInformationError, UserProfileError
from conversation_history import ConversationHistory
from config import OPENAI_API_KEY, GOOGLE_APPLICATION_CREDENTIALS_PATH
from sentiment_analyzer import analyze_sentiment



openai.api_key = OPENAI_API_KEY
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH


# Configure logging
logging.basicConfig(level=logging.INFO)


text = "I love this product. It's amazing!"
result = analyze_sentiment(text)
print(result)
user_profile = UserProfile(name="Gbemi", wake_words="Hey Julian")
conversation_history_instance = ConversationHistory(conversation_history)
conversation_history = conversation_history_instance.load_conversation_history(file_path="conversation_history.json")

# Custom exceptions
class MicrophoneError(Exception):
    pass

class OpenAIError(Exception):
    pass


def tts_engine():
    client = texttospeech.TextToSpeechClient() 
    return client



def generate_prompt(conversation_history, text, window_size=10):
    prompt = ""
    relevant_history = conversation_history[-window_size:]
    for message in relevant_history:
        if message["role"] == "system":
            prompt += f"{message['content']} "
        elif message["role"] == "user":
            prompt += f"User: {message['content']} "
        else:
            prompt += f"Assistant: {message['content']} "
    prompt += f"User: {text}. Please provide a detailed and concise answer."
    return prompt

def generate_response(conversation_history, text, user_profile, window_size=5):
    prompt = generate_prompt(conversation_history, text, window_size)
    for message in conversation_history:
        if message["role"] == "system":
            prompt += f"{message['content']} "
        elif message["role"] == "user":
            prompt += f"User: {message['content']} "
        else:
            prompt += f"Assistant: {message['content']} "
    prompt += f"User: {text}. Please provide a detailed and concise answer."
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.6,
        )
        follow_up_question = None
        if "Follow-up:" in response.choices[0].text.strip():
            response_text, follow_up_question = response.choices[0].text.strip().split("Follow-up:")
            response_text = response_text.strip()
            follow_up_question = follow_up_question.strip()
        else:
            response_text = response.choices[0].text.strip()

        return response_text, follow_up_question

    except openai.error.OpenAIError as e:
        print(f"An error occurred while generating a response using OpenAI API: {e}")
        return "I'm sorry, I'm having trouble generating a response right now.", None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "I'm sorry, I'm having trouble generating a response right now.", None


def recognize_speech():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    except OSError as e:
        print(f"Microphone error: {e}")
        raise MicrophoneError("There was a problem with the microphone.") from e

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand you.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def detect_intent(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    return session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )



WAKE_WORD = "Hey Julian"
SLEEP_WORD = "Goodbye Julian"

def interact():
    engine = tts_engine()
    user_profile = UserProfile(name="Gbemi", wake_words=["Hey Julian"])
    conversation_history = conversation_history_instance.load_conversation_history(file_path="conversation_history.json")
    listening = False

    while True:
        if not listening:
            listening = handle_idle_state(listening, conversation_history, engine, user_profile)
        else:
            listening = handle_active_state(listening, conversation_history, engine, user_profile)

def speak(text, user_profile):
    audio_content = synthesize_speech(text, user_profile)

    with tempfile.NamedTemporaryFile(delete=True) as temp_audio_file:
        temp_audio_file.write(audio_content)
        temp_audio_file.flush()
        os.system(f"start {temp_audio_file.name}")

def update_name_if_present(user_profile, text):
    information = user_profile.extract_information(text)
    if "name" in information:
        user_profile.update_preferences("name", information["name"])



def handle_idle_state(listening, conversation_history, engine, user_profile):
    if not listening:
        recognized_text = recognize_speech()
        if recognized_text and any([w.lower() in recognized_text.lower() for w in user_profile.wake_words]):
            listening = True
            print("Waiting for the wake word...")
            greeting = generate_greeting(user_profile)
            speak(greeting, user_profile)  # Removed the engine parameter
    return listening


def update_preferences_from_text(user_profile, text):
    try:
        information = user_profile.extract_information(text)
        for key, value in information.items():
            user_profile.update_preferences(key, value)
    except InvalidInformationError as e:
        print(f"Error updating preferences: {e}")

def generate_greeting(user_profile):
    return f"Hello, {user_profile['name']}! How can I help you today?"


def is_wake_word(text):
    return text and text.lower() == WAKE_WORD.lower()


def handle_active_state(listening, conversation_history, engine, user_profile):
    state = "IDLE"
    follow_up_question = None

    while state != "SLEEP":
        text = listen()

        if text and is_sleep_word(text):
            listening = False
            print("Going to sleep. Say the wake word to start interacting again.")
            break
        if follow_up_question:
            state = "FOLLOW_UP"
            speak_follow_up_question(follow_up_question, user_profile)

        conversation_history.append({"role": "user", "content": text})
        response, follow_up_question = generate_response(conversation_history, text, user_profile)
        conversation_history.append({"role": "assistant", "content": response})
        state = "PROVIDING_ANSWER"
        speak(response, user_profile)

        if not follow_up_question:
            print("I'm sorry, I'm having trouble generating a response right now.")
    return listening


def is_sleep_word(text):
    return text and text.lower() == SLEEP_WORD.lower()


def speak_follow_up_question(follow_up_question, user_profile):  # Add user_profile parameter
    print(f"Follow-up question: {follow_up_question}")
    speak(follow_up_question, user_profile) 

def synthesize_speech(text, user_profile):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Choose the voice based on the user_profile preferences
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Configure the audio format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    return response.audio_content

if __name__ == "__main__":
    interact()


