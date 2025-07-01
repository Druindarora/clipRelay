import tkinter as tk
from utils.userSettings import load_user_settings
from services.audioService import handle_record
from services.vsCodeService import focus_vscode

from utils.utilsButtons import copy_chatrelay_prefix, copy_pollution, handle_send_chatgpt

def create_button(parent, image, text, command, compound="left", grid_options=None, pack_options=None):
    """
    Create a generic button.

    Args:
        parent (Tk or Frame): The parent UI element.
        image (PhotoImage): The image to display on the button.
        text (str): The text to display on the button.
        command (callable): The function to execute when the button is clicked.
        compound (str, optional): The position of the image relative to the text. Default is "left".
        grid_options (dict, optional): Options for grid layout (row, column, padx, pady, etc.).
        pack_options (dict, optional): Options for pack layout (padx, pady, etc.).

    Returns:
        Button: The created button.
    """
    button = tk.Button(parent, image=image, text=text, compound=compound, command=command)
    if grid_options:
        button.grid(**grid_options)
    elif pack_options:
        button.pack(**pack_options)
    return button

class ButtonStateManager:
    """
    A class to manage the state of buttons and labels in the UI.

    Attributes:
        root (Tk): The root UI element.
    """
    def __init__(self, root):
        """
        Initialize the ButtonStateManager.

        Args:
            root (Tk): The root UI element.
        """
        self.root = root

    def update_label(self, label_var_name, text):
        """
        Update the text of a label.

        Args:
            label_var_name (str): The name of the label variable.
            text (str): The text to set.

        Returns:
            None
        """
        if hasattr(self.root, label_var_name):
            getattr(self.root, label_var_name).set(text)

    def update_button_state(self, button_name, state):
        """
        Update the state of a button.

        Args:
            button_name (str): The name of the button.
            state (str): The state to set ("normal" or "disabled").

        Returns:
            None
        """
        if hasattr(self.root, button_name):
            getattr(self.root, button_name).config(state=state)

def create_mode1_buttons(root, recorder, audio_state):
    """
    Create buttons for mode 1.

    Args:
        root (Tk): The root UI element.
        recorder (AudioRecorder): The audio recorder instance.
        audio_state (dict): The state of the audio recording.

    Returns:
        None
    """
    state_manager = ButtonStateManager(root)

    user_settings = load_user_settings()
    duree = user_settings.get("duree_enregistrement", 60)
    minutes = duree // 60
    root.duree_var = tk.StringVar(value=f"Durée max : {minutes} min")
    duree_label = tk.Label(
        root.buttons_zone,
        textvariable=root.duree_var,
        font=("Arial", 10, "italic")
    )
    duree_label.pack()

    img_start_record = tk.PhotoImage(file="img/start.png")
    img_stop_record = tk.PhotoImage(file="img/record_2.png")
    root.img_start_record = img_start_record
    root.img_stop_record = img_stop_record

    record_btn = create_button(
        root.buttons_zone,
        image=img_start_record,
        text="Démarrer l'enregistrement",
        command=lambda: handle_record(
            root, recorder, audio_state,
            copy_prefix_btn,
            send_chatgpt_btn,
            getattr(root, "show_vscode_btn", None),
            record_btn,
            copy_pollution_btn
        ),
        pack_options={"pady": (10, 5)}
    )
    root.record_btn = record_btn

    root.timer_var = tk.StringVar(value="00:00")
    timer_label = tk.Label(root.buttons_zone, textvariable=root.timer_var, font=("Arial", 10))
    timer_label.pack()

    root.transcription_time_var = tk.StringVar(value="Temps de transcription : --")
    transcription_time_label = tk.Label(
        root.buttons_zone,
        textvariable=root.transcription_time_var,
        font=("Arial", 10, "italic")
    )
    transcription_time_label.pack()

    button_frame = tk.Frame(root.buttons_zone)
    button_frame.pack(pady=10)
    root.button_frame = button_frame

    img_pollution = tk.PhotoImage(file="img/copy.png")
    root.img_pollution = img_pollution
    copy_pollution_btn = create_button(
        button_frame,
        image=img_pollution,
        text="Copier pollution",
        command=lambda: copy_pollution(root),
        grid_options={"row": 0, "column": 0, "padx": 10}
    )
    root.copy_pollution_btn = copy_pollution_btn

    img_copy = tk.PhotoImage(file="img/copy.png")
    root.img_copy = img_copy
    copy_prefix_btn = create_button(
        button_frame,
        image=img_copy,
        text="Copier [ChatRelay]",
        command=lambda: copy_chatrelay_prefix(root),
        grid_options={"row": 0, "column": 1, "padx": 10}
    )
    root.copy_prefix_btn = copy_prefix_btn

    img_send = tk.PhotoImage(file="img/send.png")
    root.img_send = img_send
    send_chatgpt_btn = create_button(
        button_frame,
        image=img_send,
        text="Envoyer vers ChatGPT",
        command=lambda: handle_send_chatgpt(root),
        grid_options={"row": 0, "column": 2, "padx": 10}
    )
    root.send_chatgpt_btn = send_chatgpt_btn

    img_focus = tk.PhotoImage(file="img/Focus.png")
    root.img_focus = img_focus
    show_vscode_btn = create_button(
        button_frame,
        image=img_focus,
        text="Focus VS Code",
        command=lambda: focus_vscode(root),
        grid_options={"row": 0, "column": 3, "padx": 10}
    )
    root.show_vscode_btn = show_vscode_btn

def create_mode2_buttons(root):
    """
    Create buttons for mode 2.

    Args:
        root (Tk): The root UI element.

    Returns:
        None
    """

    # --- Bouton Sauvegarder normal ---
    def save_phrases():
        # Logique de sauvegarde à ajouter ici si besoin
        pass

    save_btn = tk.Button(
        root.buttons_zone,
        text="Sauvegarder",
        command=save_phrases
    )
    save_btn.pack(pady=10)

def createButtons(root, recorder, audio_state, mode=1):
    """
    Create buttons based on the selected mode.

    Args:
        root (Tk): The root UI element.
        recorder (AudioRecorder): The audio recorder instance.
        audio_state (dict): The state of the audio recording.
        mode (int): The mode to determine which buttons to create (1 or 2).

    Returns:
        None
    """

    # Détruit la zone précédente si elle existe
    if hasattr(root, "buttons_zone"):
        root.buttons_zone.destroy()
    root.buttons_zone = tk.Frame(root)
    root.buttons_zone.pack(pady=10)

    if mode == 2:
        create_mode2_buttons(root)
    else:
        create_mode1_buttons(root, recorder, audio_state)
