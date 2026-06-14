import customtkinter as ctk
import mido
import threading

# Configuration du thème moderne
ctk.set_appearance_mode("dark")       # Mode sombre automatique
ctk.set_default_color_theme("blue")   # Couleur principale des boutons

class SpeedScoreUI:
    def __init__(self, on_midi_selected):
        self.on_midi_selected = on_midi_selected
        self.running = False
        self.thread = None
        self.inp = None

        # Fenêtre principale CustomTkinter
        self.root = ctk.CTk()
        self.root.title("SpeedScore")
        self.root.geometry("950x550")
        self.root.minsize(800, 450)

        # Gestion de la fermeture propre de la fenêtre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configuration de la grille principale (2 colonnes)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. BARRE LATÉRALE DE CONTRÔLE (SIDEBAR)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Garde la largeur fixe

        # Titre de l'application
        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚡ SpeedScore", 
            font=ctk.CTkFont(family="Arial", size=22, weight="bold")
        )
        self.title_label.pack(pady=(30, 20), padx=20)

        # Menu déroulant MIDI (Remplace OptionMenu)
        self.label = ctk.CTkLabel(self.sidebar, text="Périphérique MIDI :", font=ctk.CTkFont(size=12))
        self.label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.dropdown = ctk.CTkComboBox(self.sidebar, values=[""], width=180)
        self.dropdown.pack(pady=5, padx=20)

        # Bouton Refresh
        self.refresh_btn = ctk.CTkButton(self.sidebar, text="Refresh Ports", fg_color="transparent", border_width=1, command=self.refresh_ports)
        self.refresh_btn.pack(pady=5, padx=20)

        # Bouton START
        self.start_btn = ctk.CTkButton(
            self.sidebar, 
            text="START", 
            fg_color="#2ecc71", 
            hover_color="#27ae60", 
            text_color="white",
            font=ctk.CTkFont(weight="bold"),
            command=self.start
        )
        self.start_btn.pack(pady=(30, 10), padx=20)

        # Bouton STOP
        self.stop_btn = ctk.CTkButton(
            self.sidebar, 
            text="STOP", 
            fg_color="#e67e22", 
            hover_color="#d35400",
            text_color="white",
            font=ctk.CTkFont(weight="bold"),
            command=self.stop
        )
        self.stop_btn.pack(pady=10, padx=20)

        # Bouton RESET
        self.reset_btn = ctk.CTkButton(
            self.sidebar, 
            text="RESET", 
            fg_color="#e74c3c", 
            hover_color="#c0392b",
            text_color="white",
            command=self.reset
        )
        self.reset_btn.pack(pady=10, padx=20)

        # Indicateur de Statut
        self.status_label = ctk.CTkLabel(self.sidebar, text="Statut : Arrêté", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

        # ==========================================
        # 2. ZONE D'AFFICHAGE DES NOTES
        # ==========================================
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Zone de texte moderne (Remplace tk.Text)
        self.text = ctk.CTkTextbox(
            self.main_frame, 
            font=ctk.CTkFont(family="Consolas", size=28), 
            wrap="word",
            activate_scrollbars=True
        )
        self.text.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Premier scan des ports au démarrage
        self.refresh_ports()

    # ===== REFRESH PORTS =====
    def refresh_ports(self):
        ports = mido.get_input_names()
        if ports:
            self.dropdown.configure(values=ports)
            self.dropdown.set(ports[0])
        else:
            self.dropdown.configure(values=["Aucun appareil"])
            self.dropdown.set("Aucun appareil")

    # ===== START =====
    def start(self):
        if self.running:
            return

        port = self.dropdown.get()
        if not port or port == "Aucun appareil":
            self.status_label.configure(text="Sélectionnez un port valide", text_color="#e74c3c")
            return

        self.running = True
        self.status_label.configure(text="Écoute active...", text_color="#2ecc71")
        
        self.thread = threading.Thread(target=self.midi_loop, args=(port,), daemon=True)
        self.thread.start()

    # ===== STOP =====
    def stop(self):
        self.running = False
        self.status_label.configure(text="Statut : Arrêté", text_color="gray")
        # Note : mido se fermera proprement à la prochaine note ou lors de la coupure du flux

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
            # Utilisation de 'with' pour s'assurer que le port se ferme quoi qu'il arrive
            with mido.open_input(port) as self.inp:
                for msg in self.inp:
                    if not self.running:
                        break
                    if msg.type == "note_on" and msg.velocity > 0:
                        # Utilisation de root.after pour envoyer la note en toute sécurité à l'UI
                        self.root.after(0, lambda n=msg.note: self.on_midi_selected(n))
        except Exception as e:
            print("Erreur MIDI:", e)
            self.root.after(0, lambda: self.status_label.configure(text="Erreur de connexion", text_color="#e74c3c"))
            self.running = False

    # ===== FERMETURE PROPRE =====
    def on_closing(self):
        self.running = False
        self.root.destroy()

    def start_ui(self):
        self.root.mainloop()