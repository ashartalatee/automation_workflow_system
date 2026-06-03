# 🧹 duplicate_remover

**Business Automation Lab** › `engines/clean/duplicate_remover`
**Level:** Beginner · Portfolio Ready

---

## 1. Tujuan Engine

`duplicate_remover` adalah engine produksi untuk **mendeteksi dan menghapus baris duplikat dari file CSV** secara otomatis.

Engine ini mendukung:
- ✅ Deduplikasi **semua kolom** (full-row comparison)
- ✅ Deduplikasi **subset kolom** tertentu (misal: hanya cek `email`)
- ✅ Strategi keep: `first`, `last`, atau `none` (hapus semua duplikat)
- ✅ Output file CSV yang bersih
- ✅ Laporan ringkas: jumlah baris dihapus, persentase, dan sample duplikat

---

## 2. Struktur Folder

```
duplicate_remover/
│
├── core/
│   ├── __init__.py
│   └── engine.py            ← Kelas utama DuplicateRemover
│
├── config/
│   ├── __init__.py
│   └── settings.py          ← Semua konfigurasi engine (dataclass)
│
├── utils/
│   ├── __init__.py
│   ├── validator.py         ← Validasi file input & kolom
│   ├── reporter.py          ← Generator laporan ringkas
│   └── logger.py            ← Setup logging terpusat
│
├── tests/
│   ├── __init__.py
│   └── test_duplicate_remover.py   ← Unit tests (pytest)
│
├── datasets/
│   └── customers_raw.csv    ← Contoh data dummy (20 baris, ada duplikat)
│
├── outputs/                 ← Hasil output CSV (auto-generated)
│
├── docs/                    ← Dokumentasi tambahan (opsional)
│
├── run.py                   ← Entry point CLI
├── requirements.txt
└── README.md
```

---

## 3. Penjelasan Tiap File

| File | Fungsi |
|------|--------|
| `core/engine.py` | Kelas `DuplicateRemover` dengan method `load()`, `run()`, `save()`, `get_report()`. Semua logika dedup ada di sini. |
| `config/settings.py` | Dataclass `DuplicateRemoverConfig` — semua parameter tunable (subset, keep, encoding, output path). |
| `utils/validator.py` | Fungsi validasi: cek file exist, tidak kosong, cek nama kolom valid. |
| `utils/reporter.py` | Fungsi `generate_report()` — membangun dict laporan ringkas pasca-dedup. |
| `utils/logger.py` | Fungsi `setup_logger()` — konfigurasi logging ke stdout (dan opsional file). |
| `run.py` | Entry point CLI dengan argparse — jalankan langsung dari terminal. |
| `tests/test_duplicate_remover.py` | 15+ unit test menggunakan pytest, mencakup happy path & edge case. |
| `datasets/customers_raw.csv` | Data dummy 20 baris dengan duplikat ter-embed untuk testing. |

---

## 4. Alur Data

```
[CSV Input]
    │
    ▼
load()  →  pd.read_csv()  →  validate_input_file()
    │
    ▼
run()   →  validate_columns()  →  df.drop_duplicates()
    │
    ▼
save()  →  df.to_csv()  →  [CSV Output]
    │
    ▼
get_report()  →  dict { rows_before, rows_after, removed, rate, sample }
```

---

## 5. Cara Menjalankan

### Install Dependencies
```bash
cd engines/clean/duplicate_remover
pip install -r requirements.txt
```

### Jalankan dengan dataset default
```bash
python run.py
```

### Jalankan dengan opsi kustom
```bash
# Deduplikasi berdasarkan kolom email saja
python run.py --input datasets/customers_raw.csv --subset email

# Deduplikasi berdasarkan email dan nama, simpan baris terakhir
python run.py --input datasets/customers_raw.csv --subset email name --keep last

# Hapus SEMUA baris yang memiliki duplikat (keep none)
python run.py --input datasets/customers_raw.csv --subset email --keep none

# Output ke path kustom
python run.py --input datasets/customers_raw.csv --output outputs/hasil_bersih.csv
```

### Jalankan sebagai Python module
```python
from config.settings import DuplicateRemoverConfig
from core.engine import DuplicateRemover

config = DuplicateRemoverConfig(
    subset_columns=["email"],
    keep="first",
)
engine = DuplicateRemover(config)
engine.load("datasets/customers_raw.csv").run().save()
print(engine.get_report())
```

### Jalankan Unit Tests
```bash
python -m pytest tests/ -v
```

---

## 6. Contoh Input

**`datasets/customers_raw.csv`** (20 baris, mengandung 6 baris duplikat):

```
id,name,email,phone,city,join_date
1,Budi Santoso,budi@email.com,08111111111,Surabaya,2024-01-10
2,Siti Rahayu,siti@email.com,08222222222,Jakarta,2024-01-15
3,Andi Wijaya,andi@email.com,08333333333,Bandung,2024-02-01
4,Budi Santoso,budi@email.com,08111111111,Surabaya,2024-01-10  ← duplikat
...
```

---

## 7. Contoh Output

**`outputs/cleaned_output.csv`** (setelah `python run.py`):

```
id,name,email,phone,city,join_date
1,Budi Santoso,budi@email.com,08111111111,Surabaya,2024-01-10
2,Siti Rahayu,siti@email.com,08222222222,Jakarta,2024-01-15
3,Andi Wijaya,andi@email.com,08333333333,Bandung,2024-02-01
5,Dewi Kusuma,dewi@email.com,08444444444,Medan,2024-02-10
...
```

**Report di terminal:**
```
=======================================================
  DUPLICATE REMOVER — SUMMARY REPORT
=======================================================
  Rows before   : 20
  Rows after    : 14
  Removed       : 6 (30.0%)
  Keep strategy : first
  Columns used  : ALL
  Output saved  : outputs/cleaned_output.csv
=======================================================
```

---

## 8. Roadmap Versi Berikutnya

### v1.1 — Enhanced Detection
- [ ] Fuzzy matching (misal: "Budi Santoso" vs "budi santoso") menggunakan `rapidfuzz`
- [ ] Case-insensitive comparison per kolom
- [ ] Whitespace normalization sebelum dedup

### v1.2 — Multi-File Support
- [ ] Menerima list file CSV → merge → dedup → output
- [ ] Dedup lintas folder (batch mode)

### v1.3 — Output & Audit
- [ ] Export laporan ke `reports/dedup_report_<timestamp>.json`
- [ ] Export baris duplikat ke `outputs/duplicates_found.csv` untuk audit
- [ ] Summary visual (ASCII bar chart di terminal)

### v2.0 — Integration Ready
- [ ] REST API endpoint menggunakan FastAPI (`POST /clean/duplicate-remover`)
- [ ] Support format Excel (`.xlsx`) via openpyxl
- [ ] Support Google Sheets sebagai input/output
- [ ] Database connector (PostgreSQL, MySQL)
- [ ] Streaming mode untuk file besar (chunked processing)

---

*Business Automation Lab — `engines/clean/duplicate_remover` · v1.0*
