"""
pipeline.py
Data Preparation & Pipeline Project - AI Engineering Bootcamp
 
Pipeline ETL untuk dataset otomotif:
    Raw CSV -> Load -> Inspect -> Clean -> Transform -> Processed CSV
 
Cara menjalankan:
    python src/pipeline.py
"""

import os
import pandas as pd
import numpy as np
 
# ---------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "automobileEDA_dirty_training.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "automobileEDA_processed.csv")
 
# Token dianggap sebagai missing value saat membaca CSV
MISSING_TOKENS = ["?", "NA", "N/A", "na", "n/a", "-", "--", "null", "NULL", "None", ""]
 
# Kolom numerik yang akan dinormalisasi dengan Min-Max Scaling
KOLOM_NORMALISASI = ["price", "horsepower", "engine-size", "curb-weight"]
 
# Kolom kategorikal yang akan di-One-Hot Encoding
KOLOM_ONEHOT = ["drive-wheels", "body-style", "aspiration",
                "engine-type", "engine-location", "fuel-system"]
 
# Pemetaan manual untuk kolom kategorikal berurutan (ordinal)
PETA_ORDINAL = {"low": 0, "medium": 1, "high": 2}
PETA_PINTU = {"two": 2, "four": 4}
 
# Penyeragaman ejaan kategori yang bermakna sama
PETA_EJAAN = {"drive-wheels": {"awd": "4wd"}}

def garis(judul):
    """Mencetak pemisah antar tahap agar output terminal mudah dibaca."""
    print("\n" + "=" * 72)
    print(judul)
    print("=" * 72)

def load_data(path=RAW_PATH):
    """Membaca dataset mentah dari folder data/raw/ menjadi DataFrame."""
    garis("TAHAP 1 - LOAD DATA  (EXTRACT)")
 
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {path}\n"
            "Pastikan automobileEDA_dirty_training.csv ada di folder data/raw/"
        )
 
    df = pd.read_csv(path, na_values=MISSING_TOKENS, skipinitialspace=True)
 
    print(f"Sumber file : {os.path.relpath(path, BASE_DIR)}")
    print(f"Dataset dimuat: {df.shape[0]} baris x {df.shape[1]} kolom")
    return df

def inspect_data(df):
    """Memeriksa struktur, tipe data, missing values, duplikat, dan kategori."""
    garis("TAHAP 2 - DATA INSPECTION")
 
    print(">> Lima baris pertama:")
    print(df.head().to_string())
 
    print(f"\n>> Ukuran dataset : {df.shape[0]} baris, {df.shape[1]} kolom")
 
    print("\n>> Nama kolom:")
    print(list(df.columns))
 
    print("\n>> Tipe data setiap kolom:")
    print(df.dtypes.to_string())
 
    print("\n>> Missing values per kolom (hanya yang > 0):")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        print("   Tidak ada missing values.")
    else:
        for kolom, jumlah in missing.items():
            print(f"   {kolom:<20} {jumlah:>4} nilai ({jumlah / len(df) * 100:.1f}%)")
 
    duplikat = int(df.duplicated().sum())
    print(f"\n>> Duplicate records : {duplikat} baris")
 
    print("\n>> Nilai unik kolom kategorikal:")
    for kolom in df.select_dtypes(include=["object", "string"]).columns:
        unik = sorted(df[kolom].dropna().astype(str).unique())
        if len(unik) <= 12:
            print(f"   {kolom:<20} {unik}")
        else:
            print(f"   {kolom:<20} ({len(unik)} nilai unik) contoh: {unik[:5]}")
 
    print("\n>> Deteksi penulisan tidak konsisten (huruf besar/kecil & spasi):")
    ditemukan = False
    for kolom in df.select_dtypes(include=["object", "string"]).columns:
        seri = df[kolom].dropna().astype(str)
        n_spasi = int((seri != seri.str.strip()).sum())
        n_asli = seri.str.strip().nunique()
        n_kecil = seri.str.strip().str.lower().nunique()
        if n_spasi > 0 or n_asli != n_kecil:
            print(f"   {kolom:<20} spasi berlebih: {n_spasi:>3} | "
                  f"kategori {n_asli} -> {n_kecil} setelah lowercase")
            ditemukan = True
    if not ditemukan:
        print("   Tidak ditemukan.")
 
    print("\n>> Catatan kolom numerik yang sudah ternormalisasi (0-1):")
    for kolom in df.select_dtypes(include=np.number).columns:
        if 0 <= df[kolom].min() and df[kolom].max() <= 1 and df[kolom].nunique() > 5:
            print(f"   {kolom:<20} min={df[kolom].min():.4f} max={df[kolom].max():.4f} "
                  f"-> tidak perlu di-scaling ulang")
 
    return {"shape": df.shape, "missing": missing.to_dict(), "duplicates": duplikat}

