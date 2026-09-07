# Data Preparation & Pipeline Project — Automobile Dataset
 
Pipeline ETL sederhana untuk membersihkan dan mentransformasi dataset otomotif menggunakan Python dan Pandas.
 
## Deskripsi Dataset
 
Dataset berisi 205 baris data spesifikasi dan harga mobil dengan 30 kolom, mencakup atribut teknis (engine-size, horsepower, curb-weight), atribut kategorikal (make, body-style, drive-wheels), serta harga jual (price).
 
**Sumber dataset:** https://s.id/dataset-sesi-3
File utama: `automobileEDA_dirty_training.csv`
 
## Struktur Folder
 
```
data-pipeline-assignment/
├── data/
│   ├── raw/automobileEDA_dirty_training.csv
│   └── processed/automobileEDA_processed.csv
├── src/pipeline.py
├── documentation/data-flow-diagram.png
├── README.md
└── requirements.txt
```
 
## Kondisi Awal Dataset
 
| Aspek | Nilai |
|---|---|
| Jumlah baris | 205 |
| Jumlah kolom | 30 |
| Total missing values | 17 |
| Duplicate records | 4 |
 
### Permasalahan yang Ditemukan
 
1. **Missing values** pada 7 kolom:
   stroke (4), horsepower (3), price (3), transaction_date (2),
   make (2), num-of-doors (2), horsepower-binned (1)
 
2. **Duplicate records**: 4 baris identik
 
3. **Penulisan kategori tidak konsisten**:
 
   | Kolom | Contoh nilai kotor | Kategori awal | Setelah dibersihkan |
   |---|---|---|---|
   | make | ALFA-ROMERO, alfa-romero, "dodge  " | 25 | 22 |
   | body-style | SEDAN, Sedan, sedan | 7 | 5 |
   | drive-wheels | RWD, rwd, AWD, 4wd | 5 | 3 |
   | fuel-system | MPFI, Mpfi, mpfi | 10 | 8 |
 
4. **Tipe data belum sesuai**: kolom `transaction_date` terbaca sebagai
   teks dengan format campur (2025-01-01, 02/01/2025, 04-Jan-2025)
 
5. **Ejaan berbeda bermakna sama**: `awd` dan `4wd` pada drive-wheels
 
6. **Catatan**: kolom `length` dan `width` sudah ternormalisasi 0–1 di
   dataset sumber, sehingga tidak di-scaling ulang
 
## Data Cleaning
 
| Proses | Kolom | Metode | Alasan |
|---|---|---|---|
| Hapus spasi + lowercase | 11 kolom teks | `.str.strip().str.lower()` | Menyatukan kategori yang sama tapi beda penulisan |
| Seragamkan ejaan | drive-wheels | `awd` → `4wd` | Keduanya bermakna penggerak semua roda |
| Perbaiki tipe data | transaction_date | `pd.to_datetime()` | Format campur perlu diseragamkan |
| Hapus duplikat | semua kolom | `drop_duplicates()` | Data ganda membuat statistik bias |
| Isi missing numerik | stroke, horsepower, price | **median** | Median tahan outlier; price sebarannya miring ke kanan |
| Isi missing kategorikal | make, num-of-doors, horsepower-binned | **modus** | Kategori tidak bisa dirata-rata |
 
**Mengapa missing value diisi, bukan dihapus?**
Baris bermasalah hanya 17 dari 205 (8,3%) dan sisa kolomnya masih valid.
Menghapus baris berarti membuang data yang sebagian besar masih berguna.
 
**Hasil:** 205 baris → **201 baris**, missing values 17 → **0**
 
## Data Transformation
 
### 1. Min-Max Scaling
 
Rumus: `(x - min) / (max - min)` → hasil dalam rentang 0–1
 
| Kolom asal | Kolom baru | Min | Max |
|---|---|---|---|
| price | price_scaled | 5.118 | 45.400 |
| horsepower | horsepower_scaled | 48 | 262 |
| engine-size | engine-size_scaled | 61 | 326 |
| curb-weight | curb-weight_scaled | 1.488 | 4.066 |
 
**Contoh sebelum dan sesudah:**
 
| price (asli) | price_scaled |
|---|---|
| 13.495 | 0,2080 |
| 16.500 | 0,2826 |
| 13.950 | 0,2193 |
 
**Alasan pemilihan kolom:** keempatnya punya satuan dan rentang yang
sangat berbeda. Tanpa normalisasi, kolom price akan mendominasi
perhitungan jarak pada model karena angkanya jauh lebih besar.
 
### 2. Encoding Kategorikal
 
| Kolom | Metode | Kolom hasil |
|---|---|---|
| drive-wheels | One-Hot | drive-wheels_4wd, _fwd, _rwd |
| body-style | One-Hot | 5 kolom |
| aspiration | One-Hot | 2 kolom |
| engine-type | One-Hot | 6 kolom |
| engine-location | One-Hot | 2 kolom |
| fuel-system | One-Hot | 8 kolom |
| horsepower-binned | Ordinal | horsepower_ordinal (low=0, medium=1, high=2) |
| num-of-doors | Pemetaan | num_of_doors_numeric (two=2, four=4) |
 
**Alasan:** One-Hot dipakai untuk kategori nominal yang tidak punya
urutan. Ordinal Encoding dipakai untuk horsepower-binned karena
low–medium–high memang berjenjang.
 
## Ringkasan Sebelum dan Sesudah
 
| Aspek | Sebelum | Sesudah |
|---|---|---|
| Jumlah baris | 205 | 201 |
| Jumlah kolom | 30 | 62 |
| Missing values | 17 | 0 |
| Duplicate records | 4 | 0 |
 
## Alur ETL
 
```
Raw CSV → Load → Inspect → Clean → Transform → Processed CSV
```
 
| Tahap | Proses | Function |
|---|---|---|
| **Extract** | Membaca CSV dari data/raw/ | `load_data()` |
| **Transform** | Memeriksa kondisi dataset | `inspect_data()` |
| **Transform** | Membersihkan data | `clean_data()` |
| **Transform** | Normalisasi & encoding | `transform_data()` |
| **Load** | Menyimpan ke data/processed/ | `save_data()` |
 
Diagram lengkap: `documentation/data-flow-diagram.png`
 
## Cara Menjalankan
 
```bash
# 1. Clone repository
git clone https://github.com/USERNAME/assignment-data-pipeline-nama-peserta.git
cd assignment-data-pipeline-nama-peserta
 
# 2. Buat virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
 
# 3. Install dependency
pip install -r requirements.txt
 
# 4. Jalankan pipeline
python3 src/pipeline.py
```
 
## Lokasi Processed Dataset
 
`data/processed/automobileEDA_processed.csv` — dihasilkan otomatis
setiap kali `pipeline.py` dijalankan. Dataset mentah di `data/raw/`
tidak pernah diubah atau ditimpa.
 
## Dependency
 
- pandas >= 2.0.0
- numpy >= 1.24.0
