# pip install ttkbootstrap
import os
import time
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import Sentence2WordBook as s2wb

LANG_CHOICES = ["en", "fr", "ja", "pt"]


def process_input(text: str, settings: dict) -> str:
    text = text.strip()
    if not text:
        return "Please enter some sentences."
    # langs = ", ".join(settings["languages"]
    #                   ) if settings["languages"] else "(none)"
    # model = settings["model_size"]
    # save_new = "ON" if settings["save_new_file"] else "OFF"
    # saving = "ON" if settings["save"] else "OFF"
    output = s2wb.get_output(text, settings)
    return output


class SettingsDialog(tb.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Settings")
        self.geometry("640x420")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        pad = tb.Frame(self, padding=16)
        pad.pack(fill=BOTH, expand=True)

        # Languages
        lang_box = tb.Labelframe(pad, text="Languages", padding=10)
        lang_box.pack(fill=X, pady=(0, 10))
        row = tb.Frame(lang_box)
        row.pack(fill=X)
        self.lang_vars = {}
        for i, lang in enumerate(LANG_CHOICES):
            var = tk.BooleanVar(value=parent.lang_vars[lang].get())
            self.lang_vars[lang] = var
            tb.Checkbutton(row, text=lang, variable=var, bootstyle=SUCCESS)\
              .grid(row=0, column=i, padx=6, pady=4, sticky="w")

        # Model
        model_box = tb.Labelframe(pad, text="Model", padding=10)
        model_box.pack(fill=X, pady=(0, 10))
        self.model_var = tk.StringVar(value=parent.model_var.get())
        for i, m in enumerate(["sm", "md", "lg"]):
            tb.Radiobutton(model_box, text=m, variable=self.model_var, value=m, bootstyle=INFO)\
              .grid(row=0, column=i, padx=6, pady=4, sticky="w")

        # Saving
        save_box = tb.Labelframe(pad, text="Output Saving", padding=10)
        save_box.pack(fill=X, pady=(0, 10))
        self.save_var = tk.BooleanVar(value=parent.save_var.get())
        self.save_new_file_var = tk.BooleanVar(
            value=parent.save_new_file_var.get())
        self.save_dir_var = tk.StringVar(value=parent.save_dir_var.get())

        tb.Checkbutton(save_box, text="Save output to file", variable=self.save_var, bootstyle=PRIMARY)\
          .grid(row=0, column=0, sticky="w", padx=4, pady=4)
        tb.Checkbutton(save_box, text="Save as new file if file exists", variable=self.save_new_file_var, bootstyle=SECONDARY)\
          .grid(row=0, column=1, sticky="w", padx=12, pady=4)

        tb.Label(save_box, text="Save directory:").grid(
            row=1, column=0, sticky="w", padx=4, pady=(8, 4))
        dir_row = tb.Frame(save_box)
        dir_row.grid(row=1, column=1, columnspan=2,
                     sticky="we", padx=4, pady=(8, 4))
        dir_row.columnconfigure(0, weight=1)
        tb.Entry(dir_row, textvariable=self.save_dir_var).grid(
            row=0, column=0, sticky="we", padx=(0, 6))
        tb.Button(dir_row, text="Browse…", bootstyle=SECONDARY,
                  command=self.browse_dir).grid(row=0, column=1)

        # Actions
        actions = tb.Frame(pad)
        actions.pack(fill=X, pady=(8, 0))
        tb.Button(actions, text="Cancel", bootstyle=SECONDARY,
                  command=self.destroy).pack(side=RIGHT)
        tb.Button(actions, text="Apply", bootstyle=PRIMARY,
                  command=self.apply).pack(side=RIGHT, padx=(0, 8))
        self.bind("<Escape>", lambda e: self.destroy())

    def browse_dir(self):
        d = filedialog.askdirectory(parent=self, title="Choose save directory")
        if d:
            self.save_dir_var.set(d)

    def apply(self):
        for lang, var in self.lang_vars.items():
            self.parent.lang_vars[lang].set(var.get())
        self.parent.model_var.set(self.model_var.get())
        self.parent.save_var.set(self.save_var.get())
        self.parent.save_new_file_var.set(self.save_new_file_var.get())
        self.parent.save_dir_var.set(self.save_dir_var.get())
        self.destroy()


class App(tb.Window):
    def __init__(self):
        super().__init__(themename="minty")
        self.title("Wordbook Maker v1.0.0")
        self.geometry("960x700")
        self.place_window_center()

        # state
        self.lang_vars = {lang: tk.BooleanVar(
            value=lang in LANG_CHOICES) for lang in LANG_CHOICES}
        self.model_var = tk.StringVar(value="md")
        self.save_var = tk.BooleanVar(value=False)
        self.save_new_file_var = tk.BooleanVar(value=False)
        self.save_dir_var = tk.StringVar(value="")

        # ===== Nav Bar =====
        navbar = tb.Frame(self, padding=(14, 10))
        navbar.pack(fill=X, side=TOP)
        tb.Label(navbar, text="Wordbook Maker v1.0.0",
                 font=("", 12, "bold")).pack(side=LEFT)
        tb.Button(navbar, text="Settings", bootstyle=INFO,
                  command=self.open_settings).pack(side=RIGHT)
        tb.Separator(self, orient="horizontal").pack(fill=X)

        # ===== Main content =====
        rootpad = tb.Frame(self, padding=18)
        rootpad.pack(fill=BOTH, expand=True)

        # INPUT
        tb.Label(rootpad, text="Input", bootstyle=INFO).pack(anchor="w")
        in_wrap = tb.Frame(rootpad)
        in_wrap.pack(fill=X, pady=(6, 10))
        in_wrap.columnconfigure(0, weight=1)
        self.inbox = tk.Text(in_wrap, height=10, wrap="word", relief="flat")
        self.inbox.grid(row=0, column=0, sticky="we")
        in_scroll = tb.Scrollbar(
            in_wrap, orient="vertical", command=self.inbox.yview)
        in_scroll.grid(row=0, column=1, sticky="nsw")
        self.inbox.configure(yscrollcommand=in_scroll.set)
        self.inbox.focus_set()

        # RUN button (centered, 1/3 width)
        self.run_row = tb.Frame(rootpad)
        self.run_row.pack(fill=X, pady=(0, 14))
        for c in range(3):
            self.run_row.columnconfigure(c, weight=1)
        self.run_holder = tb.Frame(self.run_row, height=48)
        self.run_holder.grid(row=0, column=1, sticky="n")
        self.run_holder.grid_propagate(False)
        self.run_btn = tb.Button(
            self.run_holder, text="RUN ▶", bootstyle=PRIMARY, command=self.on_submit)
        self.run_btn.pack(fill=BOTH, expand=True)
        tb.Separator(rootpad, orient="horizontal").pack(fill=X, pady=(0, 6))

        # RESPONSE
        tb.Label(rootpad, text="Response", bootstyle=SUCCESS).pack(anchor="w")
        out_wrap = tb.Frame(rootpad)
        out_wrap.pack(fill=BOTH, expand=True, pady=(6, 8))
        out_wrap.columnconfigure(0, weight=1)
        out_wrap.rowconfigure(0, weight=1)
        self.outbox = tk.Text(out_wrap, height=12,
                              wrap="word", state="disabled", relief="flat")
        self.outbox.grid(row=0, column=0, sticky="nsew")
        out_scroll = tb.Scrollbar(
            out_wrap, orient="vertical", command=self.outbox.yview)
        out_scroll.grid(row=0, column=1, sticky="nsw")
        self.outbox.configure(yscrollcommand=out_scroll.set)

        # Clear Response button (centered, 1/3 width)
        self.clear_row = tb.Frame(rootpad)
        self.clear_row.pack(fill=X, pady=(0, 6))
        for c in range(3):
            self.clear_row.columnconfigure(c, weight=1)
        self.clear_holder = tb.Frame(self.clear_row, height=48)
        self.clear_holder.grid(row=0, column=1, sticky="n")
        self.clear_holder.grid_propagate(False)
        self.clear_btn = tb.Button(
            self.clear_holder, text="Clear Response", bootstyle=SECONDARY, command=self.clear_response)
        self.clear_btn.pack(fill=BOTH, expand=True)

        # bindings
        self.inbox.bind("<Return>", self.on_submit)
        self.inbox.bind("<Control-Return>", self.on_submit)
        self.inbox.bind("<Command-Return>", self.on_submit)
        self.inbox.bind("<Meta-Return>", self.on_submit)
        self.bind("<Escape>", lambda e: self.destroy())

        # equal widths
        self.bind("<Configure>", self._on_resize)
        self.after(50, self._on_resize)

    def _on_resize(self, event=None):
        w = max(260, int(self.winfo_width() / 3))
        self.run_holder.configure(width=w)
        self.clear_holder.configure(width=w)

    def open_settings(self):
        SettingsDialog(self)

    def gather_settings(self) -> dict:
        return {
            "languages": [lang for lang, var in self.lang_vars.items() if var.get()],
            "model_size": self.model_var.get(),
            "save": self.save_var.get(),
            "save_new_file": self.save_new_file_var.get(),
            "save_dir": self.save_dir_var.get().strip(),
        }

    def on_submit(self, event=None):
        text = self.inbox.get("1.0", "end-1c")
        settings = self.gather_settings()
        resp = process_input(text, settings)

        self.outbox.config(state="normal")
        self.outbox.delete("1.0", "end")
        self.outbox.insert("end", resp)
        self.outbox.config(state="disabled")
        # print(resp)

        if settings["save"] and settings["save_dir"]:
            self._save_response(
                resp, settings["save_dir"], settings["save_new_file"])

        return "break" if isinstance(event, tk.Event) else None

    def _save_response(self, content: str, directory: str, save_new_file: bool):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception:
            return
        path = os.path.join(directory, "output.txt")
        if save_new_file and os.path.exists(path):
            ts = time.strftime("%Y%m%d-%H%M%S")
            path = os.path.join(directory, f"output_{ts}.txt")
        self._write_text(path, content)

    def _write_text(self, path: str, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def clear_response(self):
        self.outbox.config(state="normal")
        self.outbox.delete("1.0", "end")
        self.outbox.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
