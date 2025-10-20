# pip install ttkbootstrap
import os
import time
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *

LANG_CHOICES = ["en", "fr", "ja", "pt"]


def process_input(text: str, settings: dict) -> str:
    text = text.strip()
    if not text:
        return "Please enter some text."
    langs = ", ".join(settings["languages"]
                      ) if settings["languages"] else "(none)"
    model = settings["model_size"]
    saving = "ON" if settings["save"] else "OFF"
    overwrite = "ON" if settings["overwrite"] else "OFF"
    prompt_info = f"create_prompt=ON, path={settings['prompt_path']}" if settings[
        "create_prompt"] else "create_prompt=OFF"
    return (
        f"Processed → {text[::-1]}  | len={len(text)}\n"
        f"[Settings] languages=[{langs}] | model={model} | save={saving} "
        f"| overwrite={overwrite} | dir={settings['save_dir'] or '(n/a)'} | {prompt_info}"
    )


class SettingsDialog(tb.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Settings")
        self.geometry("640x460")
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
        self.overwrite_var = tk.BooleanVar(value=parent.overwrite_var.get())
        self.save_dir_var = tk.StringVar(value=parent.save_dir_var.get())

        tb.Checkbutton(save_box, text="Save output to file", variable=self.save_var, bootstyle=PRIMARY)\
          .grid(row=0, column=0, sticky="w", padx=4, pady=4)
        tb.Checkbutton(save_box, text="Overwrite if file exists", variable=self.overwrite_var, bootstyle=SECONDARY)\
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

        # Prompt
        prompt_box = tb.Labelframe(pad, text="Prompt", padding=10)
        prompt_box.pack(fill=X, pady=(0, 10))
        self.create_prompt_var = tk.BooleanVar(
            value=parent.create_prompt_var.get())
        self.prompt_path_var = tk.StringVar(value=parent.prompt_path_var.get())

        tb.Checkbutton(prompt_box, text="Create prompt file", variable=self.create_prompt_var, bootstyle=WARNING)\
          .grid(row=0, column=0, sticky="w", padx=4, pady=4)

        tb.Label(prompt_box, text="Prompt file path:").grid(
            row=1, column=0, sticky="w", padx=4, pady=(8, 4))
        p_row = tb.Frame(prompt_box)
        p_row.grid(row=1, column=1, columnspan=2,
                   sticky="we", padx=4, pady=(8, 4))
        p_row.columnconfigure(0, weight=1)
        tb.Entry(p_row, textvariable=self.prompt_path_var).grid(
            row=0, column=0, sticky="we", padx=(0, 6))
        tb.Button(p_row, text="Browse…", bootstyle=SECONDARY,
                  command=self.browse_prompt).grid(row=0, column=1)

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

    def browse_prompt(self):
        p = filedialog.asksaveasfilename(parent=self, title="Choose prompt file path",
                                         defaultextension=".txt",
                                         filetypes=[("Text", "*.txt"), ("All files", "*.*")])
        if p:
            self.prompt_path_var.set(p)

    def apply(self):
        for lang, var in self.lang_vars.items():
            self.parent.lang_vars[lang].set(var.get())
        self.parent.model_var.set(self.model_var.get())
        self.parent.save_var.set(self.save_var.get())
        self.parent.overwrite_var.set(self.overwrite_var.get())
        self.parent.save_dir_var.set(self.save_dir_var.get())
        self.parent.create_prompt_var.set(self.create_prompt_var.get())
        self.parent.prompt_path_var.set(self.prompt_path_var.get())
        self.destroy()


class App(tb.Window):
    def __init__(self):
        super().__init__(themename="minty")
        self.title("Wordbook Maker v1.0.0")
        self.geometry("960x700")
        self.place_window_center()

        # state
        self.lang_vars = {lang: tk.BooleanVar(
            value=lang in ["en", "ja"]) for lang in LANG_CHOICES}
        self.model_var = tk.StringVar(value="md")
        self.save_var = tk.BooleanVar(value=False)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.save_dir_var = tk.StringVar(value="")
        self.create_prompt_var = tk.BooleanVar(value=False)
        self.prompt_path_var = tk.StringVar(value="")

        # ===== Nav Bar =====
        navbar = tb.Frame(self, padding=(14, 10))
        navbar.pack(fill=X, side=TOP)
        tb.Label(navbar, text="Wordbook Maker v1.0.0",
                 font=("", 12, "bold")).pack(side=LEFT)
        tb.Button(navbar, text="Settings", bootstyle=INFO,
                  command=self.open_settings).pack(side=RIGHT)

        # --- Separator between Nav Bar and Input ---
        tb.Separator(self, orient="horizontal").pack(fill=X)

        # ===== Main content =====
        rootpad = tb.Frame(self, padding=18)
        rootpad.pack(fill=BOTH, expand=True)

        # INPUT
        tb.Label(rootpad, text="Enter Sentences\n(enter sentence(s) in any of the language selected)",
                 bootstyle=INFO).pack(anchor="w")
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

        # RUN centered with width = 1/3 of window (fixed height for clickability)
        self.run_row = tb.Frame(rootpad)
        self.run_row.pack(fill=X, pady=(0, 14))
        for c in range(3):
            self.run_row.columnconfigure(c, weight=1)
        self.run_holder = tb.Frame(self.run_row, height=48)      # give height
        self.run_holder.grid(row=0, column=1, sticky="n")
        self.run_holder.grid_propagate(
            False)                     # keep our size
        self.run_btn = tb.Button(
            self.run_holder, text="RUN ▶", bootstyle=PRIMARY, command=self.on_submit)
        self.run_btn.pack(fill=BOTH, expand=True)

        # --- Separator between RUN and Response ---
        # tb.Separator(rootpad, orient="horizontal").pack(fill=X, pady=(0, 6))

        # RESPONSE (scrollable)
        tb.Label(rootpad, text="Wordbook Output\n(the response may include errors)",
                 bootstyle=SUCCESS).pack(anchor="w")
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

        # Clear Response centered with width = 1/3 of window (fixed height)
        self.clear_row = tb.Frame(rootpad)
        self.clear_row.pack(fill=X, pady=(0, 6))
        for c in range(3):
            self.clear_row.columnconfigure(c, weight=1)
        self.clear_holder = tb.Frame(self.clear_row, height=48)
        self.clear_holder.grid(row=0, column=1, sticky="n")
        self.clear_holder.grid_propagate(False)
        self.clear_btn = tb.Button(
            self.clear_holder, text="Clear Output", bootstyle=SECONDARY, command=self.clear_response)
        self.clear_btn.pack(fill=BOTH, expand=True)

        # keys
        self.inbox.bind("<Return>", self.on_submit)
        # self.inbox.bind("<Control-Return>", self.on_submit)
        self.inbox.bind("<Command-Return>", self.on_submit)  # macOS
        # macOS alt mapping
        # self.inbox.bind("<Meta-Return>", self.on_submit)
        self.bind("<Escape>", lambda e: self.destroy())

        # keep buttons equal width = 1/3 window
        self.bind("<Configure>", self._on_resize)
        self.after(50, self._on_resize)  # initial sizing after layout

    def _on_resize(self, event=None):
        # target width ~ 1/3 of current window width; clamp to sensible min
        w = max(260, int(self.winfo_width() / 3))
        self.run_holder.configure(width=w)
        self.clear_holder.configure(width=w)
        # height already set to 48 to avoid "flattened" look and ensure clickability

    def open_settings(self):
        SettingsDialog(self)

    def gather_settings(self) -> dict:
        return {
            "languages": [lang for lang, var in self.lang_vars.items() if var.get()],
            "model_size": self.model_var.get(),
            "save": self.save_var.get(),
            "overwrite": self.overwrite_var.get(),
            "save_dir": self.save_dir_var.get().strip(),
            "create_prompt": self.create_prompt_var.get(),
            "prompt_path": self.prompt_path_var.get().strip(),
        }

    def on_submit(self, event=None):
        text = self.inbox.get("1.0", "end-1c")
        settings = self.gather_settings()
        resp = process_input(text, settings)

        self.outbox.config(state="normal")
        self.outbox.delete("1.0", "end")
        self.outbox.insert("end", resp)
        self.outbox.config(state="disabled")
        print(resp)

        if settings["save"] and settings["save_dir"]:
            self._save_response(
                resp, settings["save_dir"], settings["overwrite"])
        if settings["create_prompt"] and settings["prompt_path"]:
            self._write_text(settings["prompt_path"], text, overwrite=True)

        return "break" if isinstance(event, tk.Event) else None

    def _save_response(self, content: str, directory: str, overwrite: bool):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception:
            return
        path = os.path.join(directory, "output.txt")
        if not overwrite and os.path.exists(path):
            ts = time.strftime("%Y%m%d-%H%M%S")
            path = os.path.join(directory, f"output_{ts}.txt")
        self._write_text(path, content, overwrite=True)

    def _write_text(self, path: str, content: str, overwrite: bool):
        mode = "w" if overwrite else "x"
        try:
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)
        except FileExistsError:
            base, ext = os.path.splitext(path)
            with open(f"{base}_{int(time.time())}{ext}", "w", encoding="utf-8") as f:
                f.write(content)

    def clear_response(self):
        self.outbox.config(state="normal")
        self.outbox.delete("1.0", "end")
        self.outbox.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
