import pygame
import threading
from tkinter import messagebox
import shutil
import psutil
import os
import time
import zipfile
import random
import tkinter as tk
from tkinter import Toplevel, Label, Text, END, Button, messagebox, Entry, Menu
import traceback
import webbrowser

# ---------- Temel dizinler ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BTL_DESKTOP = os.path.join(BASE_DIR, "BTL_Desktop")
TRASH_DIR = os.path.join(BASE_DIR, "BTL_Trash")
updates_dir = os.path.join(BASE_DIR, "updates")
old_versions_dir = os.path.join(BASE_DIR, "old_versions")
os.makedirs(BTL_DESKTOP, exist_ok=True)
os.makedirs(TRASH_DIR, exist_ok=True)
os.makedirs(updates_dir, exist_ok=True)
os.makedirs(old_versions_dir, exist_ok=True)

root = tk.Tk()
root.title("BTLv3.8Fusion")
root.geometry("900x600")
root.config(bg="deepskyblue")

# ---------- Görev çubuğu ----------
taskbar = tk.Frame(root, bg="gray20", height=40)
taskbar.pack(side="bottom", fill="x")

clock_label = tk.Label(taskbar, fg="white", bg="gray20", font=("Arial", 12))
clock_label.pack(side="right", padx=10)

def update_clock():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    root.after(1000, update_clock)
update_clock()

# ---------- Dosya Yöneticisi ----------
def open_file_manager():
    win = Toplevel(root)
    win.title("Dosya Yöneticisi")
    win.geometry("400x400")
    
    sys_files = [f"SYSTEM_FILE_{i}.sys" for i in range(1, 21)]
    
    lb = tk.Listbox(win)
    lb.pack(expand=True, fill="both")
    
    for f in sys_files:
        lb.insert(END, f)
    
    def delete_file():
        sel = lb.get(tk.ACTIVE)
        if sel and sel.endswith(".sys"):
            for i in range(15):
                messagebox.showerror("Hata", f"{sel} silinemez! Sistem hatası {i+1}/15")
            win.destroy()
            root.destroy()
        else:
            lb.delete(tk.ACTIVE)
    
    del_btn = tk.Button(win, text="Sil", command=delete_file)
    del_btn.pack(pady=5)

# ---------- Ayarlar (Gerçek Uygulamalı) ----------
settings_data = {
    "Tema": ["Light", "Dark", "Blue"],
    "Ses": ["Açık", "Kapalı"]
}

current_settings = {
    "Tema": "Light",
    "Ses": "Açık"
}

def apply_theme(theme):
    if theme == "Light":
        root.config(bg="deepskyblue")
        taskbar.config(bg="gray20")
    elif theme == "Dark":
        root.config(bg="black")
        taskbar.config(bg="gray10")
    elif theme == "Blue":
        root.config(bg="blue")
        taskbar.config(bg="darkblue")
    # Masaüstü ikonlarını da güncelle
    for data in desktop_icons.values():
        data["frame"].config(bg=root.cget("bg"))
        for widget in data["frame"].winfo_children():
            widget.config(bg=root.cget("bg"))

def open_settings():
    win = Toplevel(root)
    win.title("Ayarlar")
    win.geometry("300x250")
    
    tk.Label(win, text="Ayarlar", font=("Arial", 14, "bold")).pack(pady=10)
    
    options_vars = {}
    
    for key, options in settings_data.items():
        frame = tk.Frame(win)
        frame.pack(fill="x", pady=5, padx=10)
        tk.Label(frame, text=key).pack(side="left")
        var = tk.StringVar(value=current_settings[key])
        options_vars[key] = var
        tk.OptionMenu(frame, var, *options).pack(side="right")
    
    def save_settings():
        for k,v in options_vars.items():
            current_settings[k] = v.get()
        # Temayı uygula
        apply_theme(current_settings["Tema"])
        # Ses ayarını uygula (simülasyon)
        if current_settings["Ses"] == "Açık":
            play_info()
        messagebox.showinfo("Ayarlar Kaydedildi", "Ayarlar başarıyla uygulandı!")
    
    save_btn = tk.Button(win, text="Kaydet", command=save_settings)
    save_btn.pack(pady=10)

