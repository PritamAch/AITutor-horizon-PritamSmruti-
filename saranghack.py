import tkinter as tk
from tkinter import scrolledtext, Button
from gtts import gTTS
import pygame
from io import BytesIO
import openai
import speech_recognition as sr
from threading import Thread

pygame.init()

def audioToText():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    recognizer.energy_threshold = 4000

    with microphone as source:
        try:
            audio = recognizer.listen(source, timeout=None)
            text = recognizer.recognize_google(audio)
            print("Recognized:", text)
            return text
        
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return ""

def play_text(text):
    tts = gTTS(text=text, lang='en')
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()

def toggle_mic():
    global listening
    if listening:
        mic_button.config(text="Start Microphone")
        listening = False
    else:
        mic_button.config(text="Stop Microphone")
        listening = True
        take_input_from_mic()

def toggle_tts():
    global tts_enabled
    tts_enabled = not tts_enabled
    if tts_enabled:
        tts_button.config(text="Disable TTS")
    else:
        tts_button.config(text="Enable TTS")

def take_input_from_mic():
    if listening:
        message = audioToText()
        if message != "":
            history_text.insert(tk.END, "You: " + message + "\n")
            history_text.see(tk.END)
            process_input(message)

def send_message():
    message = input_text.get("1.0", tk.END).strip()
    if message:
        history_text.insert(tk.END, "You: " + message + "\n")
        history_text.see(tk.END)
        input_text.delete("1.0", tk.END)
        process_input(message)

def process_input(message):
    global history
    if message == "exit":
        root.destroy()
        return

    history.append({"role": "user", "content": message})
    chat_completion = openai.ChatCompletion.create(model="pai-001", messages=history)

    response = chat_completion.choices[0].message.content
    history.append({"role": "assistant", "content": response})

    history_text.insert(tk.END, "Assistant: " + response + "\n")
    history_text.see(tk.END)
    if tts_enabled:
        Thread(target=play_text, args=(response,)).start()

openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-dpqdJpwNUzoOxhxxEhWfrzHqkrwDsWbTLqDyPJHltXpBZXaj"

root = tk.Tk()
root.title("Personal Teacher")

history = [{"role": "user", "content": "answer always in less than 50 words"},
           {"role": "assistant", "content": "ok i will always answer as short as possible unless asked otherwis"}]

listening = False
tts_enabled = True

history_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
history_text.pack(padx=10, pady=10)

input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=5)
input_text.pack(padx=10, pady=10)

mic_button = Button(root, text="Start Microphone", command=toggle_mic)
mic_button.pack(pady=5)

tts_button = Button(root, text="Disable TTS", command=toggle_tts)
tts_button.pack(pady=5)

send_button = Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

root.after(1000, take_input_from_mic)  # Start listening to the microphone after 1 second
root.mainloop()
