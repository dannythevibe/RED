import pyttsx3

def list_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("Red: Auditing system voices...")
    for index, voice in enumerate(voices):
        print(f"Index: {index} | Name: {voice.name} | Genders: {voice.gender} | ID: {voice.id}")

if __name__ == "__main__":
    list_voices()
