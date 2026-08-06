import tkinter as tk
import customtkinter as ctk

class ContextMenu:
    """A reusable right-click context menu for CustomTkinter widgets."""
    
    @staticmethod
    def _get_internal_widget(widget):
        """Returns the internal standard tkinter widget if it exists."""
        if hasattr(widget, "_textbox"):
            return widget._textbox
        if hasattr(widget, "_entry"):
            return widget._entry
        return widget

    @staticmethod
    def add_context_menu(widget):
        """Adds a standard context menu (Cut, Copy, Paste, Select All) to a widget."""
        menu = tk.Menu(widget, tearoff=0, bg="#2B2B2B", fg="#DCE4EE", 
                       activebackground="#1F538D", activeforeground="white", 
                       borderwidth=0, font=("Segoe UI", 10))
        
        is_text = isinstance(widget, (ctk.CTkTextbox, tk.Text))
        target = ContextMenu._get_internal_widget(widget)

        def do_popup(event):
            # Focus widget on right click
            widget.focus_set()
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        def handle_cut():
            if str(widget.cget("state")) == "normal":
                target.event_generate("<<Cut>>")

        def handle_copy():
            # Copy should work even if disabled (for log boxes)
            target.event_generate("<<Copy>>")

        def handle_paste():
            if str(widget.cget("state")) == "normal":
                target.event_generate("<<Paste>>")

        root = widget.winfo_toplevel()
        tr = getattr(root, "tr", lambda text: text)
        menu.add_command(label=tr("Cut"), command=handle_cut)
        menu.add_command(label=tr("Copy"), command=handle_copy)
        menu.add_command(label=tr("Paste"), command=handle_paste)
        menu.add_separator()
        menu.add_command(label=tr("Select All"), command=lambda: ContextMenu.select_all(widget))
        
        if is_text:
            menu.add_separator()
            menu.add_command(label=tr("Clear All"), command=lambda: ContextMenu.clear_all(widget))

        widget.bind("<Button-3>", do_popup)

    @staticmethod
    def select_all(widget):
        widget.focus_set()
        if isinstance(widget, (ctk.CTkTextbox, tk.Text)):
            widget.tag_add("sel", "1.0", "end")
        else:
            widget.select_range(0, "end")
            widget.icursor("end")
        return "break"

    @staticmethod
    def clear_all(widget):
        try:
            old_state = str(widget.cget("state"))
            widget.configure(state="normal")
            
            if isinstance(widget, (ctk.CTkTextbox, tk.Text)):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, "end")
                
            widget.configure(state=old_state)
        except Exception:
            try:
                target = ContextMenu._get_internal_widget(widget)
                target.configure(state="normal")
                if hasattr(target, "delete"):
                    if isinstance(target, tk.Text):
                        target.delete("1.0", "end")
                    else:
                        target.delete(0, "end")
            except:
                pass
