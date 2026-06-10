#!/usr/bin/env python3
import fcntl
import os
import signal
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

APP_ROOT = "/home/ngoctien/.openclaw/workspace/apps/linux-shimeji"
WINDOW_CONF = os.path.join(APP_ROOT, "window.conf")
TITLES_CONF = os.path.join(APP_ROOT, "titles.conf")
RUN_SCRIPT = os.path.join(APP_ROOT, "run-linux-shimeji.sh")
LOCK_FILE = "/tmp/linux-shimeji-settings.lock"

HEADER = "Put window offsets on the following lines in this order : x, y, width, height. No entry will default to 0."
DEFAULT_WINDOW = ["0", "0", "0", "0"]
_lock_handle = None


def acquire_single_instance_lock():
    global _lock_handle
    _lock_handle = open(LOCK_FILE, "w")
    try:
        fcntl.flock(_lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_handle.write(str(os.getpid()))
        _lock_handle.flush()
        return True
    except OSError:
        try:
            _lock_handle.seek(0)
            pid_text = _lock_handle.read().strip()
            if pid_text.isdigit():
                os.kill(int(pid_text), signal.SIGTERM)
        except Exception:
            pass
        return False


def read_window_conf():
    vals = DEFAULT_WINDOW[:]
    if os.path.exists(WINDOW_CONF):
        with open(WINDOW_CONF, "r", encoding="utf-8", errors="replace") as f:
            lines = [line.rstrip("\n") for line in f.readlines()]
        nums = [line.strip() for line in lines[1:] if line.strip()]
        for i in range(min(4, len(nums))):
            vals[i] = nums[i]
    return vals


def write_window_conf(vals):
    content = HEADER + "\n" + "\n".join(vals) + "\n"
    with open(WINDOW_CONF, "w", encoding="utf-8") as f:
        f.write(content)


def read_titles_conf():
    if not os.path.exists(TITLES_CONF):
        return ""
    with open(TITLES_CONF, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_titles_conf(text):
    with open(TITLES_CONF, "w", encoding="utf-8") as f:
        f.write(text)


def restart_shimeji():
    subprocess.run("pkill -f 'com.group_finity.mascot.Main'", shell=True)
    subprocess.Popen([RUN_SCRIPT], cwd=APP_ROOT)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Linux Shimeji Settings")
        self.geometry("640x520")
        self.minsize(620, 500)
        self.configure(padx=12, pady=12)
        self.option_add("*Font", "Sans 10")
        self._build()
        self.load_values()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        ttk.Label(top, text="Linux Shimeji Settings", font=("Sans", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Chỉnh vị trí bám cửa sổ và danh sách title được tương tác.").grid(row=1, column=0, sticky="w", pady=(4, 10))

        offsets = ttk.LabelFrame(self, text="window.conf")
        offsets.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for i in range(4):
            offsets.grid_columnconfigure(i, weight=1)

        self.entries = {}
        fields = [
            ("x offset", "x"),
            ("y offset", "y"),
            ("width add", "w"),
            ("height add", "h"),
        ]
        for idx, (label, key) in enumerate(fields):
            col = idx % 2
            row = idx // 2
            block = ttk.Frame(offsets)
            block.grid(row=row, column=col, sticky="ew", padx=10, pady=8)
            block.grid_columnconfigure(1, weight=1)
            ttk.Label(block, text=label, width=12).grid(row=0, column=0, sticky="w", padx=(0, 8))
            ent = ttk.Entry(block, width=12)
            ent.grid(row=0, column=1, sticky="w")
            self.entries[key] = ent

        ttk.Label(offsets, text="Save rồi bấm Restart Shimeji để thấy thay đổi.").grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))

        titles = ttk.LabelFrame(self, text="titles.conf")
        titles.grid(row=2, column=0, sticky="nsew")
        titles.grid_columnconfigure(0, weight=1)
        titles.grid_rowconfigure(1, weight=1)
        ttk.Label(titles, text="Mỗi dòng một title cửa sổ. Để trống = bám mọi cửa sổ.").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 6))

        text_wrap = ttk.Frame(titles)
        text_wrap.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        text_wrap.grid_columnconfigure(0, weight=1)
        text_wrap.grid_rowconfigure(0, weight=1)
        self.text = tk.Text(text_wrap, height=10, wrap="word")
        yscroll = ttk.Scrollbar(text_wrap, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=yscroll.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left")
        ttk.Button(buttons, text="Reset window.conf", command=self.reset_window).pack(side="left", padx=8)
        ttk.Button(buttons, text="Restart Shimeji", command=self.restart).pack(side="left")
        ttk.Button(buttons, text="Open App Folder", command=self.open_folder).pack(side="left", padx=8)
        ttk.Button(buttons, text="Close", command=self.destroy).pack(side="right")

    def load_values(self):
        vals = read_window_conf()
        for key, val in zip(["x", "y", "w", "h"], vals):
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, val)
        self.text.delete("1.0", "end")
        self.text.insert("1.0", read_titles_conf())

    def save(self):
        vals = [self.entries[k].get().strip() or "0" for k in ["x", "y", "w", "h"]]
        try:
            [int(v) for v in vals]
        except ValueError:
            messagebox.showerror("Invalid number", "4 ô window.conf phải là số nguyên.")
            return
        write_window_conf(vals)
        write_titles_conf(self.text.get("1.0", "end").rstrip() + "\n" if self.text.get("1.0", "end").strip() else "")
        messagebox.showinfo("Saved", "Đã lưu settings.")

    def reset_window(self):
        for key, val in zip(["x", "y", "w", "h"], DEFAULT_WINDOW):
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, val)

    def restart(self):
        self.save()
        try:
            restart_shimeji()
            messagebox.showinfo("Restarted", "Đã restart Linux Shimeji.")
        except Exception as e:
            messagebox.showerror("Restart failed", str(e))

    def open_folder(self):
        subprocess.Popen(["xdg-open", APP_ROOT])


if __name__ == "__main__":
    if not acquire_single_instance_lock():
        sys.exit(0)
    App().mainloop()
