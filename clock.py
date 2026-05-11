import tkinter as tk
from tkinter import messagebox, colorchooser, ttk, font
import json
import os
import locale
from time import strftime
import sys

# --- 1. XỬ LÝ ĐƯỜNG DẪN CONFIG ---
def get_config_path():
    if hasattr(sys, '_MEIPASS'):
        # Nếu đang chạy file .exe build từ PyInstaller
        return os.path.join(os.path.dirname(sys.executable), "config.json")
    # Nếu đang chạy file .py bình thường
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

CONFIG_FILE = get_config_path()

# --- 2. THIẾT LẬP NGÔN NGỮ ---
try:
    locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'vi_VN')
    except:
        pass

# --- 3. HÀM CẤU HÌNH ---
def load_config():
    default_config = {
        "top_dis": -80,
        "time_dis": -60,
        "font_timelabel": "Segoe UI",
        "font_datelabel": "Segoe UI",
        "size_timelabel": 60,
        "size_datelabel": 20,
        "text_color": "white",
        "bg_color": "gray99",
        "show_seconds": False,
        "time_24h": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return {**default_config, **json.load(f)}
        except:
            return default_config
    return default_config

def save_config(new_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4)

# --- 4. GIAO DIỆN CÀI ĐẶT ---
settings_window_instance = None 

def open_settings(*args):
    global settings_window_instance

    if settings_window_instance is not None and settings_window_instance.winfo_exists():
        settings_window_instance.focus_force()
        return

    settings_win = tk.Toplevel(root)
    settings_window_instance = settings_win
    settings_win.title("Cài đặt")
    settings_win.geometry("400x420")
    settings_win.attributes('-topmost', True)
    
    current_conf = load_config()
    entries = {}

    # Biến cho Checkbox
    show_sec_var = tk.BooleanVar(value=current_conf.get("show_seconds", True))
    time_24h_var = tk.BooleanVar(value=current_conf.get("time_24h", True))

    def pick_color(entry_widget):
        color_code = colorchooser.askcolor(title="Chọn màu", parent=settings_win)[1]
        if color_code:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, color_code)

    # Các trường nhập liệu
    fields = [
        ("Vị trí dọc", "top_dis", "number", [-500, 500, 5]),
        ("Time-Date", "time_dis", "number", [-200, 200, 5]),
        ("Font Giờ", "font_timelabel", "font_list", []),
        ("Size Giờ", "size_timelabel", "number", [10, 200, 2]),
        ("Font Ngày", "font_datelabel", "font_list", []),
        ("Size Ngày", "size_datelabel", "number", [10, 100, 1]),
        ("Màu chữ", "text_color", "color", [])
    ]

    for label_text, key, dtype, params in fields:
        row = tk.Frame(settings_win)
        row.pack(fill="x", padx=10, pady=5)
        tk.Label(row, text=label_text, width=15, anchor="w").pack(side="left")
        
        if dtype == "number":
            ent = tk.Spinbox(row, from_=params[0], to=params[1], increment=params[2])
            ent.delete(0, tk.END)
            ent.insert(0, current_conf.get(key, 0))
            ent.pack(side="right", expand=True, fill="x")
            entries[key] = ent
        elif dtype == "font_list":
            system_fonts = sorted(list(set(font.families())))
            clean_fonts = [f for f in system_fonts if not f.startswith('@')]
            ent = ttk.Combobox(row, values=clean_fonts, state="readonly")
            ent.set(current_conf.get(key, "Segoe UI"))
            ent.pack(side="right", expand=True, fill="x")
            entries[key] = ent
        elif dtype == "color":
            ent = tk.Entry(row)
            ent.insert(0, current_conf.get(key, "white"))
            ent.pack(side="left", expand=True, fill="x", padx=(0, 5))
            tk.Button(row, text="🎨", command=lambda e=ent: pick_color(e)).pack(side="right")
            entries[key] = ent

    # Checkbox
    check_frame = tk.Frame(settings_win)
    check_frame.pack(fill="x", padx=10, pady=10)
    tk.Checkbutton(check_frame, text="Hiện giây", variable=show_sec_var).pack(side="left", padx=5)
    tk.Checkbutton(check_frame, text="Định dạng 24h", variable=time_24h_var).pack(side="left", padx=20)

    def apply():
        new_conf = current_conf.copy()
        try:
            for k, entry in entries.items():
                val = entry.get()
                if k in ["top_dis", "time_dis", "size_timelabel", "size_datelabel"]:
                    new_conf[k] = int(val)
                else:
                    new_conf[k] = val
            
            new_conf["show_seconds"] = show_sec_var.get()
            new_conf["time_24h"] = time_24h_var.get()
            
            save_config(new_conf)
            refresh_ui()
            settings_win.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    tk.Button(settings_win, text="Lưu & Áp dụng", command=apply, bg="#2ecc71", fg="white", height=2).pack(fill="x", padx=20, pady=10)
