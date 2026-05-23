import sounddevice as sd
import soundfile as sf
import numpy as np
import os

def test_mics():
    print("=== MICROPHONE DIAGNOSTIC TOOL ===")
    devices = sd.query_devices()
    
    # Filter for input devices (Microphones)
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    if not input_devices:
        print("No microphones found!")
        return

    print(f"Found {len(input_devices)} microphones. Testing each one...\n")
    
    for i, dev in enumerate(input_devices):
        dev_index = dev['index']
        dev_name = dev['name']
        print(f"Testing ID {dev_index}: {dev_name}")
        print("   >>> SPEAK NOW! (Recording 3s) <<<")
        
        try:
            # Try recording in Stereo (2 channels) - Safer for Intel Mics
            fs = 48000
            recording = sd.rec(int(3 * fs), samplerate=fs, channels=2, device=dev_index)
            sd.wait()
            
            filename = f"test_mic_{dev_index}.wav"
            sf.write(filename, recording, fs)
            
            # Check volume
            vol = np.max(np.abs(recording))
            print(f"   Saved to '{filename}' | Volume detected: {vol:.4f}")
            if vol < 0.01:
                print("   ⚠️  WARNING: Likely Silence")
            else:
                print("   ✅  Likely Valid Audio")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_mics()
    print("\nDONE.")
    print("Go to your folder and LISTEN to the 'test_mic_X.wav' files.")
    print("Find the one where you can hear your voice clearly.")