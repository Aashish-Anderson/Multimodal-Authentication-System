import os
import sounddevice as sd
import soundfile as sf
import time
import numpy as np
import pickle
import librosa
from sklearn.mixture import GaussianMixture


# ==========================================
# CONFIGURATION
# ==========================================
DATA_PATH = "data/voices/"
MODEL_PATH = "models/voice_models/"


def ensure_dirs():
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(MODEL_PATH, exist_ok=True)


def normalize_audio(audio):
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        return audio / max_val
    return audio


def extract_features(file_path):
    try:
        audio, sample_rate = librosa.load(file_path, sr=None)
        audio = normalize_audio(audio)

        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=20)
        mfcc_delta = librosa.feature.delta(mfcc)
        return np.vstack((mfcc, mfcc_delta)).T
    except:
        return None



# ======================================================
# RECORD
# ======================================================

def record_voice(user_id):

    ensure_dirs()
    fs = 48000
    duration = 4

    print(f"\n[VOICE] Recording 3 samples for User {user_id}...", flush=True)

    for i in range(3):

        print(f"\nSample {i+1}/3 - Say: 'Biometric Access is Secure'", flush=True)
        time.sleep(0.5)
        print("Recording... (SPEAK NOW)", flush=True)

        # 🔥 FIX — Always use default mic
        sd.default.device = None

        voice = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()

        sf.write(f"{DATA_PATH}user_{user_id}_{i+1}.wav", voice, fs)

        print(f"Saved sample {i+1}.", flush=True)

    train_voice_model(user_id)



# ======================================================
# TRAIN
# ======================================================

def train_voice_model(user_id):

    ensure_dirs()
    features = []

    files = [f for f in os.listdir(DATA_PATH) if f.startswith(f"user_{user_id}_")]

    print(f"[TRAIN] Training Voice Model for User {user_id}...", flush=True)

    for file in files:
        vector = extract_features(os.path.join(DATA_PATH, file))
        if vector is not None:
            features.append(vector)

    if not features:
        print("[ERROR] No audio data found.", flush=True)
        return

    features = np.vstack(features)

    gmm = GaussianMixture(n_components=32, covariance_type='diag', n_init=3)
    gmm.fit(features)

    with open(f"{MODEL_PATH}user_{user_id}.gmm", 'wb') as f:
        pickle.dump(gmm, f)

    print("[SUCCESS] Voice model saved.", flush=True)



# ======================================================
# VERIFY
# ======================================================

def verify_voice(user_id):

    model_file = f"{MODEL_PATH}user_{user_id}.gmm"

    if not os.path.exists(model_file):
        print("[ERROR] No Voice Model Found", flush=True)
        return False

    print(f"[AUTH] Please speak passphrase for User {user_id}...", flush=True)

    fs = 48000
    duration = 4

    # 🔥 FIX — Always use default mic
    sd.default.device = None

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()

    sf.write("temp_auth.wav", recording, fs)

    with open(model_file, 'rb') as f:
        gmm = pickle.load(f)

    features = extract_features("temp_auth.wav")

    if features is None:
        return False

    score = gmm.score(features)

    print("---------------------------------------", flush=True)
    print(f"  CONFIDENCE SCORE: {score:.2f}", flush=True)
    print("---------------------------------------", flush=True)

    os.remove("temp_auth.wav")

    THRESHOLD = -110.0

    if score > THRESHOLD:
        return True

    print(f"❌ Voice Mismatch. (Score {score:.2f} < {THRESHOLD})", flush=True)
    return False
