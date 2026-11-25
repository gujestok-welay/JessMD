import ctypes
import os
import re
import sys
import threading
import traceback

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

base_tcl_dir = os.path.join(sys.base_prefix, "tcl")
if os.path.isdir(base_tcl_dir):
    for folder in os.listdir(base_tcl_dir):
        full_path = os.path.join(base_tcl_dir, folder)
        if folder.startswith("tcl8") and os.path.isdir(full_path):
            os.environ.setdefault("TCL_LIBRARY", full_path)
        elif folder.startswith("tk8") and os.path.isdir(full_path):
            os.environ.setdefault("TK_LIBRARY", full_path)

# Pastikan folder JessMD masuk ke sys.path agar ocr_helper bisa diimpor saat dipanggil dari Explorer
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

def show_message(title: str, text: str, icon: int = 0x10):
    ctypes.windll.user32.MessageBoxW(0, text, title, icon)

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls",
    ".csv", ".html", ".htm", ".txt", ".json", ".xml", ".epub"
}

def clean_markdown_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()

def truncate_filename(filename: str, max_len: int = 38) -> str:
    if len(filename) <= max_len:
        return filename
    name, ext = os.path.splitext(filename)
    return f"{name[:max_len - len(ext) - 3]}...{ext}"

def run_conversion_with_popup(input_path: str):
    import tkinter as tk
    from tkinter import ttk
    from markitdown import MarkItDown
    from ocr_helper import convert_document

    base_path, _ = os.path.splitext(input_path)
    output_path = f"{base_path}.md"
    filename = os.path.basename(input_path)
    result_state = {"error": None}

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg="#1e1e2e")

    width, height = 340, 105
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    pos_x = (screen_w // 2) - (width // 2)
    pos_y = (screen_h // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    frame = tk.Frame(
        root,
        bg="#1e1e2e",
        highlightbackground="#45475a",
        highlightthickness=1,
        padx=18,
        pady=14
    )
    frame.pack(fill="both", expand=True)

    lbl_title = tk.Label(
        frame,
        text="JessMD — Mengonversi ke Markdown...",
        font=("Segoe UI", 10, "bold"),
        fg="#cdd6f4",
        bg="#1e1e2e",
        anchor="w"
    )
    lbl_title.pack(fill="x")

    lbl_file = tk.Label(
        frame,
        text=truncate_filename(filename),
        font=("Segoe UI", 9),
        fg="#a6adc8",
        bg="#1e1e2e",
        anchor="w",
        pady=4
    )
    lbl_file.pack(fill="x")

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor="#313244",
        background="#89b4fa",
        bordercolor="#313244",
        lightcolor="#89b4fa",
        darkcolor="#89b4fa",
        thickness=6
    )

    progress = ttk.Progressbar(
        frame,
        style="Custom.Horizontal.TProgressbar",
        mode="indeterminate",
        length=300
    )
    progress.pack(fill="x", pady=(4, 0))
    progress.start(12)

    def worker():
        try:
            converter = MarkItDown()
            md_text, _ = convert_document(input_path, converter)
            md_text = clean_markdown_text(md_text)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_text)
        except Exception as e:
            result_state["error"] = str(e)
        finally:
            root.after(0, root.destroy)

    threading.Thread(target=worker, daemon=True).start()
    root.mainloop()

    if result_state["error"]:
        show_message(
            "JessMD — Gagal Mengonversi",
            f"Terjadi kesalahan saat mengonversi file:\n{filename}\n\nDetail: {result_state['error']}",
            0x10
        )

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        return

    _, ext = os.path.splitext(input_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        show_message(
            "JessMD — Format Tidak Didukung",
            f"Format file '{ext}' tidak didukung untuk konversi Markdown.",
            0x30
        )
        return

    run_conversion_with_popup(input_path)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        err_detail = traceback.format_exc()
        log_path = os.path.join(SCRIPT_DIR, "jessmd_error.log")
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write(err_detail)
        show_message(
            "JessMD — Error Sistem",
            f"Aplikasi mengalami error. Detail tersimpan di jessmd_error.log:\n\n{err_detail[:400]}",
            0x10
        )