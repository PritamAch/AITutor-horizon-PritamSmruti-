import tkinter as tk
from tkinter import scrolledtext, Button, messagebox, Radiobutton
import pygame
from io import BytesIO
import openai
import speech_recognition as sr
import random
from threading import Thread
import gtts as gTTS

# Initialize Pygame
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
            append_message("You: " + message, "blue")
            process_input(message)

def send_message():
    message = input_text.get("1.0", tk.END).strip()
    if message:
        append_message("You: " + message, "blue")
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

    append_message("Assistant: " + response, "green")
    if tts_enabled:
        Thread(target=play_text, args=(response,)).start()

def generate_question():
    global current_question
    global current_answer
    global is_question_asked

    # Extract assistant responses from history
    assistant_responses = [msg['content'] for msg in history if msg['role'] == 'assistant']

    if len(assistant_responses) < 1:
        messagebox.showwarning("Insufficient Dialogue History", "There is not enough dialogue history to generate a question.")
        return

    # Randomly select an assistant response
    response = random.choice(assistant_responses)

    # Generate options based on the response
    options = [response]
    while len(options) < 4:
        new_option = openai.Completion.create(
            engine="pai-001", prompt=f"Complete the following: '{response}' with:",
            max_tokens=10, stop="\n"
        ).choices[0].text.strip()
        if new_option not in options:
            options.append(new_option)

    random.shuffle(options)

    current_question = f"What could be the completion of: '{response}'?"
    current_answer = response
    current_options = options
    is_question_asked = True

    append_message("Question: " + current_question, "green")
    for i, option in enumerate(current_options):
        append_message(f"{chr(65+i)}. {option}", "green")

def check_answer():
    global is_question_asked
    global score

    if not is_question_asked:
        messagebox.showinfo("No Question Asked", "Please generate a question first.")
        return

    user_choice = var.get()

    if current_options[user_choice] == current_answer:
        messagebox.showinfo("Correct Answer", "Your answer is correct!")
        score += 1
    else:
        messagebox.showinfo("Incorrect Answer", "Your answer is incorrect.")

    append_message("Score: " + str(score), "green")

    is_question_asked = False

# Initialize OpenAI
openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-dpqdJpwNUzoOxhxxEhWfrzHqkrwDsWbTLqDyPJHltXpBZXaj"

root = tk.Tk()
root.title("Personal Teacher")

history = [{"role": "user", "content": "answer always in less than 50 words"},
           {"role": "assistant", "content": "ok i will always answer as short as possible unless asked otherwis"}]

listening = False
tts_enabled = True
score = 0
is_question_asked = False
current_question = ""
current_answer = ""
current_options = []

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

question_button = Button(root, text="Generate Question", command=generate_question)
question_button.pack(pady=5)

var = tk.IntVar()
radio_buttons = []
for i in range(4):
    radio_buttons.append(Radiobutton(root, text="", variable=var, value=i))
    radio_buttons[-1].pack(pady=1)

answer_button = Button(root, text="Check Answer", command=check_answer)
answer_button.pack(pady=5)

root.after(1000, take_input_from_mic)  # Start listening to the microphone after 1 second
root.mainloop()
