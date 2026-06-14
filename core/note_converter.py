import re

NOTE_NAMES = ["do", "do#", "re", "re#", "mi", "fa",
              "fa#", "sol", "sol#", "la", "la#", "si"]
SPEEDSCORE_TO_SEMITONE = {name: idx for idx, name in enumerate(NOTE_NAMES)}


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


def speedscore_to_midi(token: str):
    if not token:
        return None

    clean = token.strip()
    if not clean:
        return None

    octave = 4
    if clean.endswith("''"):
        octave = 6
        clean = clean[:-2]
    elif clean.endswith("'"):
        octave = 5
        clean = clean[:-1]
    elif clean.endswith(",,"):
        octave = 2
        clean = clean[:-2]
    elif clean.endswith(","):
        octave = 3
        clean = clean[:-1]

    if clean not in SPEEDSCORE_TO_SEMITONE:
        return None

    semitone = SPEEDSCORE_TO_SEMITONE[clean]
    return semitone + (octave + 1) * 12


def transpose_speedscore(text: str, semitone_shift: int):
    parts = re.split(r"(\s+)", text)
    result = []

    for part in parts:
        if part.isspace() or part == "":
            result.append(part)
            continue

        midi = speedscore_to_midi(part)
        if midi is None:
            result.append(part)
            continue

        transposed = midi + semitone_shift
        if transposed < 0:
            transposed = 0
        result.append(midi_to_speedscore(transposed))

    return "".join(result)