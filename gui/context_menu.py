import tkinter as tk
import customtkinter as ctk

class ContextMenu:
    """A reusable right-click context menu for CustomTkinter widgets."""
    
    @staticmethod
    def add_context_menu(widget):
        """Adds a standard context menu (Cut, Copy, Paste, Select All) to a widget."""
        menu = tk.Menu(widget, tearoff=0, bg="#2D2D2D", fg="white", activebackground="#4682B4", borderwidth=0)
        
        # Determine if widget is a Text/Textbox (multiline) or Entry
        is_text = isinstance(widget, (ctk.CTkTextbox, tk.Text))
        
        def do_popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        # Build Menu
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: ContextMenu.select_all(widget))
        
        if is_text:
            menu.add_separator()
            menu.add_command(label="Clear All", command=lambda: ContextMenu.clear_all(widget))

        # Bind Right Click (Windows/Linux: <Button-3>, macOS: <Button-2> or <Control-Button-1>)
        widget.bind("<Button-3>", do_popup)

    @staticmethod
    def select_all(widget):
        if isinstance(widget, (ctk.CTkTextbox, tk.Text)):
            widget.tag_add("sel", "1.0", "end")
        else:
            widget.select_range(0, "end")
            widget.icursor("end")
        return "break"

    @staticmethod
    def clear_all(widget):
        if isinstance(widget, (ctk.CTkTextbox, tk.Text)):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            # If it's meant to be disabled (like a log box), it should stay disabled after clear
            # But the caller usually handles that.
        else:
            widget.delete(0, "end")
