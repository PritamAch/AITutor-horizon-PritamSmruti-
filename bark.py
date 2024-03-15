from io import BytesIO
import os
import tempfile
from gtts import gTTS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

import openai
import speech_recognition as sr
from threading import Thread

class PersonalTeacherApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = [{"role": "user", "content": "answer always in less than 50 words"},
                        {"role": "assistant", "content": "ok i will always answer as short as possible unless asked otherwise"}]
        self.listening = False
        self.tts_enabled = True

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.history_display = Label(text="Assistant: How can I help you with your studies?",
                             size_hint_y=0.7, halign="left", valign="middle", font_size="20sp",
                             text_size=(None, None), padding=(10, 10))

        layout.add_widget(self.history_display)

        self.input_text = TextInput(hint_text="Type your message here", multiline=False, size_hint_y=0.1, font_size="20sp")
        layout.add_widget(self.input_text)

        button_layout = BoxLayout(size_hint_y=0.2)
        send_button = Button(text="Send", size_hint=(0.4, 1), font_size="20sp")
        send_button.bind(on_press=self.send_message)
        button_layout.add_widget(send_button)

        mic_button = Button(text="Start Microphone", size_hint=(0.3, 1), font_size="20sp")
        mic_button.bind(on_press=self.toggle_mic)
        button_layout.add_widget(mic_button)

        tts_button = Button(text="Disable TTS", size_hint=(0.3, 1), font_size="20sp")
        tts_button.bind(on_press=self.toggle_tts)
        button_layout.add_widget(tts_button)

        layout.add_widget(button_layout)

        return layout

    def toggle_mic(self, instance):
        if self.listening:
            instance.text = "Start Microphone"
            self.listening = False
        else:
            instance.text = "Stop Microphone"
            self.listening = True
            self.take_input_from_mic()

    def toggle_tts(self, instance):
        self.tts_enabled = not self.tts_enabled
        if self.tts_enabled:
            instance.text = "Disable TTS"
        else:
            instance.text = "Enable TTS"

    def take_input_from_mic(self):
        def recognize_audio():
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            recognizer.energy_threshold = 4000

            with microphone as source:
                try:
                    audio = recognizer.listen(source, timeout=None)
                    text = recognizer.recognize_google(audio)
                    self.append_message("You: " + text, "user")
                    self.process_input(text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    pass

        Clock.schedule_once(lambda dt: Thread(target=recognize_audio).start(), 0.5)

    def send_message(self, instance):
        message = self.input_text.text.strip()
        if message:
            self.append_message("You: " + message, "user")
            self.input_text.text = ""
            self.process_input(message)

    def append_message(self, message, role):
        if role == "user":
            color = (0, 0, 1, 1)  # Blue
        elif role == "assistant":
            color = (0, 0.5, 0, 1)  # Green
        else:
            color = (0, 0, 0, 1)  # Black
        self.history_display.text += "\n" + message
        self.history_display.color = color

    def process_input(self, message):
            if message.lower() == "exit":
                self.stop()
            else:
                self.history.append({"role": "user", "content": message})
                chat_completion = openai.ChatCompletion.create(model="pai-001", messages=self.history)
                response = chat_completion.choices[0].message.content
                self.history.append({"role": "assistant", "content": response})
                self.append_message("Assistant: " + response, "assistant")
                if self.tts_enabled:
                    Thread(target=self.play_text, args=(response,)).start()

    def play_text(self, text):
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            tts.save(temp_file.name)
            sound = SoundLoader.load(temp_file.name)
            sound.play()
        os.unlink(temp_file.name)
        
openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-dpqdJpwNUzoOxhxxEhWfrzHqkrwDsWbTLqDyPJHltXpBZXaj"
if __name__ == "__main__":
    PersonalTeacherApp().run()
