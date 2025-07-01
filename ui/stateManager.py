class StateManager:
    """
    A class to manage the state of buttons and labels in the UI.

    Attributes:
        root (Tk): The root UI element.
    """
    def __init__(self, root):
        """
        Initialize the StateManager.

        Args:
            root (Tk): The root UI element.
        """
        self.root = root
        self.buttons = []
        self.status_label = root.status_label

    def register_buttons(self, *buttons):
        """
        Register buttons to be managed by the state manager.

        Args:
            *buttons: The buttons to register.

        Returns:
            None
        """
        self.buttons.extend(buttons)

    def set_buttons_state(self, state):
        """
        Set the state of the registered buttons.

        Args:
            state (str): The state to set ("normal" or "disabled").

        Returns:
            None
        """
        for btn in self.buttons:
            if btn:
                btn.config(state=state)

    def update_status(self, text, color):
        """
        Update the status label text and color.

        Args:
            text (str): The text to set.
            color (str): The color to set (e.g., "red", "green").

        Returns:
            None
        """
        self.status_label.config(text=text, fg=color)