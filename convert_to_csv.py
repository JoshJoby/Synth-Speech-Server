import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
import joblib
import concurrent.futures
import os
import multiprocessing
import subprocess

class Final_year():
    def resample_if_necessary(self, audio, sr, target_sr):
        if sr != target_sr: 
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        return audio

    def extract_features(self, audio_file, SR):
        y, sr = librosa.load(audio_file, sr=None, duration=5, res_type='kaiser_fast')
        y = self.resample_if_necessary(y, sr, SR)
        chroma_stft = librosa.feature.chroma_stft(y=y, sr=SR)
        rms = librosa.feature.rms(y=y)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=SR)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=SR)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=SR)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        mfccs = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20)

        features = np.vstack([
            chroma_stft,
            rms,
            spectral_centroid,
            spectral_bandwidth,
            rolloff,
            zero_crossing_rate,
            mfccs
        ])

        # Transpose the features matrix to have time frames as rows and features as columns
        features = features.T

        return features

    def save_features_to_csv(self, audio_files, output_csv_file, SR, num_cores=-1):
        progress_bar = tqdm(audio_files, desc="Processing audio files")
        num_threads = os.cpu_count() or multiprocessing.cpu_count()

        # List to store the results
        data = []
        
        # Use ThreadPoolExecutor to process audio files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit tasks to the executor
            futures = {executor.submit(self.extract_features, audio_file,SR): audio_file for audio_file in progress_bar}
        
            # Iterate over completed tasks
            for future in concurrent.futures.as_completed(futures):
                audio_file = futures[future]
                try:
                    result = future.result()
                    
                    if result is not None:
                        data.append(result[0][:26])
                except Exception as e:
                    print(f"Error processing {audio_file}: {e}")

        # Check if each element in data is a 2D array, reshape if necessary
        # flattened_array = np.array([arr.flatten() if len(arr.shape) == 2 else arr for arr in data])
        # flat_array = np.squeeze(flattened_array)
        # final_data = []
        # for row in flat_array:
        #     final_data.append(flat_array[0])
        # print(final_data)
        feature_names = [
            "chroma_stft",
            "rms",
            "spectral_centroid",
            "spectral_bandwidth",
            "rolloff",
            "zero_crossing_rate",
            "mfcc1", "mfcc2", "mfcc3", "mfcc4", "mfcc5",
            "mfcc6", "mfcc7", "mfcc8", "mfcc9", "mfcc10",
            "mfcc11", "mfcc12", "mfcc13", "mfcc14", "mfcc15",
            "mfcc16", "mfcc17", "mfcc18", "mfcc19", "mfcc20"
        ]

        df = pd.DataFrame(data, columns=feature_names)
        df.to_csv(output_csv_file, index=False)

    def test_csv(self):
        df = pd.read_csv("extracted_features_final.csv")
        X_test = df.iloc[:,:]
        model = joblib.load('trained_random_forest_model_1000.pkl')
        predictions = model.predict(X_test)

        # Use the predictions in your application
        print("Predicted class labels:", predictions)


# # Example usage:
# if __name__ == '__main__':
    
#     sampleFile = "sample.ogg"
#     resultFile = "new_sample.mp3"
#     ffmpeg_path = 'ffmpeg\\bin\\ffmpeg.exe'  
#     command = [ffmpeg_path, '-i', sampleFile, '-acodec', 'libmp3lame', resultFile]
#     subprocess.run(command)
#     audio_files_fake = ["new_sample.mp3"]
#     output_csv_file = "extracted_features_final.csv"
#     SAMPLE_RATE = 16000
#     final_year_instance = Final_year()
#     final_year_instance.save_features_to_csv(audio_files_fake, output_csv_file, SAMPLE_RATE, num_cores=-1)
#     print("Features extracted and saved to 'extracted_features_final.csv'")
    # final_year_instance.test_csv()
