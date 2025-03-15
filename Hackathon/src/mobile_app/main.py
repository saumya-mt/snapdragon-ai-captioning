from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from bleak import BleakClient
import asyncio
import os
from plyer import camera, tts, vibrator
import bluetooth
import threading
from kivy.core.audio import SoundLoader

class AccessibleImageApp(App):
    def __init__(self):
        super().__init__()
        self.bluetooth_socket = None
        self.server_address = None
        
    def build(self):
        # Use large, high-contrast layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Large, easy to find button
        self.capture_btn = Button(
            text='TAP ANYWHERE TO TAKE PHOTO',
            size_hint=(1, 0.7),
            font_size='32sp',
            background_color=(0, 0.7, 0, 1)  # Green color
        )
        self.capture_btn.bind(on_press=self.on_button_press)
        
        # Status label with large text
        self.status_label = Label(
            text='Ready - Double tap to take photo',
            font_size='24sp'
        )
        
        layout.add_widget(self.capture_btn)
        layout.add_widget(self.status_label)
        
        # Initialize text-to-speech
        self.speak("App ready. Double tap anywhere to take photo.")
        
        return layout
    
    def speak(self, text):
        """Speak text and vibrate for feedback"""
        tts.speak(text)
        try:
            vibrator.vibrate(0.1)  # Short vibration
        except:
            pass
    
    def on_button_press(self, instance):
        """Handle button press with audio feedback"""
        self.speak("Taking photo")
        threading.Thread(target=self.capture_and_send).start()
    
    def capture_and_send(self):
        """Capture and send image with audio feedback"""
        try:
            # Take photo
            self.speak("Point camera and wait")
            image_path = camera.take_picture()
            
            if not image_path:
                self.speak("Failed to take photo. Try again.")
                return
            
            self.speak("Photo taken. Sending for analysis.")
            
            # Connect to laptop if not connected
            if not self.bluetooth_socket:
                self.connect_to_laptop()
            
            # Send image
            if self.bluetooth_socket:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Send image size first
                size = len(image_data).to_bytes(8, 'big')
                self.bluetooth_socket.send(size)
                
                # Send image data
                self.bluetooth_socket.send(image_data)
                
                self.speak("Image sent. Waiting for description.")
                
                # Receive audio response
                size_data = self.bluetooth_socket.recv(8)
                audio_size = int.from_bytes(size_data, 'big')
                
                audio_data = b''
                while len(audio_data) < audio_size:
                    chunk = self.bluetooth_socket.recv(min(4096, audio_size - len(audio_data)))
                    if not chunk:
                        break
                    audio_data += chunk
                
                # Save and play audio
                audio_path = 'description.mp3'
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                
                # Play audio description
                sound = SoundLoader.load(audio_path)
                if sound:
                    sound.play()
                
            else:
                self.speak("Not connected to analysis server. Please try again.")
            
        except Exception as e:
            self.speak(f"Error: {str(e)}")
    
    def connect_to_laptop(self):
        """Connect to laptop server with audio feedback"""
        try:
            self.speak("Connecting to analysis server")
            
            # Search for the laptop
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
            for addr, name in nearby_devices:
                if name == "ImageAnalysisServer":  # Set this name on your laptop
                    self.server_address = addr
                    break
            
            if not self.server_address:
                self.speak("Analysis server not found")
                return
            
            # Connect
            self.bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.bluetooth_socket.connect((self.server_address, 1))
            
            self.speak("Connected to analysis server")
            
        except Exception as e:
            self.speak(f"Connection error: {str(e)}")
            self.bluetooth_socket = None

if __name__ == '__main__':
    AccessibleImageApp().run() 