def clean_data(df):
    """
    Membersihkan dataset:
      a. Menghapus spasi berlebih pada kolom teks
      b. Menyeragamkan penulisan kategori menjadi huruf kecil
      c. Menyeragamkan ejaan kategori yang bermakna sama (awd -> 4wd)
      d. Memperbaiki tipe data kolom tanggal
      e. Menghapus duplicate records
      f. Mengisi missing values (median untuk numerik, modus untuk kategorikal)
    """
    garis("TAHAP 3 - DATA CLEANING")
 
    df = df.copy()
    baris_awal = len(df)
    missing_awal = int(df.isnull().sum().sum())
    kolom_berubah = []
 
    kolom_teks = df.select_dtypes(include=["object", "string"]).columns.tolist()
 
    # --- a & b. Strip spasi + lowercase ---
    for kolom in kolom_teks:
        sebelum = df[kolom].copy()
        df[kolom] = df[kolom].astype("string").str.strip().str.lower()
        df[kolom] = df[kolom].replace({"nan": pd.NA, "": pd.NA})
        if not sebelum.astype("string").equals(df[kolom]):
            kolom_berubah.append(kolom)
    print(f"a. Strip spasi + lowercase pada {len(kolom_teks)} kolom teks")
    print(f"   Kolom yang berubah: {kolom_berubah}")
 
    # --- c. Seragamkan ejaan kategori yang bermakna sama ---
    for kolom, peta in PETA_EJAAN.items():
        if kolom in df.columns:
            jumlah = int(df[kolom].isin(peta.keys()).sum())
            df[kolom] = df[kolom].replace(peta)
            print(f"b. Penyeragaman ejaan '{kolom}': {peta} ({jumlah} baris terdampak)")
 
    # --- d. Perbaiki tipe data tanggal ---
    if "transaction_date" in df.columns:
        sebelum_valid = df["transaction_date"].notna().sum()
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"], format="mixed", dayfirst=False, errors="coerce"
        )
        sesudah_valid = df["transaction_date"].notna().sum()
        print(f"c. Konversi 'transaction_date' ke datetime: "
              f"{sebelum_valid} -> {sesudah_valid} nilai valid")
        if "transaction_date" not in kolom_berubah:
            kolom_berubah.append("transaction_date")
 
    # --- e. Hapus duplicate records ---
    duplikat = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"d. Duplicate records dihapus: {duplikat} baris")
 
    # --- f. Isi missing values ---
    print("e. Penanganan missing values:")
    for kolom in df.columns:
        kosong = int(df[kolom].isnull().sum())
        if kosong == 0:
            continue
 
        if pd.api.types.is_numeric_dtype(df[kolom]):
            nilai, metode = df[kolom].median(), "median"
        elif pd.api.types.is_datetime64_any_dtype(df[kolom]):
            nilai, metode = df[kolom].mode().iloc[0], "modus (tanggal)"
        else:
            modus = df[kolom].mode()
            nilai = modus.iloc[0] if not modus.empty else "unknown"
            metode = "modus"
 
        df[kolom] = df[kolom].fillna(nilai)
        if kolom not in kolom_berubah:
            kolom_berubah.append(kolom)
        print(f"   {kolom:<20} {kosong:>3} nilai -> diisi {metode} = {nilai}")
 
    # --- Ringkasan ---
    print("\n>> RINGKASAN CLEANING")
    print(f"   Jumlah baris   : {baris_awal} -> {len(df)}")
    print(f"   Missing values : {missing_awal} -> {int(df.isnull().sum().sum())}")
    print(f"   Duplikat dihapus: {duplikat}")
    print(f"   Kolom berubah  : {len(kolom_berubah)} kolom")
 
    return df

