# 📄 JessMD — Document to Markdown Converter

Konverter dokumen lokal berbasis Python (`microsoft/markitdown`) untuk mengubah file **PDF (termasuk hasil scan OCR), Word (`.docx`), PowerPoint (`.pptx`), dan Excel (`.xlsx`)** menjadi teks Markdown bersih agar lebih hemat token saat diunggah ke AI.

## ✨ Fitur Utama

- **Web UI Batch Upload (Streamlit):** Unggah banyak file sekaligus, cek estimasi jumlah token (`tiktoken`), salin teks, atau unduh dalam bentuk `.zip` / satu file `.md` gabungan.
- **Integrasi Klik Kanan Windows Explorer:** Klik kanan dokumen apa saja -> _Convert to Markdown (JessMD)_ dengan indikator loading otomatis.
- **Smart OCR PDF:** Otomatis mendeteksi PDF hasil scan gambar dan mengekstrak teksnya secara offline menggunakan `rapidocr-onnxruntime`.

## 🚀 Cara Instalasi di Windows (Otomatis)

1. ⬇️ Download Aplikasi
👉 **[Klik di sini untuk Download JessMD (.ZIP)](https://github.com/gujestok-welay/JessMD/releases/latest/download/JessMD-Windows.zip)**
2. Masuk ke dalam folder hasil ekstrak dan klik ganda **`Install_JessMD.bat`**.
3. Tunggu hingga proses instalasi selesai (script akan otomatis menyiapkan Python, environment, shortcut Desktop, dan menu klik kanan Explorer).

## 🗑️ Cara Menghapus (Uninstall)

Klik ganda **`Uninstall_JessMD.bat`** untuk menghapus menu klik kanan dan shortcut Desktop, lalu hapus folder aplikasi.
