import tkinter as tk
from tkinter import scrolledtext, Button
import pygame
from io import BytesIO
import openai
import speech_recognition as sr
from threading import Thread
from gtts import gTTS

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
            append_message("You:\n " + message, "blue")
            process_input(message)

def send_message():
    message = input_text.get("1.0", tk.END).strip()
    if message:
        append_message("You:\n " + message, "blue")
        process_input(message)
        input_text.delete("1.0", tk.END)

def append_message(message, color):
    history_text.config(state=tk.NORMAL)
    history_text.insert(tk.END, message + "\n", color)
    history_text.see(tk.END)
    history_text.config(state=tk.DISABLED)

def process_input(message):
    global history
    if message == "exit":
        root.destroy()
        return

    history.append({"role": "user", "content": message})
    chat_completion = openai.ChatCompletion.create(model="pai-001", messages=history)

    response = chat_completion.choices[0].message.content
    history.append({"role": "assistant", "content": response})

    append_message("AI Teacher:\n " + response, "green")
    if tts_enabled:
        Thread(target=play_text, args=(response,)).start()

def generate_questions():
    global is_question_asked


    history_subset = history[2:]  # Exclude the first two entries
    completion = openai.Completion.create(
        engine="pai-001",
        prompt="\n".join([f"{msg['content']}" for msg in history_subset]) + "\nQ:",
        temperature=0.7,
        max_tokens=100,
        n=5,
        stop="\n"
    )
    
    # Display the generated questions
    for i, choice in enumerate(completion.choices):
        question = choice.text.strip()
        append_message(f"Question {i + 1}: {question}", "green")

# Initialize OpenAI
openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-dpqdJpwNUzoOxhxxEhWfrzHqkrwDsWbTLqDyPJHltXpBZXaj"

# Initialize tkinter
root = tk.Tk()
root.title("Virtual Teacher")
root.configure(bg="#e6e6fa")  # Set light purpleish background color
root.iconbitmap("logo.ico")

history = [{"role": "user", "content": "generate the response less than 50 words unless asked otherwise"},
           {"role": "assistant", "content": "okay"}]

listening = False
tts_enabled = True
is_question_asked = False

# GUI 

history_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, bg="#f0f8ff", fg="black")  # Set light blue background for history text
history_text.pack(padx=10, pady=10)

input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=5, bg="#f0f8ff", fg="black")  # Set light blue background for input text
input_text.pack(padx=10, pady=10)

mic_button = Button(root, text="Start Microphone", command=toggle_mic, bg="#9370DB", fg="white")  # Set dark purple background for button
mic_button.pack(pady=5)

tts_button = Button(root, text="Disable TTS", command=toggle_tts, bg="#9370DB", fg="white")  # Set dark purple background for button
tts_button.pack(pady=5)

send_button = Button(root, text="Send", command=send_message, bg="#9370DB", fg="white")  # Set dark purple background for button
send_button.pack(pady=5)

question_button = Button(root, text="Generate Questions", command=generate_questions, bg="#9370DB", fg="white")  # Set dark purple background for button
question_button.pack(pady=5)

# Start microphone input after 1 second
root.after(1000, take_input_from_mic)
root.mainloop()
