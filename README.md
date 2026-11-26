# MediaFire Downloader

Scraper buat download file dari link share MediaFire publik — tanpa buka webnya, tanpa iklan, tanpa klik tombol download berkali-kali.

Cukup kasih link share, script ini men-scrape halaman MediaFire, mengambil link download aslinya, lalu mengunduh filenya langsung.

## Isi

| File | Fungsi |
|---|---|
| `mediafire.py` | Script utamanya. Cuma butuh library `requests`. |

## Persiapan

Butuh Python 3 dan library `requests`:

```bash
python3 --version
```

Install `requests` — pilih salah satu cara sesuai kondisi sistem:

```bash
# Cara biasa
pip install requests

# Kalau muncul error "externally-managed-environment" (Debian/Ubuntu baru),
# pilih salah satu:

# 1) Pakai paket sistem (paling gampang)
apt install python3-requests

# 2) Pakai virtual environment
python3 -m venv venv
./venv/bin/pip install requests
# lalu jalankan script pakai ./venv/bin/python

# 3) Paksa install (cepat, tapi bisa mengganggu paket sistem)
pip install requests --break-system-packages
```

> Di banyak server `requests` sebenarnya sudah terpasang bawaan. Coba jalankan scriptnya dulu — kalau tidak ada error `ModuleNotFoundError: No module named 'requests'`, berarti tidak perlu install apa-apa.

Catatan: di sebagian sistem perintahnya `python3`, bukan `python`. Semua contoh di bawah pakai `python3`.

## Cara Pakai (CLI)

### 1. `download` — unduh filenya

```bash
python3 mediafire.py download "<link-share>"
python3 mediafire.py download "<link-share>" <folder-tujuan>
```

Contoh:

```bash
python3 mediafire.py download "https://www.mediafire.com/file/34sepfc5cpm7704/received_922836232251815.mp4/file"
```

Output:

```
received_922836232251815.mp4  100% (5098637/5098637 bytes)
Saved to: received_922836232251815.mp4
```

- Tanpa folder tujuan, file disimpan di folder tempat perintah dijalankan.
- Progress download tampil dalam persen dan byte.

### 2. `info` — lihat metadata file tanpa mengunduh

```bash
python3 mediafire.py info "<link-share>"
```

Output:

```
filename     : received_922836232251815.mp4
quickkey     : 34sepfc5cpm7704
size         : 4.86MB
uploaded     : 2023-05-07 18:46:34
size_bytes   : 5098637
content_type : video/mp4
direct       : https://download2262.mediafire.com/...
```

## Cara Pakai (sebagai library)

```python
from mediafire import download, get_info

# Metadata file
meta = get_info("https://www.mediafire.com/file/xxxx/file.zip/file")
print(meta["size"], meta["uploaded"], meta["content_type"])

# Download ke folder tertentu
path = download("https://www.mediafire.com/file/xxxx/file.zip/file", "downloads")
print(path)
```

## Yang Perlu Diketahui

- **Link share vs link direct.** Link share (`mediafire.com/file/...`) itu yang awet dan bisa dipakai kapan saja. Link direct yang tampil di `info` umurnya pendek — ada token yang kedaluwarsa dalam beberapa jam dan kadang terikat ke IP yang mengambilnya. Habis mengambil link, langsung pakai. Kalau sudah mati, ambil ulang lewat `info` dari link share-nya.
- **Huruf besar/kecil di link tidak masalah.** Script hanya mengambil file key (quickkey) dari link lalu membangun URL-nya sendiri, jadi link yang casing-nya berantakan atau nama filenya salah tetap jalan.
- **Format link yang didukung:**
  - `https://www.mediafire.com/file/<key>/<namafile>/file`
  - `https://www.mediafire.com/file/<key>`
  - `https://www.mediafire.com/download/<key>/<namafile>`
  - quickkey-nya saja, misalnya `34sepfc5cpm7704`
- **Batasan:** hanya untuk file publik dari link share. File yang dihapus, dibuat privat, atau diproteksi password tidak bisa diambil — script akan menampilkan error `Direct link not found`.

## Troubleshooting

| Masalah | Solusi |
|---|---|
| `python: command not found` | Pakai `python3`. |
| `ModuleNotFoundError: No module named 'requests'` | Install `requests`, lihat bagian Persiapan. |
| `externally-managed-environment` saat `pip install` | Bukan error script — sistem melarang pip global. Pakai `apt install python3-requests`, venv, atau `--break-system-packages`. |
| `404 Client Error` | Link share-nya salah/sudah dihapus, atau pakai script versi lama. Pastikan quickkey di link benar. |
| `Direct link not found` | File tidak publik, sudah dihapus, atau diproteksi password. |
| Download berhenti di tengah | Jalankan ulang perintah `download` yang sama; file ditulis ulang dari awal. |
