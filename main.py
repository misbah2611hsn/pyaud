from flask import Flask, request, render_template_string,render_template
from gtts import gTTS
from io import BytesIO
import os
from langchain_fireworks import ChatFireworks
from IPython.display import Audio

# Setup Fireworks model and environment variables
os.environ["FIREWORKS_API_KEY"] = ""
mod = ChatFireworks(model="accounts/fireworks/models/mixtral-8x7b-instruct")

# Initialize Flask app
app = Flask(__name__,template_folder='src')

# Function to generate speech from text
def generate(text):
    response = mod.invoke(text).content  # Get model response
    language = 'en'
    
    # Convert text to speech
    tts = gTTS(text=response, lang=language, slow=False)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    return mp3_fp

# Flask route for voice input and audio output
@app.route('/', methods=['GET', 'POST'])
def index():
    audio_data = None  # Placeholder for the audio data
    if request.method == 'POST':
        text = request.form['text']  # Get the transcribed text from the form
        mp3_fp = generate(text)  # Generate speech
        mp3_fp.seek(0)  # Reset file pointer
        
        # Return HTML with embedded audio
        audio_data = mp3_fp.read()  # Read the audio file data
        audio_html = Audio(audio_data, autoplay=True)._repr_html_()  # Generate HTML to play audio
        return render_template_string('''
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Voice Command Text-to-Speech</title>
                <style>
                    /* General Styles */
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f7f6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }
                    .container {
                        background-color: white;
                        border-radius: 12px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        padding: 40px;
                        max-width: 600px;
                        text-align: center;
                    }
                    h1 {
                        font-size: 2rem;
                        color: #4CAF50;
                    }
                    p {
                        font-size: 1.1rem;
                        color: #666;
                        margin-top: 10px;
                    }

                    /* Button Styles */
                    button {
                        padding: 12px 24px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 30px;
                        cursor: pointer;
                        font-size: 1rem;
                        transition: background-color 0.3s ease;
                    }
                    button:hover {
                        background-color: #45a049;
                    }

                    /* Loader */
                    .loader {
                        border: 12px solid #f3f3f3;
                        border-top: 12px solid #4CAF50;
                        border-radius: 50%;
                        width: 60px;
                        height: 60px;
                        animation: spin 2s linear infinite;
                        display: none; /* Hidden initially */
                        margin: 20px auto;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }

                    /* Audio Player */
                    .audio-container {
                        margin-top: 20px;
                    }
                    audio {
                        width: 100%;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Voice Command Text-to-Speech</h1>
                    <p>Click below to speak and convert your speech to audio</p>
                    <form method="post" enctype="multipart/form-data" id="speechForm">
                        <input type="hidden" name="text" id="text_input">
                        <button type="button" onclick="startRecognition()">🎤 Start Voice Command</button>
                        <div class="loader" id="loader"></div>
                    </form>

                    <div class="audio-container">{{ audio_html|safe }}</div>

                </div>

                <script>
                    // JavaScript to capture voice input using Web Speech API
                    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = 'en-US';
                    recognition.interimResults = false;
                    recognition.maxAlternatives = 1;

                    function startRecognition() {
                        document.getElementById('loader').style.display = 'block';  // Show loader
                        recognition.start();
                        console.log('Voice recognition started.');
                    }

                    recognition.onresult = function(event) {
                        var speechResult = event.results[0][0].transcript;
                        document.getElementById('text_input').value = speechResult;
                        console.log('Result received: ' + speechResult);
                        
                        // Automatically submit the form after recognition
                        document.getElementById('speechForm').submit();
                    }

                    recognition.onspeechend = function() {
                        recognition.stop();
                        console.log('Voice recognition ended.');
                    }

                    recognition.onerror = function(event) {
                        document.getElementById('loader').style.display = 'none';  // Hide loader on error
                        console.log('Error occurred in recognition: ' + event.error);
                    }

                    // Hide the loader when form is submitted
                    document.getElementById('speechForm').onsubmit = function() {
                        document.getElementById('loader').style.display = 'block';  // Show loader
                    }
                </script>
            </body>
            </html>
        ''', audio_html=audio_html)
    
    # HTML form for voice input
    return render_template('index.html')
  
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
