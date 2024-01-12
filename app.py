from flask import Flask, Response, request
import os
from convert_to_csv import Final_year
from flask_cors import CORS
import subprocess
app = Flask(__name__)
CORS(app)

@app.route('/test', methods=["GET"])
def test_get():
    return "Hi"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        uploaded_files = request.files.getlist('audioFiles')

        for audio_file in uploaded_files:
            if audio_file and allowed_file(audio_file.filename):
                audio_file.save('./tracks/' + audio_file.filename)
                home()
            else:
                return 'Invalid audio file'

        return 'Audio files uploaded successfully'
    except Exception as e:
        return f'Error uploading audio: {str(e)}'
    
def home():
    output_csv_file = "extracted_features_final.csv"
    SAMPLE_RATE = 16000

    # Get a list of all the files in the ./tracks directory
    track_files = [f for f in os.listdir('./tracks') if os.path.isfile(os.path.join('./tracks', f))]

    if not track_files:
        response_data = "No audio files in the ./tracks directory"
        return Response(response_data, status=404, mimetype='text/plain')
    c = 0
    converted_files = []
    for track_file in track_files:
        file_path = os.path.join('./tracks', track_file)
        resultFile = "new_sample" + str(c) + ".mp3"
        c += 1
        ffmpeg_path = 'ffmpeg\\bin\\ffmpeg.exe'  
        command = [ffmpeg_path, '-y', '-i', file_path, '-acodec', 'libmp3lame', resultFile]
        subprocess.run(command)
        converted_files.append(resultFile)
    process_and_delete_audio(converted_files, output_csv_file, SAMPLE_RATE)

    response_data = "Features extracted and saved to 'extracted_features_final.csv'"
    return Response(response_data, status=200, mimetype='text/plain')  

def allowed_file(filename):
    # Check if the file extension is allowed (optional)
    allowed_extensions = {'ogg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_and_delete_audio(file_paths, output_csv_file, SAMPLE_RATE):
    final_year_instance = Final_year()
    final_year_instance.save_features_to_csv(file_paths, output_csv_file, SAMPLE_RATE, num_cores=-1)
    for file_path in file_paths:
        os.remove(file_path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
