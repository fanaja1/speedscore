import tkinter as tk
import mido
import threading

class SpeedScoreUI:
    def __init__(self, on_midi_selected):
        self.on_midi_selected = on_midi_selected
        self.running = False
        self.thread = None
        self.inp = None

        self.root = tk.Tk()
        self.root.title("SpeedScore")
        self.root.geometry("900x500")

        # ===== MIDI SELECT =====
        self.label = tk.Label(self.root, text="Choisir un port MIDI")
        self.label.pack()

        self.port_var = tk.StringVar()

        self.dropdown = tk.OptionMenu(self.root, self.port_var, "")
        self.dropdown.pack()

        self.refresh_btn = tk.Button(self.root, text="Refresh MIDI", command=self.refresh_ports)
        self.refresh_btn.pack()

        self.start_btn = tk.Button(self.root, text="START", command=self.start)
        self.start_btn.pack()

        self.stop_btn = tk.Button(self.root, text="STOP", command=self.stop)
        self.stop_btn.pack()

        self.reset_btn = tk.Button(self.root, text="RESET", command=self.reset)
        self.reset_btn.pack()

        # ===== TEXT DISPLAY =====
        self.text = tk.Text(self.root, font=("Arial", 28))
        self.text.pack(expand=True, fill="both")

        self.refresh_ports()

    # ===== MIDI PORT LIST =====
    def refresh_ports(self):
        ports = mido.get_input_names()

        menu = self.dropdown["menu"]
        menu.delete(0, "end")

        for p in ports:
            menu.add_command(label=p, command=lambda value=p: self.port_var.set(value))

        if ports:
            self.port_var.set(ports[0])

    # ===== START MIDI =====
    def start(self):
        if self.running:
            return

        port = self.port_var.get()
        if not port:
            return

        self.running = True
        self.thread = threading.Thread(target=self.midi_loop, args=(port,), daemon=True)
        self.thread.start()

    # ===== STOP MIDI =====
    def stop(self):
        self.running = False
        if self.inp:
            self.inp.close()

    # ===== RESET =====
    def reset(self):
        self.text.delete("1.0", "end")

    # ===== ADD NOTE =====
    def add_note(self, note):
        if not self.running:
            return

        self.text.insert("end", note + " ")
        self.text.see("end")

    # ===== MIDI LOOP =====
    def midi_loop(self, port):
        try:
            self.inp = mido.open_input(port)

            for msg in self.inp:
                if not self.running:
                    break

                if msg.type == "note_on" and msg.velocity > 0:
                    self.on_midi_selected(msg.note)

        except Exception as e:
            print("Erreur MIDI:", e)

    def start_ui(self):
        self.root.mainloop()