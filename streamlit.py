import datetime
import os
import pyttsx3
import speech_recognition as sr
import wikipedia
import webbrowser
import smtplib
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (for email credentials)
load_dotenv()

# Initialize speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()
    st.session_state.response = audio  # Update UI


def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.session_state.listening = True
        audio = r.listen(source)
        st.session_state.listening = False

    try:
        query = r.recognize_google(audio, language='en-bd')
        st.session_state.query = query  # Update UI
        return query.lower()
    except Exception as e:
        speak("Say that again")
        return None


def send_email(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(os.getenv("EMAIL"), os.getenv("EMAIL_PASSWORD"))
        server.sendmail(os.getenv("EMAIL"), to, content)
        server.close()
        speak("Email has been sent")
    except Exception as e:
        speak("Failed to send email")


def wish_me():
    hour = datetime.datetime.now().hour
    if 4 < hour < 12:
        speak("Good Morning Boss")
    elif 12 <= hour <= 18:
        speak("Good Afternoon Boss")
    else:
        speak("Good Evening Boss")


# Streamlit UI
st.title("🎤 Voice Assistant")
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'response' not in st.session_state:
    st.session_state.response = ""

# Microphone button
if st.button("🎤 Speak Command"):
    wish_me()
    query = command()

    if query:
        if "wikipedia" in query:
            speak("Searching Wikipedia...")
            result = wikipedia.summary(query.replace("wikipedia", ""), sentences=2)
            speak("According to Wikipedia: " + result)

        elif "open youtube" in query:
            webbrowser.open("youtube.com")
            speak("Opening YouTube")

        elif "code" in query:
            os.startfile(r"C:\Users\ASUS\AppData\Local\Programs\Microsoft VS Code\Code.exe")
            speak("Opening VS Code")

        elif "send email" in query:
            speak("What should I say?")
            content = command()
            send_email("recipient@example.com", content)

# Display outputs
st.write("**You said:** " + st.session_state.query)
st.write("**Assistant:** " + st.session_state.response)
if st.session_state.listening:
    st.write("🎤 Listening...")