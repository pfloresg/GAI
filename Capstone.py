#!/usr/bin/env python3

import os
import time
import playsound
import time
import speech_recognition as sr
from gtts import gTTS
import numpy as np
import os
import urllib.request as ur
import ipywidgets as widgets

from openai import OpenAI
from IPython.display import IFrame, HTML
from io import BytesIO 
from PIL import Image
from IPython.display import display



key_API=os.environ['OPENAI_API']
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    # or you can explicitly pass in the key (NOT RECOMMENDED)
    api_key=key_API,
)

## Function which inputs speechtotext using gtts, prefer this from OpenAI due to not costing for the UI
def speak(text,lang):
    tts = gTTS(text=text, lang=lang)
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    
#get the audio from the Mic to transform to text so it can interact with the prompts API of OpenAI
def get_audio(lang):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=0.2)
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio,language=lang)
            print(said)
        except sr.UnknownValueError:
            print("No logre entenderte, ¿Puedes repetir eso?")
        except sr.RequestError as e:
            print(f"Error with the speech recognition service; {e}")
        #return None
        except Exception as e:
            print("Exception: " + str(e))

    return said

#Function used to record audio to be used to translate, currently only spanish
def rec_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=0.2)
        audio = r.listen(source)
    said = r.recognize_google(audio,language="es-MX")
    print(said)
    tts = gTTS(text=said, lang="es")
    filename = "voice.mp3"
    tts.save(filename)
    #playsound.playsound(filename)
    return filename

#Function used to create prompt and interact with dalee  
#This will ask the user about the design and style he wants for it
def dalee():
    speak("Que deseas que ponga en el diseño","es")
    logo_prompt= "Tema: "+get_audio("es-MX")
    speak("En que estilo","es")
    logo_prompt=logo_prompt+" Estilo:"+get_audio("es-MX") 

    image_size = 1024
    response = client.images.generate(
    model="dall-e-3",
    prompt=logo_prompt,
    size=f"{image_size}x{image_size}"
    )
    image_url = response.model_dump()['data'][0]['url']
    url = image_url
    with ur.urlopen(url) as url:
        img = Image.open(BytesIO(url.read()))
    display(img)
    print(image_url)
    
#Function to translate the recorded information, interface with whisper to translate the text
#Then it plays back what the translation is
def translate():
    speak("Reproduce o di lo que deseas traducir","es")
    audio_file= open(rec_audio(), "rb")
    translation = client.audio.translations.create(
    model="whisper-1",
    file=audio_file
    )
    speak(translation.text,"en")
    
#Fuction to have the interface with the GPT model and to be able to interact
# through voice keeping in this mode until the user ask to exit     
def assistant():
    while True:
        speak("Como puedo asistirte?","es")
        #Translate speech to text
        SpeechText = get_audio("es-MX")
        SpeechText = SpeechText.lower()
        
        #Manage if the user wants to leave the 
        if SpeechText=="salir":
            speak("Ten un buen día","es")
            break
        else:
            response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                "role": "system",
                "content": "Eres un util asistente"
                },
                {
                "role": "user",
                "content": "{}".format(SpeechText)
                }
                ]
            )

            # Print out results for further processing
            print(f"Human:{SpeechText}\nAI:{response.model_dump()['choices'][0]['message']['content']}")

            # SPEAK IT OUT
            speak(response.model_dump()['choices'][0]['message']['content'],"es")
        continue
    

while True:

    try:

        with sr.Microphone() as source:

            #Greetings and present options
            speak("Buen día","es")
            #Translate speech to text
            SpeechText = get_audio("es-MX")
            SpeechText = SpeechText.lower()
            
            #Manage the option the user want to do translate, assistant, translate or exit
            if SpeechText=="salir":
                speak("Ten un buen día","es")
                break
            elif "imagen" in SpeechText:
                dalee()
            elif "asistente" in SpeechText:
                assistant()
            elif "traductor" in SpeechText:
                translate()
            
                

           
    #Exception handling
    except sr.UnknownValueError:
       print("I didn't quite get you. Can you please repeat that?")
       speak("No logre entenderte, ¿Puedes repetir eso?","es")
       recognizer = sr.Recognizer()
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")
    except Exception as e:
        print("Exception: " + str(e))
    continue