# Thêm đoạn chú thích dưới nút Lưu
    note_text = (
        "• Vị trí dọc: Thay đổi vị trí dọc của đồng hồ\n"
        "• Time-Date: > 40 đặt Ngày lên trên Giờ\n"
        "• Time-Date: < -60 đặt Ngày xuống dưới Giờ\n"
        "Version: 0.1 mod by @drphe"
    )
    
    lbl_note = tk.Label(  # Thêm tk. nếu cần
        settings_win, 
        text=note_text, 
        justify="left",    # Căn lề trái để các dấu • thẳng hàng
        fg="#7f8c8d",      
        font=("Segoe UI", 9, "italic")
    )
    # pady=(10, 0) để tạo khoảng cách với nút Lưu phía trên
    lbl_note.pack(padx=20, pady=(10, 0), fill="x", anchor="w")

# --- 5. LOGIC ĐỒNG HỒ ---
def refresh_ui():
    conf = load_config()
    timeframe.config(bg=conf["bg_color"])
    timelabel.config(font=(conf["font_timelabel"], conf["size_timelabel"]), fg=conf["text_color"], bg=conf["bg_color"])
    datelabel.config(font=(conf["font_datelabel"], conf["size_datelabel"]), fg=conf["text_color"], bg=conf["bg_color"])
    
    timelabel.place(y=screen_height/2 - conf["top_dis"], x=screen_width/2, anchor="center")
    datelabel.place(y=screen_height/2 - (conf["top_dis"] + conf["time_dis"]), x=screen_width/2, anchor="center")
    root.wm_attributes("-transparentcolor", conf["bg_color"])

def update_clock():
    conf = load_config()
    is_24h = conf.get("time_24h", True)
    show_sec = conf.get("show_seconds", True)

    if is_24h:
        fmt = "%H:%M:%S" if show_sec else "%H:%M"
    else:
        fmt = "%I:%M:%S %p" if show_sec else "%I:%M %p"

    tkintertime.set(strftime(fmt))
    tkinterdate.set(strftime("%A, %d %B"))
    root.after(1000, update_clock)

# --- 6. KHỞI CHẠY ---
root = tk.Tk()
root.overrideredirect(1)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

timeframe = tk.Frame(root, width=screen_width, height=screen_height)
timeframe.grid(row=0, column=0)

tkintertime = tk.StringVar()
timelabel = tk.Label(timeframe, textvariable=tkintertime)
tkinterdate = tk.StringVar()
datelabel = tk.Label(timeframe, textvariable=tkinterdate)

refresh_ui()

# Sự kiện chuột
for w in (timelabel, datelabel, timeframe):
    w.bind('<Double-Button-1>', lambda e: open_settings())
# Bắt sự kiện bàn phím
root.bind('<Escape>', lambda e: root.destroy())
root.bind('<Control-s>', open_settings)          # Ctrl + s (viết thường)
root.bind('<Control-S>', open_settings)

update_clock()
root.mainloop()