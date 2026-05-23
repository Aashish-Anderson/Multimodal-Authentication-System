from src.face_manager import capture_face, verify_face
from src.voice_manager import record_voice, verify_voice
import os

# Ensure resource folder exists
if not os.path.exists("resources/haarcascade_frontalface_default.xml"):
    print("CRITICAL ERROR: haarcascade_frontalface_default.xml not found in 'resources' folder.")
    print("Please download it from OpenCV GitHub and place it there.")
    exit()

def main():
    while True:
        print("\n=== BIOMETRIC SECURITY SYSTEM ===")
        print("1. Enroll New User")
        print("2. Authenticate User (Face + Voice)")
        print("3. Exit")
        
        choice = input("Select: ")
        
        if choice == "1":
            uid = input("Enter New User ID (Numeric): ")
            if uid.isdigit():
                capture_face(uid)
                record_voice(uid)
            else:
                print("ID must be numeric.")

        elif choice == "2":
            uid = input("Enter User ID to verify: ")
            
            # STEP 1: FACE
            if verify_face(uid):
                print("✅ Face Verified.")
                
                # STEP 2: VOICE (Only if Face Passes)
                if verify_voice(uid):
                    print("✅ Voice Verified.")
                    print("\n🎉 ACCESS GRANTED: Welcome User " + uid + " 🎉")
                else:
                    print("✅ Voice Verified. Access Denied.")
            else:
                print("❌ Face Failed. Access Denied.")
        
        elif choice == "3":
            break

if __name__ == "__main__":
    main()