import datetime
import os

import pyttsx3
import  speech_recognition as sr
import wikipedia
import webbrowser
import smtplib

engine=pyttsx3.init('sapi5')
voices=engine.getProperty('voices')
engine.setProperty('voice',voices[1].id)
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def commad():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Lestening....")
        r.pause_threshold=1
        audio=r.listen(source)

    try:
        print("Recognizing...")
        query=r.recognize_google(audio,language='en-bd')
        print(f"user said: {query}\n")
    except Exception as e:
        # print(e)

        print("Say that again")
        return "None"
    return query

def sendemail(to,content):
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.login('ekdomses33@gmail.com','ajtkdcymrpblvuwc')
    server.sendmail('ekdomses33@gmail.com',to,content)
    server.close()

def wishme():
    hour=int(datetime.datetime.now().hour)
    if hour>4 and hour<12:
        speak("Good Morning Boss")
    elif hour>=12 and hour<=18:
        speak("Good afternoon Boss Hasib")
    else:
        speak("Good Evening Boss Hasib ")
if __name__ == "__main__":
    wishme()


    #query exucute
    while True:
        query = commad().lower()
        if "wikipedia" in query:
            speak("Searching Wikipedia")
            query=query.replace("wikipedia","")
            result=wikipedia.summary(query)
            print(result)
            speak("Accoroding to Wikipedia")
            speak(result)

        elif "open youtube" in query:
            webbrowser.open("youtube.com")

        elif "code" in query:
            # codepath="C:\\Users\\ASUS\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            codepath =( r"C:\Users\ASUS\AppData\Local\Programs\Microsoft VS Code\Code.exe")
            os.startfile(codepath)

        elif "send email" in query:
            try:
                speak("what should i say")
                content=commad()
                to="aislam192006@bscse.uiu.ac.bd"
                sendemail(to,content)
                speak("email has been sent")

            except Exception as e:
                print(e)
                speak("Failed to sent email , boss")


        elif "stop" in query:
            break


