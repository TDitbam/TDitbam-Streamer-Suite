import tkinter as tk
import customtkinter as ctk

class ContextMenu:
    """A reusable right-click context menu for CustomTkinter widgets."""
    
    @staticmethod
    def add_context_menu(widget):
        """Adds a standard context menu (Cut, Copy, Paste, Select All) to a widget."""
        # Theme-aware colors
        menu = tk.Menu(widget, tearoff=0, bg="#2B2B2B", fg="#DCE4EE", 
                       activebackground="#1F538D", activeforeground="white", 
                       borderwidth=0, font=("Segoe UI", 10))
        
        is_text = isinstance(widget, (ctk.CTkTextbox, tk.Text))
        
        def do_popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        def handle_cut():
            if str(widget.cget("state")) == "normal":
                widget.event_generate("<<Cut>>")

        def handle_paste():
            if str(widget.cget("state")) == "normal":
                widget.event_generate("<<Paste>>")

        menu.add_command(label="Cut", command=handle_cut)
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=handle_paste)
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: ContextMenu.select_all(widget))
        
        if is_text:
            menu.add_separator()
            menu.add_command(label="Clear All", command=lambda: ContextMenu.clear_all(widget))

        widget.bind("<Button-3>", do_popup)

    @staticmethod
    def select_all(widget):
        if isinstance(widget, (ctk.CTkTextbox, tk.Text)):
            widget.tag_add("sel", "1.0", "end")
        else:
            widget.select_range(0, "end")
            widget.icursor("end")
        widget.focus_set()
        return "break"

    @staticmethod
    def clear_all(widget):
        try:
            # Get current state safely
            old_state = str(widget.cget("state"))
            
            # Temporary enable to clear
            widget.configure(state="normal")
            
            if isinstance(widget, (ctk.CTkTextbox, tk.Text)):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, "end")
                
            # Restore state
            widget.configure(state=old_state)
        except Exception:
            # Fallback for underlying widgets
            try:
                if hasattr(widget, "_textbox"):
                    widget._textbox.configure(state="normal")
                    widget._textbox.delete("1.0", "end")
                    # We don't restore state on underlying widget as it might be complex
                elif hasattr(widget, "_entry"):
                    widget._entry.configure(state="normal")
                    widget._entry.delete(0, "end")
            except:
                pass
