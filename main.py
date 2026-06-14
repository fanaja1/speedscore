import mido
from core.note_converter import midi_to_speedscore

ports = mido.get_input_names()

for i, p in enumerate(ports):
    print(f"{i}: {p}")

choice = int(input("\nChoisis le port: "))

sequence = []

with mido.open_input(ports[choice]) as inp:
    print("\n🎹 Joue...\n")

    for msg in inp:
        if msg.type == "note_on" and msg.velocity > 0:

            note = midi_to_speedscore(msg.note)
            sequence.append(note)

            print(" ".join(sequence))