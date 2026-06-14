NOTE_NAMES = ["do", "do#", "re", "re#", "mi", "fa",
              "fa#", "sol", "sol#", "la", "la#", "si"]

def midi_to_speedscore(midi_number: int):
    note = NOTE_NAMES[midi_number % 12]
    octave = (midi_number // 12) - 1

    # zone 3 (grave)
    if octave == 3:
        return f"{note},"

    # zone 4 (standard)
    elif octave == 4:
        return f"{note}"

    # zone 5 (aigu)
    elif octave == 5:
        return f"{note}'"

    # autres octaves
    elif octave < 3:
        return f"{note},,"
    else:
        return f"{note}''"