# ---------- Fonksiyon: İkon sürükle ----------
def make_draggable(widget):
    def start_drag(event):
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
    def do_drag(event):
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        widget.place(x=x, y=y)
    widget.bind("<Button-1>", start_drag)
    widget.bind("<B1-Motion>", do_drag)

# ---------- Masaüstü ikon ekle ----------
desktop_icons = {}
def add_icon(x, y, emoji, name, command, deletable=False):
    frame = tk.Frame(root, bg="deepskyblue")
    frame.place(x=x, y=y)
    icon = tk.Label(frame, text=emoji, font=("Arial", 40), bg="deepskyblue")
    icon.pack()
    label = tk.Label(frame, text=name, bg="deepskyblue", font=("Arial", 10))
    label.pack()
    icon.bind("<Double-Button-1>", lambda e: command())
    label.bind("<Double-Button-1>", lambda e: command())
    # Sağ tık menüsü
    def context(event):
        menu = Menu(root, tearoff=0)
        if deletable:
            menu.add_command(label="Çöp Kutusuna Taşı", command=lambda: move_to_trash(name, frame))
        else:
            menu.add_command(label="Silinemez (Sistem Uygulaması)")
        menu.post(event.x_root, event.y_root)
    icon.bind("<Button-3>", context)
    label.bind("<Button-3>", context)
    make_draggable(frame)
    desktop_icons[name] = {"frame": frame, "deletable": deletable}

# ---------- Çöp Kutusu ----------
def move_to_trash(app_name, frame):
    frame.place_forget()
    desktop_icons.pop(app_name, None)
    with open(os.path.join(TRASH_DIR, app_name + ".txt"), "w") as f:
        f.write(app_name)

def open_trash():
    win = Toplevel(root)
    win.title("Çöp Kutusu")
    win.geometry("300x400")
    files = os.listdir(TRASH_DIR)
    lb = tk.Listbox(win)
    lb.pack(expand=True, fill="both")

    for f in files:
        lb.insert(END, f.replace(".txt", ""))

    def restore():
        sel = lb.get(tk.ACTIVE)
        if sel:
            path = os.path.join(TRASH_DIR, sel + ".txt")
            if os.path.exists(path):
                os.remove(path)
                add_icon(100,100,"📦", sel, lambda: messagebox.showinfo("Uygulama", f"{sel} açıldı!"), deletable=True)
                lb.delete(tk.ACTIVE)

    def empty_trash():
        for f in os.listdir(TRASH_DIR):
            os.remove(os.path.join(TRASH_DIR, f))
        lb.delete(0, END)

    Button(win, text="Geri Yükle", command=restore).pack()
    Button(win, text="Çöp Kutusunu Boşalt", command=empty_trash).pack()

# ---------- CMD Paneli ----------
users = ["EREN", "BETİ", "YİĞİT ASLAN"]
btl_active_users = []

def open_cmd_panel():
    win = Toplevel(root)
    win.title("CMD Paneli")
    win.geometry("400x300")
    txt = Text(win)
    txt.pack(expand=True, fill="both")
    entry = Entry(win)
    entry.pack(fill="x")

    def run():
        cmd = entry.get().strip().lower()
        if cmd.startswith("active"):
            user = cmd.split()[-1].upper()
            if user in users and user not in btl_active_users:
                btl_active_users.append(user)
                txt.insert(END, f"{user} aktif edildi.\n")
            else:
                txt.insert(END, "Geçersiz kullanıcı veya zaten aktif.\n")
        elif cmd.startswith("deactive"):
            user = cmd.split()[-1].upper()
            if user in btl_active_users:
                btl_active_users.remove(user)
                txt.insert(END, f"{user} pasif edildi.\n")
            else:
                txt.insert(END, "Geçersiz kullanıcı veya zaten pasif.\n")
        elif cmd == "store:list":
            txt.insert(END, "BTL Store Uygulamaları:\n- Not Defteri\n- Yılan Oyunu\n- Top Yakalama\n- Maria'yı Kurtar\n")
        else:
            txt.insert(END, "Bilinmeyen komut.\n")
        entry.delete(0, END)

    entry.bind("<Return>", lambda e: run())
    Button(win, text="Çalıştır", command=run).pack()

