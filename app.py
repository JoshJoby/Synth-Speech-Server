from flask import Flask, Response, request
import requests
import os
from convert_to_csv import Final_year
from flask_cors import CORS
import subprocess
from flask import jsonify
app = Flask(__name__)
CORS(app)
x = 0
@app.route('/test', methods=["POST"])
def send_csv_file_test():
    csv_file = "sample.csv"
    url = "http://localhost:80/predict"  # Replace with the actual endpoint to send the CSV file
    files = {'csv': open(csv_file, 'rb')}
    response = requests.post(url, files=files)
    data = response.json()
    predictions = data['predictions']
    # print(predictions)
    return response.json()

def test_get():
    return "Hi"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    results = ""
    try:
        uploaded_files = request.files.getlist('audioFiles')

        for audio_file in uploaded_files:
            if audio_file and allowed_file(audio_file.filename):
                audio_file.save('./tracks/' + audio_file.filename)
                try:
                    results =  home()
                except Exception as e:
                    print("inside " + str(e))
                    return f'{str(e)}'
            else:
                return 'Invalid audio file'
        print("RESULTS FINAL:", results)
        return results
    except Exception as e:
        print("Hii " + str(e))
        return f'{str(e)}'


def send_csv_file(csv_file):
    url = "http://localhost:80/predict"  # Replace with the actual endpoint to send the CSV file
    try:
        files =  {"csv" : open(csv_file, 'rb')}
        response = requests.post(url, files=files)
    except Exception as e:
        print("inside send csv " + str(e))
        return f'{str(e)}'
    print("response from server: " + str(response))
    if response.status_code == 200:
        data = response.json()
        predictions = data['predictions']
        print(predictions)
        print("File uploaded successfully.")
    else:
        print("Failed to upload file. Status code:", response.status_code)
    return response.json()
    
def home():
    response_data = None
    try:
        output_csv_file = "extracted_features_final.csv"
        SAMPLE_RATE = 16000

        # Get a list of all the files in the ./tracks directory
        track_files = [f for f in os.listdir('./tracks') if os.path.isfile(os.path.join('./tracks', f))]

        if not track_files:
            response_data = "No audio files in the ./tracks directory"
            return Response(response_data, status=404, mimetype='text/plain')
        print(track_files,"tracks")
        converted_files = []
        if(len(track_files) >= 6):
            for track_file in track_files:
                file_path = os.path.join('./tracks', track_file)
                resultFile = "new_sample" + str(len(converted_files)) + ".wav"
                ffmpeg_path = 'ffmpeg\\bin\\ffmpeg.exe'  
                command = [ffmpeg_path, '-y', '-i', file_path, '-acodec', 'pcm_s16le', '-ar', str(SAMPLE_RATE), resultFile]
                subprocess.run(command)
                converted_files.append(resultFile)
        
            process_and_delete_audio(converted_files, output_csv_file, SAMPLE_RATE)
            for file_path in track_files:
                os.remove(os.path.join('./tracks', file_path))
                
        print(output_csv_file,"output csv file")
        response_data = send_csv_file(output_csv_file)
        print(response_data,"response data")
    except Exception as e:
        print("inside home",str(e))
        response_data = str(e)
    return response_data 

def allowed_file(filename):
    # Check if the file extension is allowed (optional)
    allowed_extensions = {'ogg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_and_delete_audio(file_paths, output_csv_file, SAMPLE_RATE):
    final_year_instance = Final_year()
    final_year_instance.save_features_to_csv(file_paths, output_csv_file, SAMPLE_RATE, num_cores=-1)
    # file_paths.clear()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