def min_max_scaling(seri):
    """Min-Max Scaling manual: (x - min) / (max - min). Hasil dalam rentang 0-1."""
    rentang = seri.max() - seri.min()
    if rentang == 0:
        return pd.Series(0.0, index=seri.index)
    return (seri - seri.min()) / rentang
 
 
def transform_data(df):
    """
    Transformasi data:
      a. Min-Max Scaling pada kolom numerik  -> kolom baru '<nama>_scaled'
      b. One-Hot Encoding pada kolom kategorikal nominal
      c. Ordinal Encoding pada kolom kategorikal berurutan
    """
    garis("TAHAP 4 - DATA TRANSFORMATION")
 
    df = df.copy()
    contoh_perbandingan = {}
 
    # --- a. Min-Max Scaling ---
    print("a. Min-Max Scaling (hasil 0-1):")
    for kolom in KOLOM_NORMALISASI:
        if kolom not in df.columns:
            continue
        kolom_baru = f"{kolom}_scaled"
        df[kolom_baru] = min_max_scaling(df[kolom])
 
        contoh_perbandingan[kolom] = (
            df[kolom].head(3).tolist(),
            df[kolom_baru].head(3).round(4).tolist(),
        )
        print(f"   {kolom:<14} min={df[kolom].min():>9.2f}  max={df[kolom].max():>9.2f}"
              f"  ->  {kolom_baru}")
        print(f"   {'contoh':<14} {contoh_perbandingan[kolom][0]}  ->  "
              f"{contoh_perbandingan[kolom][1]}")
 
    # --- b. One-Hot Encoding ---
    print("\nb. One-Hot Encoding:")
    for kolom in KOLOM_ONEHOT:
        if kolom not in df.columns:
            continue
        dummies = pd.get_dummies(df[kolom], prefix=kolom, dtype=int)
        df = pd.concat([df, dummies], axis=1)
        print(f"   {kolom:<16} {df[kolom].nunique()} kategori -> {list(dummies.columns)}")
 
    # --- c. Ordinal Encoding ---
    print("\nc. Ordinal / Label Encoding:")
    if "horsepower-binned" in df.columns:
        df["horsepower_ordinal"] = df["horsepower-binned"].map(PETA_ORDINAL)
        print(f"   horsepower-binned  {PETA_ORDINAL}  -> horsepower_ordinal")
 
    if "num-of-doors" in df.columns:
        df["num_of_doors_numeric"] = df["num-of-doors"].map(PETA_PINTU)
        print(f"   num-of-doors       {PETA_PINTU}  -> num_of_doors_numeric")
 
    print(f"\n>> Jumlah kolom setelah transformasi: {df.shape[1]}")
    return df

def save_data(df, path=PROCESSED_PATH):
    """Menyimpan processed dataset ke folder data/processed/."""
    garis("TAHAP 5 - SAVE DATA  (LOAD)")
 
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
 
    print(f"Processed dataset : {os.path.relpath(path, BASE_DIR)}")
    print(f"Ukuran akhir      : {df.shape[0]} baris x {df.shape[1]} kolom")
    return path

def run_pipeline():
    """Menjalankan seluruh tahap ETL dari awal sampai akhir."""
    print("\n" + "#" * 72)
    print("#  DATA PIPELINE - AUTOMOBILE DATASET")
    print("#  Raw CSV -> Load -> Inspect -> Clean -> Transform -> Processed CSV")
    print("#" * 72)
 
    df_raw = load_data()                    # EXTRACT
    ringkasan = inspect_data(df_raw)        # INSPECT
    df_clean = clean_data(df_raw)           # TRANSFORM - cleaning
    df_final = transform_data(df_clean)     # TRANSFORM - scaling & encoding
    save_data(df_final)                     # LOAD
 
    garis("PIPELINE SELESAI")
    print(f"Baris : {ringkasan['shape'][0]} (raw) -> {df_final.shape[0]} (processed)")
    print(f"Kolom : {ringkasan['shape'][1]} (raw) -> {df_final.shape[1]} (processed)")
    print("Dataset mentah di data/raw/ tidak diubah.\n")
 
    return df_final
 
 
if __name__ == "__main__":
    run_pipeline()