def show_users():
    messagebox.showinfo("Kullanıcılar", "\n".join(users))

# ---------- Arama Çubuğu ----------
search_var = tk.StringVar()
def search_app(event=None):
    app_name = search_var.get().strip().lower()
    mapping = {
        "not defteri": open_notepad,
        "yılan oyunu": open_snake_game,
        "top yakalama": open_ball_game,
        "maria'yı kurtar": open_maria_game,
        "cmd paneli": open_cmd_panel,
        "kullanıcılar": show_users
    }
    func = mapping.get(app_name)
    if func:
        func()
    else:
        messagebox.showerror("Hata", "Böyle bir uygulama bulunamadı!")

search_entry = Entry(taskbar, textvariable=search_var, width=30)
search_entry.pack(side="left", padx=10)
search_entry.bind("<Return>", search_app)

# ---------- Sağ tık menüsü ----------
def show_context_menu(event):
    menu = Menu(root, tearoff=0)
    menu.add_command(label="Yeni + Metin Belgesi", command=lambda: create_new_file(BTL_DESKTOP))
    menu.add_command(label="Yeni + Klasör", command=lambda: create_new_folder(BTL_DESKTOP))
    menu.add_command(label="Yeni + .zip Klasörü", command=lambda: create_new_zip(BTL_DESKTOP))
    menu.post(event.x_root, event.y_root)
root.bind("<Button-3>", show_context_menu)

# ---------- Dosya/Klasör/Zip ----------
def create_new_file(desktop_dir):
    path = os.path.join(desktop_dir, f"YeniDosya{random.randint(1,100)}.txt")
    with open(path, "w") as f: f.write("")
    add_icon(200,200,"📄", os.path.basename(path), lambda: os.startfile(path), deletable=True)

def create_new_folder(desktop_dir):
    folder_path = os.path.join(desktop_dir, f"YeniKlasor{random.randint(1,100)}")
    os.makedirs(folder_path, exist_ok=True)
    add_icon(250,200,"📁", os.path.basename(folder_path), lambda: os.startfile(folder_path), deletable=True)

