import sounddevice as sd

print("listing available audio devices...\n")
print(sd.query_devices())

print("\nLOOK FOR YOUR MICROPHONE IN THE LIST ABOVE.")
print("Write down the number (Index) next to it.")