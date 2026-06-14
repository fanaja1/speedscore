from core.note_converter import midi_to_speedscore
from ui.main_window import SpeedScoreUI

def handle_note(midi_note):
    note = midi_to_speedscore(midi_note)
    ui.add_note(note)

if __name__ == "__main__":
    ui = SpeedScoreUI(handle_note)
    ui.start_ui()