def create_new_zip(desktop_dir):
    zip_path = os.path.join(desktop_dir, f"YeniZip{random.randint(1,100)}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf: pass
    add_icon(300,200,"📂", os.path.basename(zip_path), lambda: os.startfile(zip_path), deletable=True)

# ---------- Uygulamalar ----------
def open_notepad():
    win = Toplevel(root)
    win.title("BTL Not Defteri")
    win.geometry("500x400")
    text = Text(win, wrap="word")
    text.pack(expand=True, fill="both")

def open_ball_game():
    win = Toplevel(root)
    win.title("Top Yakalama")
    win.geometry("400x300")
    score = [0]
    canvas = tk.Canvas(win, width=400, height=300, bg="white")
    canvas.pack()
    ball = canvas.create_oval(180, 140, 220, 180, fill="red")
    def click_ball(event):
        if canvas.find_withtag("current"):
            score[0] += 1
            label.config(text=f"Score: {score[0]}")
            x = random.randint(0, 360)
            y = random.randint(0, 260)
            canvas.coords(ball, x, y, x+40, y+40)
    canvas.tag_bind(ball, "<Button-1>", click_ball)
    label = Label(win, text="Score: 0")
    label.pack()

def open_snake_game():
    win = Toplevel(root)
    win.title("Yılan Oyunu")
    win.geometry("400x400")
    canvas = tk.Canvas(win, width=400, height=400, bg="black")
    canvas.pack()
    canvas.focus_set()
    snake = [(200,200)]
    snake_dir = "Right"
    food = [random.randrange(0,20)*20, random.randrange(0,20)*20]
    food_rect = canvas.create_rectangle(food[0], food[1], food[0]+20, food[1]+20, fill="green")
    def move_snake():
        nonlocal snake, snake_dir, food
        x, y = snake[-1]
        if snake_dir=="Right": x+=20
        elif snake_dir=="Left": x-=20
        elif snake_dir=="Up": y-=20
        elif snake_dir=="Down": y+=20
        if x < 0 or x >= 400 or y < 0 or y >= 400 or (x,y) in snake:
            messagebox.showinfo("Oyun Bitti", f"Skorunuz: {len(snake)}")
            win.destroy()
            return
        snake.append((x,y))
        canvas.delete("snake")
        for seg in snake:
            canvas.create_rectangle(seg[0], seg[1], seg[0]+20, seg[1]+20, fill="white", tag="snake")
        if x==food[0] and y==food[1]:
            food = [random.randrange(0,20)*20, random.randrange(0,20)*20]
            canvas.coords(food_rect, food[0], food[1], food[0]+20, food[1]+20)
        else:
            snake.pop(0)
        win.after(200, move_snake)
    def change_dir(event):
        nonlocal snake_dir
        opposite = {"Up":"Down", "Down":"Up", "Left":"Right", "Right":"Left"}
        if event.keysym in ["Up","Down","Left","Right"] and event.keysym != opposite.get(snake_dir):
            snake_dir = event.keysym
    win.bind("<Key>", change_dir)
    move_snake()

def open_browser():
    webbrowser.open("https://www.google.com")

def open_update_center():
    win = Toplevel(root)
    win.title("BTL Güncelleme Merkezi")
    win.geometry("300x200")
    Button(win, text="Güncelle", command=lambda: messagebox.showinfo("BTL", "Güncelleme tamamlandı!")).pack(pady=20)

# ---------- Görev Yöneticisi ----------
def open_task_manager():
    win = tk.Toplevel(root)  # root senin ana Tk penceresi
    win.title("Görev Yöneticisi")
    win.geometry("250x150")
    
    cpu = random.randint(1,100)
    ram = random.randint(1000,16000)
    gpu = random.randint(1,100)
    bellek = random.randint(1,100)
    
    tk.Label(win, text=f"CPU Kullanımı: %{cpu}").pack(anchor="w", padx=10, pady=2)
    tk.Label(win, text=f"RAM Kullanımı: {ram} MB").pack(anchor="w", padx=10, pady=2)
    tk.Label(win, text=f"GPU Kullanımı: %{gpu}").pack(anchor="w", padx=10, pady=2)
    tk.Label(win, text=f"Bellek Kullanımı: %{bellek}").pack(anchor="w", padx=10, pady=2)

# ---------- Masaüstüne ikon eklemek için ----------
add_icon(850,10,"📊","Görev Yöneticisi", open_task_manager, deletable=False)
import psutil  # pil bilgisi için gerekli, pip install psutil

# ---------- Wi-Fi Simgesi ----------
wifi_icon = tk.Label(taskbar, text="🛜", bg="gray20", fg="white", font=("Arial", 16))
wifi_icon.pack(side="left", padx=2)

def wifi_click(event):
    messagebox.showinfo("Wi-Fi", "Wi-Fi bağlı!")

wifi_icon.bind("<Button-1>", wifi_click)

# ---------- Pil Simgesi ----------
battery_icon = tk.Label(taskbar, text="🔋", bg="gray20", fg="white", font=("Arial", 16))
battery_icon.pack(side="left", padx=2)

def battery_click(event):
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        status = "Şarjda" if plugged else "Şarjda değil"
        messagebox.showinfo("Pil Durumu", f"Şarj: %{percent}\nDurum: {status}")
    else:
        messagebox.showinfo("Pil Durumu", "Pil bilgisi alınamadı!")

battery_icon.bind("<Button-1>", battery_click)

# ---------- Maria'yı Kurtar Oyunu ----------
def open_maria_game():
    win = Toplevel(root)
    win.title("Maria'yı Kurtar")
    win.geometry("500x500")
    canvas = tk.Canvas(win, width=500, height=500, bg="lightblue")
    canvas.pack()

    messagebox.showinfo("Başlangıç", "Maria arkadaşı Sely ile gezerken kayboldu!\nSely: Maria! Neredesin??\nHadi ipuçlarını bul ve Maria'yı kurtar!")

    paper_pieces = []
    positions = [(50,50), (200,100), (350,200)]
    text_message = "Sely, kurtar beni"
    for pos in positions:
        piece = canvas.create_rectangle(pos[0], pos[1], pos[0]+30, pos[1]+30, fill="yellow")
        paper_pieces.append(piece)
    collected = []

    def collect_piece(event):
        for piece in paper_pieces:
            coords = canvas.coords(piece)
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                if piece not in collected:
                    collected.append(piece)
                    canvas.itemconfig(piece, fill="gray")
        if len(collected) == len(paper_pieces):
            messagebox.showinfo("İpucu Bulundu", f"Kağıt parçaları birleştirildi: '{text_message}'\nCanavarlar çıkıyor! Obby başlıyor...")
            start_obby()

    canvas.bind("<Button-1>", collect_piece)

    sely = canvas.create_rectangle(20, 450, 40, 470, fill="green")
    obstacles = []
    obstacle_speed = 5
    for y in range(50, 400, 100):
        obs = canvas.create_rectangle(100, y, 150, y+20, fill="red")
        obstacles.append(obs)

    def move_obby():
        for obs in obstacles:
            canvas.move(obs, obstacle_speed, 0)
            coords = canvas.coords(obs)
            if coords[2] >= 500 or coords[0] <= 0:
                canvas.move(obs, -obstacle_speed*10, 0)
            if check_collision(sely, obs):
                messagebox.showinfo("Obby", "Sely çarptı! Yeniden başla.")
                canvas.coords(sely, 20, 450, 40, 470)
        win.after(50, move_obby)

    def check_collision(rect1, rect2):
        x1,y1,x2,y2 = canvas.coords(rect1)
        a1,b1,a2,b2 = canvas.coords(rect2)
        return not (x2<a1 or x1>a2 or y2<b1 or y1>b2)

    boss_hp = [500]
    sely_lives = [5]
    boss = canvas.create_rectangle(200,50,300,150, fill="purple")
    boss_attacks = []

    def boss_attack():
        fireball = canvas.create_oval(250,150,270,170, fill="orange")
        boss_attacks.append(fireball)
        animate_fireball(fireball)
        if sely_lives[0] > 0 and boss_hp[0] > 0:
            win.after(1500, boss_attack)

    def animate_fireball(fireball):
        canvas.move(fireball, 0, 10)
        if canvas.coords(fireball)[3] >= 500:
            canvas.delete(fireball)
            if fireball in boss_attacks: boss_attacks.remove(fireball)
        else:
            if check_collision(sely, fireball):
                sely_lives[0] -= 1
                canvas.delete(fireball)
                if fireball in boss_attacks: boss_attacks.remove(fireball)
                if sely_lives[0] <= 0:
                    messagebox.showinfo("Oyun Bitti", "Sely öldü! Maria kurtulamadı.")
                    win.destroy()
                    return
            win.after(50, lambda: animate_fireball(fireball))

    def decrease_boss_hp(event):
        if boss_hp[0] > 0:
            boss_hp[0] -= 1
            if boss_hp[0] <= 0:
                messagebox.showinfo("Tebrikler!", "Boss yenildi! Maria kurtarıldı!")
                win.destroy()

    def start_boss_battle():
        messagebox.showinfo("Boss", "Boss ortaya çıktı! 30 saniye içinde 'S' tuşuna basarak saldırın!")
        win.bind("<KeyPress-s>", decrease_boss_hp)
        boss_attack()

    def start_obby():
        move_obby()
        win.after(1000, start_boss_battle)
import tkinter as tk
from tkinter import ttk
import time

# ---------- Startup Animasyonu ----------
def startup_animation(callback):
    win = tk.Toplevel()
    win.title("BTLv3.8Fusion Başlatılıyor")
    win.geometry("400x200")
    win.config(bg="black")

    label = tk.Label(win, text="BTL", font=("Arial", 40, "bold"), fg="white", bg="black")
    label.pack(pady=30)

    progress = ttk.Progressbar(win, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)
    
    def fill_bar(val=0):
        if val <= 100:
            progress["value"] = val
            win.update()
            win.after(30, lambda: fill_bar(val+2))
        else:
            win.destroy()
            callback()  # Ana programı başlat

    fill_bar()

# ---------- Shutdown Animasyonu ----------
def shutdown_animation():
    win = tk.Toplevel()
    win.title("BTLv3.8Fusion Kapanıyor")
    win.geometry("400x200")
    win.config(bg="black")

    label = tk.Label(win, text="BTL", font=("Arial", 40, "bold"), fg="white", bg="black")
    label.pack(pady=30)

    progress = ttk.Progressbar(win, orient="horizontal", length=300, mode="determinate", style="red.Horizontal.TProgressbar")
    progress.pack(pady=20)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("red.Horizontal.TProgressbar", troughcolor='black', background='red')

    def fill_bar(val=0):
        if val <= 100:
            progress["value"] = val
            win.update()
            win.after(30, lambda: fill_bar(val+2))
        else:
            win.destroy()
            root.destroy()  # Ana sistemi kapat

    fill_bar()

# ---------- Örnek Ana Program Fonksiyonu ----------
def main_app():
    print("BTL açıldı! Buraya ana program kodlarını ekle.")

#----------- Ses sistemi ----------
pygame.mixer.init()

def play_sound(path):
    def run():
        sound = pygame.mixer.Sound(path)
        sound.play()
    threading.Thread(target=run).start()

# Ses oynatma fonksiyonları
def play_startup():
    play_sound("assets/startup.wav")

def play_info():
    play_sound("assets/wav.wav")

def play_error():
    play_sound("assets/error.wav")

def play_shutdown():
    play_sound("assets/shutdown.wav")

# Örnek kullanım (aşağıdaki messagebox fonksiyonlarını kendi GUI kodunuzda çağırabilirsiniz)
def show_info_with_sound(title, message):
    play_info()
    messagebox.showinfo(title, message)

def show_error_with_sound(title, message):
    play_error()
    messagebox.showerror(title, message)

def shutdown_procedure():
    play_shutdown()
    # shutdown animasyonu veya GUI kapanışı burada yapılabilir

# ---------- Kullanımı ----------
# Startup ekranı:
startup_animation(main_app)

# Shutdown'u ana programda çağırmak için:
# shutdown_animation()

# ---------- Başlat Butonu ----------
def open_start_menu():
    menu = Toplevel(root)
    menu.title("Başlat")
    menu.geometry("200x400+0+200")
    menu.config(bg="gray10")
    Button(menu, text="📝 Not Defteri", command=open_notepad).pack(fill="x")
    Button(menu, text="🌐 BTL Tarayıcı", command=open_browser).pack(fill="x")
    Button(menu, text="🐍 Yılan Oyunu", command=open_snake_game).pack(fill="x")
    Button(menu, text="⚽ Top Yakalama", command=open_ball_game).pack(fill="x")
    Button(menu, text="🧩 Maria'yı Kurtar", command=open_maria_game).pack(fill="x")
    Button(menu, text="🧠 CMD Paneli", command=open_cmd_panel).pack(fill="x")
    Button(menu, text="👤 Kullanıcılar", command=show_users).pack(fill="x")
    Button(menu, text="🚪 Çıkış", command=shutdown_animation).pack(fill="x")
    Button(menu, text="🎨 Paint", command=open_paint_app).pack(fill="x")
start_button = Button(taskbar, text="Başlat", command=open_start_menu, bg="gray30", fg="white")
start_button.pack(side="left", padx=5)

# ---------- Başlangıç İkonları ----------
add_icon(50,50,"📝","Not Defteri", open_notepad, deletable=True)
add_icon(150,50,"🐍","Yılan Oyunu", open_snake_game, deletable=True)
add_icon(250,50,"⚽","Top Yakalama", open_ball_game, deletable=True)
add_icon(350,50,"🧩","Maria'yı Kurtar", open_maria_game, deletable=True)
add_icon(450,50,"🧠","CMD Paneli", open_cmd_panel, deletable=False)
add_icon(550,50,"🗑️","Çöp Kutusu", open_trash, deletable=False)
add_icon(650,50,"🌐","BTL Tarayıcı", open_browser, deletable=True)
add_icon(750,50,"⚙️","Güncelleme Merkezi", open_update_center, deletable=False)
add_icon(850, 50, "🗂️", "Dosya Yöneticisi", open_file_manager, deletable=False)
add_icon(950, 50, "⚙️", "Ayarlar", open_settings, deletable=False)

def open_paint_app():
    paint_win = Toplevel(root)
    paint_win.title("BTL Paint")
    paint_win.geometry("700x500")

    color_frame = tk.Frame(paint_win)
    color_frame.pack(side="top", fill="x")

    colors = ["black", "red", "green", "blue", "orange", "purple", "brown"]
    color_var = tk.StringVar(value="black")

    def set_color(c):
        color_var.set(c)

    for c in colors:
        b = tk.Button(color_frame, bg=c, width=2, command=lambda col=c: set_color(col))
        b.pack(side="left", padx=2)

    brush_size = tk.IntVar(value=3)

    size_scale = tk.Scale(color_frame, from_=1, to=10, orient="horizontal", label="Fırça Kalınlığı", variable=brush_size)
    size_scale.pack(side="left", padx=10)

    canvas = tk.Canvas(paint_win, bg="white", cursor="cross")
    canvas.pack(expand=True, fill="both")

    last_x, last_y = None, None

    def start_draw(event):
        nonlocal last_x, last_y
        last_x, last_y = event.x, event.y

    def draw(event):
        nonlocal last_x, last_y
        x, y = event.x, event.y
        canvas.create_line(last_x, last_y, x, y, fill=color_var.get(), width=brush_size.get(), capstyle=tk.ROUND, smooth=True)
        last_x, last_y = x, y

    def reset(event):
        nonlocal last_x, last_y
        last_x, last_y = None, None

    def clear_canvas():
        canvas.delete("all")

    clear_btn = tk.Button(paint_win, text="Temizle", command=clear_canvas)
    clear_btn.pack(side="bottom", pady=5)

    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", reset)

# Masaüstüne Paint ikonu ekle
add_icon(50, 220, "🎨", "Paint", open_paint_app, deletable=True)
# ---------- BTL Store - Uygulama İndirme ----------
def btl_store():
    win = Toplevel(root)
    win.title("BTL Store")
    win.geometry("400x400")
    apps = {
        "Not Defteri": open_notepad,
        "Yılan Oyunu": open_snake_game,
        "Top Yakalama": open_ball_game,
        "Maria'yı Kurtar": open_maria_game
    }
    for app_name in apps:
        def make_command(name=app_name):
            def command():
                # Masaüstüne simge ekle
                add_icon(random.randint(50, 700), random.randint(100, 500), "🎮", name, apps[name], deletable=True)
                messagebox.showinfo("BTL Store", f"{name} indirildi ve masaüstüne eklendi!")
            return command
        Button(win, text=f"📥 {app_name} İndir", command=make_command()).pack(pady=5, fill="x")

add_icon(50,120,"🏬","BTL Store", btl_store, deletable=False)
# ---------- Diller ----------
LANGUAGES = {
    "TR": {
        "start_menu": "Başlat",
        "task_manager": "Görev Yöneticisi",
        "notepad": "Not Defteri",
        "snake_game": "Yılan Oyunu",
        "ball_game": "Top Yakalama",
        "maria_game": "Maria'yı Kurtar",
        "cmd_panel": "CMD Paneli",
        "trash": "Çöp Kutusu",
        "browser": "BTL Tarayıcı",
        "update_center": "Güncelleme Merkezi",
        "paint": "Paint",
        "store": "BTL Store",
        "restore": "Geri Yükle",
        "empty_trash": "Çöp Kutusunu Boşalt",
        "info_title": "Bilgi",
        "error_title": "Hata",
        "game_over": "Oyun Bitti",
        "boss_defeated": "Boss yenildi! Maria kurtarıldı!",
        "sely_dead": "Sely öldü! Maria kurtulamadı!"
    },
    "EN": {
        "start_menu": "Start",
        "task_manager": "Task Manager",
        "notepad": "Notepad",
        "snake_game": "Snake Game",
        "ball_game": "Ball Catch",
        "maria_game": "Save Maria",
        "cmd_panel": "CMD Panel",
        "trash": "Trash",
        "browser": "BTL Browser",
        "update_center": "Update Center",
        "paint": "Paint",
        "store": "BTL Store",
        "restore": "Restore",
        "empty_trash": "Empty Trash",
        "info_title": "Info",
        "error_title": "Error",
        "game_over": "Game Over",
        "boss_defeated": "Boss defeated! Maria saved!",
        "sely_dead": "Sely died! Maria couldn't be saved!"
    }
}

current_lang = "EN"  # Sistem İngilizce başlasın
L = LANGUAGES[current_lang]

# ---------- Dil Değiştirme Fonksiyonu ----------
def change_language(lang_code):
    global current_lang, L
    if lang_code in LANGUAGES:
        current_lang = lang_code
        L = LANGUAGES[current_lang]
        update_ui_texts()

# ---------- UI Güncelleme ----------
def update_ui_texts():
    start_button.config(text=L["start_menu"])
    wifi_icon.config(text="🛜")
    battery_icon.config(text="🔋")

    for name, icon_data in desktop_icons.items():
        frame = icon_data["frame"]
        label = frame.children['!label2']
        if name == "Görev Yöneticisi": label.config(text=L["task_manager"])
        elif name == "Not Defteri": label.config(text=L["notepad"])
        elif name == "Yılan Oyunu": label.config(text=L["snake_game"])
        elif name == "Top Yakalama": label.config(text=L["ball_game"])
        elif name == "Maria'yı Kurtar": label.config(text=L["maria_game"])
        elif name == "CMD Paneli": label.config(text=L["cmd_panel"])
        elif name == "Çöp Kutusu": label.config(text=L["trash"])
        elif name == "BTL Tarayıcı": label.config(text=L["browser"])
        elif name == "Güncelleme Merkezi": label.config(text=L["update_center"])
        elif name == "Paint": label.config(text=L["paint"])
        elif name == "BTL Store": label.config(text=L["store"])

# ---------- MessageBoxlar ----------
def show_info_with_sound(title_key, message_key):
    play_info()
    messagebox.showinfo(L[title_key], L[message_key])

def show_error_with_sound(title_key, message_key):
    play_error()
    messagebox.showerror(L[title_key], L[message_key])

# ---------- Örnek pencere başlıkları ----------
def open_notepad():
    win = Toplevel(root)
    win.title(L["notepad"])
    win.geometry("500x400")
    text = Text(win, wrap="word")
    text.pack(expand=True, fill="both")

def open_task_manager():
    win = Toplevel(root)
    win.title(L["task_manager"])
    win.geometry("250x150")
    cpu = random.randint(1,100)
    ram = random.randint(1000,16000)
    gpu = random.randint(1,100)
    bellek = random.randint(1,100)
    tk.Label(win, text=f"CPU Usage: %{cpu}").pack(anchor="w", padx=10, pady=2)
    tk.Label(win, text=f"RAM Usage: {ram} MB").pack(anchor="w", padx=10, pady=2)
    tk.Label(win, text=f"GPU Usage: %{gpu}").pack(anchor="w", padx=10, pady=2)
    tk.Label(win, text=f"Memory Usage: %{bellek}").pack(anchor="w", padx=10, pady=2)

def open_trash():
    win = Toplevel(root)
    win.title(L["trash"])
    win.geometry("300x400")
    files = os.listdir(TRASH_DIR)
    lb = tk.Listbox(win)
    lb.pack(expand=True, fill="both")
    for f in files:
        lb.insert(END, f.replace(".txt",""))
    Button(win, text=L["restore"], command=lambda: restore_file(lb)).pack()
    Button(win, text=L["empty_trash"], command=lambda: empty_trash_files(lb)).pack()

# ---------- Maria Oyunu Mesajları ----------
def maria_game_message_start():
    messagebox.showinfo(L["info_title"], "Maria arkadaşı Sely ile gezerken kayboldu!")

def maria_game_boss_defeated():
    messagebox.showinfo(L["info_title"], L["boss_defeated"])

def maria_game_sely_dead():
    messagebox.showinfo(L["game_over"], L["sely_dead"])

# ---------- Dil Değiştirme Örneği ----------
# change_language("TR")  # Bunu çağırırsan sistem Türkçe olur
# ---------- Görev Çubuğuna Dil Seçici ----------
lang_var = tk.StringVar(value=current_lang)
def lang_change(event=None):
    change_language(lang_var.get())

lang_menu = tk.OptionMenu(taskbar, lang_var, *LANGUAGES.keys(), command=lambda _: lang_change())
lang_menu.config(bg="gray30", fg="white")
lang_menu.pack(side="left", padx=5)

# ---------- Program Başlat ----------
root.mainloop()