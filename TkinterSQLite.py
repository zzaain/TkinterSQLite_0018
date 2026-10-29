import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Inisialisasi Database dan Tabel
def init_db():
    conn = sqlite3.connect("prediksi_diabetes.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pasien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pasien TEXT NOT NULL,
            usia INTEGER NOT NULL,
            gula_darah REAL NOT NULL,
            bmi REAL NOT NULL,
            riwayat_ortu TEXT NOT NULL,
            hasil_prediksi TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Logika Penentuan Risiko Diabetes
def hitung_risiko(gula_darah, bmi, riwayat_ortu):
    if gula_darah >= 200:
        return "Sangat Tinggi"
    elif 140 <= gula_darah <= 199:
        if bmi >= 30 or riwayat_ortu == "Ya":
            return "Tinggi"
        else:
            return "Sedang"
    else: # gula_darah < 140
        if bmi >= 30:
            return "Sedang" if riwayat_ortu == "Ya" else "Waspada"
        else:
            if riwayat_ortu == "Ya":
                return "Waspada"
            else:
                return "Rendah"

# Fungsi Placeholder untuk Entry (Contoh Angka/Teks)
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = '#95a5a6'
        self.default_fg_color = self['fg']

        self.put_placeholder()
        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

    def put_placeholder(self):
        if not self.get() or self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def focus_in(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def focus_out(self, *args):
        if not self.get():
            self.put_placeholder()

# Fungsi untuk Memproses Prediksi dan Menyimpan ke Database
def proses_prediksi():
    nama = entry_nama.get().strip()
    usia_str = entry_usia.get().strip()
    gula_str = entry_gula.get().strip()
    bmi_str = entry_bmi.get().strip()
    riwayat = combo_riwayat.get()

    # Validasi Input (Pastikan bukan placeholder)
    if not nama or nama == "Contoh: Afifah Sheriell":
        messagebox.showerror("Error Validasi", "Nama pasien tidak boleh kosong!")
        return
    
    try:
        usia = int(usia_str)
        if usia <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error Validasi", "Usia harus berupa angka positif yang valid!")
        return

    try:
        gula_darah = float(gula_str)
        if gula_darah < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error Validasi", "Kadar gula darah harus berupa angka yang valid!")
        return

    try:
        bmi = float(bmi_str)
        if bmi < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error Validasi", "Nilai BMI harus berupa angka yang valid!")
        return

    if riwayat not in ["Ya", "Tidak"]:
        messagebox.showerror("Error Validasi", "Pilih riwayat diabetes orang tua (Ya/Tidak)!")
        return

    # Hitung Risiko
    hasil = hitung_risiko(gula_darah, bmi, riwayat)

    # Pengaturan Warna Label Berdasarkan Tingkat Risiko
    warna_risiko = {
        "Rendah": "#27ae60",       # Hijau
        "Waspada": "#d68910",      # Kuning Tua/Oranye Terang
        "Sedang": "#ca6f1e",       # Oranye
        "Tinggi": "#c0392b",       # Merah
        "Sangat Tinggi": "#78281f" # Merah Gelap
    }
    
    warna_text = warna_risiko.get(hasil, "#000000")
    label_hasil.config(text=f"Hasil Prediksi: Risiko {hasil}", fg=warna_text)

    # Simpan ke Database SQLite
    try:
        conn = sqlite3.connect("prediksi_diabetes.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pasien (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nama, usia, gula_darah, bmi, riwayat, hasil))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukses", "Data berhasil diprediksi dan disimpan ke database!")
        
        # Reset Form
        entry_nama.delete(0, tk.END)
        entry_nama.put_placeholder()
        entry_usia.delete(0, tk.END)
        entry_usia.put_placeholder()
        entry_gula.delete(0, tk.END)
        entry_gula.put_placeholder()
        entry_bmi.delete(0, tk.END)
        entry_bmi.put_placeholder()
        combo_riwayat.set('')
        
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal menyimpan ke database: {e}")

# Fungsi untuk Menampilkan Data (Jendela Baru dengan Tabel/Treeview)
def lihat_data():
    jendela_data = tk.Toplevel(root)
    jendela_data.title("Riwayat Data Pasien")
    jendela_data.geometry("750x400")
    jendela_data.config(bg="#e8f4f8")

    label_judul = tk.Label(jendela_data, text="Data Riwayat Prediksi Pasien", font=("Arial", 14, "bold"), bg="#e8f4f8", fg="#1b4f72")
    label_judul.pack(pady=10)

    frame_tabel = tk.Frame(jendela_data)
    frame_tabel.pack(fill="both", expand=True, padx=15, pady=10)

    columns = ("ID", "Nama Pasien", "Usia", "Gula Darah", "BMI", "Riwayat Ortu", "Hasil Prediksi")
    tree = ttk.Treeview(frame_tabel, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=95, anchor="center")
    tree.column("Nama Pasien", width=140, anchor="w")

    scrollbar = ttk.Scrollbar(frame_tabel, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    try:
        conn = sqlite3.connect("prediksi_diabetes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pasien")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat data: {e}")

# --- SETUP UTAMA GUI TKINTER (TEMA MERAH BIRU) ---
if __name__ == "__main__":
    init_db()

    root = tk.Tk()
    root.title("Aplikasi Prediksi Risiko Diabetes")
    root.geometry("460x570")
    root.config(bg="#e8f4f8")  # Background biru muda lembut
    root.resizable(False, False)

    # Judul Aplikasi
    title_label = tk.Label(root, text="Prediksi Risiko Diabetes", font=("Arial", 16, "bold"), bg="#e8f4f8", fg="#1b4f72")
    title_label.pack(pady=15)

    # Frame Form Input
    form_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
    form_frame.pack(padx=20, pady=5, fill="both", expand=True)

    # Input Nama Pasien (dengan Contoh Teks)
    tk.Label(form_frame, text="Nama Pasien:", font=("Arial", 10), bg="#ffffff", anchor="w").grid(row=0, column=0, sticky="w", padx=15, pady=8)
    entry_nama = PlaceholderEntry(form_frame, placeholder="Contoh: Afifah Sheriell", font=("Arial", 10), width=22)
    entry_nama.grid(row=0, column=1, padx=15, pady=8)

    # Input Usia (dengan Contoh Angka)
    tk.Label(form_frame, text="Usia (Tahun):", font=("Arial", 10), bg="#ffffff", anchor="w").grid(row=1, column=0, sticky="w", padx=15, pady=8)
    entry_usia = PlaceholderEntry(form_frame, placeholder="Contoh: 20", font=("Arial", 10), width=22)
    entry_usia.grid(row=1, column=1, padx=15, pady=8)

    # Input Kadar Gula Darah (dengan Contoh Angka)
    tk.Label(form_frame, text="Kadar Gula Darah (mg/dL):", font=("Arial", 10), bg="#ffffff", anchor="w").grid(row=2, column=0, sticky="w", padx=15, pady=8)
    entry_gula = PlaceholderEntry(form_frame, placeholder="Contoh: 125", font=("Arial", 10), width=22)
    entry_gula.grid(row=2, column=1, padx=15, pady=8)

    # Input BMI (dengan Contoh Angka)
    tk.Label(form_frame, text="Nilai BMI:", font=("Arial", 10), bg="#ffffff", anchor="w").grid(row=3, column=0, sticky="w", padx=15, pady=8)
    entry_bmi = PlaceholderEntry(form_frame, placeholder="Contoh: 22.5", font=("Arial", 10), width=22)
    entry_bmi.grid(row=3, column=1, padx=15, pady=8)

    # Combobox Riwayat Diabetes Orang Tua
    tk.Label(form_frame, text="Riwayat Ortu (Ya/Tidak):", font=("Arial", 10), bg="#ffffff", anchor="w").grid(row=4, column=0, sticky="w", padx=15, pady=8)
    combo_riwayat = ttk.Combobox(form_frame, values=["Ya", "Tidak"], font=("Arial", 10), width=20, state="readonly")
    combo_riwayat.grid(row=4, column=1, padx=15, pady=8)

    # Label Hasil Prediksi
    label_hasil = tk.Label(root, text="Hasil Prediksi: -", font=("Arial", 11, "bold"), bg="#e8f4f8", fg="#1b4f72")
    label_hasil.pack(pady=10)

    # Frame Tombol Aksi (Kombinasi Merah dan Biru)
    btn_frame = tk.Frame(root, bg="#e8f4f8")
    btn_frame.pack(pady=10)

    btn_prediksi = tk.Button(btn_frame, text="Proses Prediksi", font=("Arial", 10, "bold"), bg="#c0392b", fg="white", width=14, command=proses_prediksi)
    btn_prediksi.grid(row=0, column=0, padx=5)

    btn_lihat = tk.Button(btn_frame, text="Lihat Data", font=("Arial", 10, "bold"), bg="#2980b9", fg="white", width=14, command=lihat_data)
    btn_lihat.grid(row=0, column=1, padx=5)

    root.mainloop()