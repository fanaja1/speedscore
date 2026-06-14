import customtkinter as ctk
import mido
import threading

# Configuration du thème sombre haut de gamme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SpeedScoreUI:
    def __init__(self, on_midi_selected):
        self.on_midi_selected = on_midi_selected
        self.running = False
        self.thread = None
        self.inp = None
        
        # Gestion de la taille de la police (Zoom)
        self.font_size = 32

        # Fenêtre Principale
        self.root = ctk.CTk()
        self.root.title("SpeedScore — Realtime MIDI Dashboard")
        self.root.geometry("1000x600")
        self.root.minsize(850, 500)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Grille principale : Sidebar (0) | Contenu Principal (1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. BARRE LATÉRALE (SIDEBAR)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color="#1e1e24")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Titre
        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚡ SPEEDSCORE", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        )
        self.title_label.pack(pady=(35, 20), padx=20)

        # --- SECTION CONFIGURATION ---
        self.config_box = ctk.CTkFrame(self.sidebar, fg_color="#2a2a35", corner_radius=10)
        self.config_box.pack(pady=10, padx=15, fill="x")

        self.label = ctk.CTkLabel(self.config_box, text="ENTRÉE MIDI", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a0a0b0")
        self.label.pack(pady=(10, 2), padx=15, anchor="w")
        
        self.dropdown = ctk.CTkComboBox(self.config_box, values=[""], height=35, fg_color="#1e1e24", border_color="#3a3a4a")
        self.dropdown.pack(pady=(0, 10), padx=15, fill="x")

        self.refresh_btn = ctk.CTkButton(
            self.config_box, 
            text="🔄 Scanner les ports", 
            height=30,
            fg_color="transparent", 
            border_width=1, 
            border_color="#4a4a5a",
            hover_color="#3a3a4a",
            command=self.refresh_ports
        )
        self.refresh_btn.pack(pady=(0, 12), padx=15, fill="x")

        # --- CONTROLES DE FLUX ---
        self.start_btn = ctk.CTkButton(
            self.sidebar, 
            text="▶ START", 
            height=40,
            fg_color="#2ec4b6", 
            hover_color="#20a497", 
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start
        )
        self.start_btn.pack(pady=(15, 8), padx=15, fill="x")

        self.stop_btn = ctk.CTkButton(
            self.sidebar, 
            text="■ STOP", 
            height=40,
            fg_color="#ff206e", 
            hover_color="#d61b5c",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.stop
        )
        self.stop_btn.pack(pady=8, padx=15, fill="x")

        # --- NOUVELLE SECTION : ÉDITION & TEXTE ---
        self.text_tools_box = ctk.CTkFrame(self.sidebar, fg_color="#2a2a35", corner_radius=10)
        self.text_tools_box.pack(pady=10, padx=15, fill="x")

        self.tools_label = ctk.CTkLabel(self.text_tools_box, text="OPTIONS DE TEXTE", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a0a0b0")
        self.tools_label.pack(pady=(10, 5), padx=15, anchor="w")

        # Bouton Effacer la dernière note
        self.delete_last_btn = ctk.CTkButton(
            self.text_tools_box, 
            text="⌫ Effacer dernière note", 
            height=32,
            fg_color="#3a3a4a", 
            hover_color="#4a4a5a",
            command=self.delete_last_note
        )
        self.delete_last_btn.pack(pady=5, padx=15, fill="x")

        # Bouton Tout Nettoyer (ancien RESET)
        self.reset_btn = ctk.CTkButton(
            self.text_tools_box, 
            text="🗑️ Tout nettoyer", 
            height=32,
            fg_color="#3a3a4a", 
            hover_color="#c0392b", # Devient rouge foncé au survol pour sécurité
            command=self.reset
        )
        self.reset_btn.pack(pady=5, padx=15, fill="x")

        # Layout pour Zoom / Dézoom (côte à côte)
        self.zoom_frame = ctk.CTkFrame(self.text_tools_box, fg_color="transparent")
        self.zoom_frame.pack(pady=(5, 12), padx=15, fill="x")

        self.zoom_out_btn = ctk.CTkButton(
            self.zoom_frame, 
            text="🔍 -", 
            width=70,
            height=32,
            fg_color="#3a3a4a", 
            hover_color="#4a4a5a",
            command=self.zoom_out
        )
        self.zoom_out_btn.pack(side="left", expand=True, padx=(0, 5))

        self.zoom_in_btn = ctk.CTkButton(
            self.zoom_frame, 
            text="🔍 +", 
            width=70,
            height=32,
            fg_color="#3a3a4a", 
            hover_color="#4a4a5a",
            command=self.zoom_in
        )
        self.zoom_in_btn.pack(side="right", expand=True, padx=(5, 0))


        # --- STATUT EN BAS ---
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.pack(side="bottom", pady=20, padx=15, fill="x")
        
        self.status_dot = ctk.CTkLabel(self.status_frame, text="●", text_color="#ff206e", font=ctk.CTkFont(size=16))
        self.status_dot.pack(side="left", padx=(10, 5))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Déconnecté", text_color="#808090", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left")

        # ==========================================
        # 2. ZONE CENTRALE D'AFFICHAGE
        # ==========================================
        self.main_container = ctk.CTkFrame(self.root, fg_color="#121214", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.display_card = ctk.CTkFrame(self.main_container, fg_color="#1e1e24", corner_radius=16)
        self.display_card.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")
        self.display_card.grid_columnconfigure(0, weight=1)
        self.display_card.grid_rowconfigure(1, weight=1)

        self.card_title = ctk.CTkLabel(
            self.display_card, 
            text="FLUX DE NOTES CONVERTIES", 
            font=ctk.CTkFont(size=11, weight="bold"), 
            text_color="#707080"
        )
        self.card_title.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

        # Zone de texte principale
        self.text = ctk.CTkTextbox(
            self.display_card, 
            font=ctk.CTkFont(family="Consolas", size=self.font_size, weight="bold"), 
            fg_color="#121214",
            text_color="#2ec4b6",  
            wrap="word",
            activate_scrollbars=True,
            border_width=1,
            border_color="#2a2a35"
        )
        self.text.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew")

        self.refresh_ports()

    # ===== REFRESH PORTS =====
    def refresh_ports(self):
        ports = mido.get_input_names()
        if ports:
            self.dropdown.configure(values=ports)
            self.dropdown.set(ports[0])
        else:
            self.dropdown.configure(values=["Aucun périphérique"])
            self.dropdown.set("Aucun périphérique")

    # ===== START =====
    def start(self):
        if self.running:
            return

        port = self.dropdown.get()
        if not port or port == "Aucun périphérique":
            self.update_status("Erreur de port", "#ff206e")
            return

        self.running = True
        self.update_status("Écoute active", "#2ec4b6")
        
        self.thread = threading.Thread(target=self.midi_loop, args=(port,), daemon=True)
        self.thread.start()

    # ===== STOP =====
    def stop(self):
        self.running = False
        self.update_status("Arrêté", "#ff9f1c")

    # ===== RESET =====
    def reset(self):
        self.text.delete("1.0", "end")

    # ===== EFFACER DERNIÈRE NOTE =====
    def delete_last_note(self):
        # Récupère tout le contenu actuel (Tkinter ajoute un \n invisible à la fin d'où le -2c)
        content = self.text.get("1.0", "end-1c").rstrip()
        if content:
            # Trouve le dernier espace pour couper proprement la dernière note complète
            last_space = content.rfind(" ")
            if last_space != -1:
                self.text.delete(f"1.0 + {last_space + 1} chars", "end")
            else:
                self.text.delete("1.0", "end")

    # ===== ZOOM / DEZOOM =====
    def zoom_in(self):
        if self.font_size < 72: # Limite max raisonnable
            self.font_size += 4
            self.text.configure(font=ctk.CTkFont(family="Consolas", size=self.font_size, weight="bold"))

    def zoom_out(self):
        if self.font_size > 12: # Limite min pour rester lisible
            self.font_size -= 4
            self.text.configure(font=ctk.CTkFont(family="Consolas", size=self.font_size, weight="bold"))

    # ===== ADD NOTE =====
    def add_note(self, note):
        if not self.running:
            return
        self.text.insert("end", note + " ")
        self.text.see("end")

    # ===== HELPER STATUS =====
    def update_status(self, text, color):
        self.status_label.configure(text=text)
        self.status_dot.configure(text_color=color)

    # ===== MIDI LOOP =====
    def midi_loop(self, port):
        try:
            with mido.open_input(port) as self.inp:
                for msg in self.inp:
                    if not self.running:
                        break
                    if msg.type == "note_on" and msg.velocity > 0:
                        self.root.after(0, lambda n=msg.note: self.on_midi_selected(n))
        except Exception as e:
            print("Erreur MIDI:", e)
            self.root.after(0, lambda: self.update_status("Erreur connexion", "#ff206e"))
            self.running = False

    def on_closing(self):
        self.running = False
        self.root.destroy()

    def start_ui(self):
        self.root.mainloop()