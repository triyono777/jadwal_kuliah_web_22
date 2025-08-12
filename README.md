## Jadwal Kuliah Web (Python + React)

Aplikasi optimasi jadwal kuliah menggunakan kombinasi CSP dan Algoritma Genetika sesuai spesifikasi pada `alur_aplikasi.md`.

### Arsitektur
- Backend: FastAPI (Python), koneksi ke Supabase (Postgres hosted)
- Frontend: React + Vite (TypeScript)
- Database: Schema dan seed tersedia di `backend/db/*.sql`

### Prasyarat
- Python 3.10+
- Node.js 18+
- Project Supabase (URL dan anon/service role key)

### Setup Backend
1. Buat virtualenv dan install dependensi:
   ```bash
   cd backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Salin environment:
   ```bash
   cp .env.example .env
   # Isi SUPABASE_URL dan SUPABASE_ANON_KEY (atau SERVICE_ROLE di server)
   ```
3. Inisialisasi database (schema + seed) di Supabase:
   ```bash
   # Buka Supabase Dashboard -> SQL editor
   # Jalankan isi dari backend/db/schema.sql dan backend/db/seed.sql
   ```
4. Jalankan API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Setup Frontend
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Akses UI di `http://localhost:5173`.

### Cara Pakai
- Di UI, pilih preset parameter atau set manual: `G`, `N`, `p_m`, `k`.
- Klik "Generate Jadwal" untuk menjalankan GA.
- Hasil akan menampilkan fitness, ringkasan pelanggaran, dan tabel jadwal (ID referensi).
- Hasil kini menampilkan summary (termasuk parameter), grafik konvergensi fitness, dan tombol ekspor PDF/Excel.
- Data diambil langsung dari database sesuai schema. Edit data di DB untuk menyesuaikan.

### Catatan Implementasi
- Hard constraints: konflik ruangan, konflik dosen, konflik kelas pada slot yang sama.
- Soft constraints: kapasitas ruangan, preferensi waktu dosen.
- Fitness: `1000 - 100*V_hard - 10*V_soft`.

### Struktur Proyek
```
backend/
  app/
    main.py        # Endpoint FastAPI
    db.py          # Koneksi dan pembacaan data
    ga.py          # Mesin GA
    models.py      # Model domain
    schemas.py     # Skema Pydantic + presets
  db/
    schema.sql     # Tabel
    seed.sql       # Data contoh
  scripts/
    init_db.py     # Eksekusi schema + seed
  requirements.txt
  .env.example
frontend/
  src/
    App.tsx, api.ts, main.tsx
  index.html, vite.config.ts, package.json
README.md
alur_aplikasi.md
```

### Produksi
- Konfigurasi CORS via `backend/.env` (`CORS_ORIGINS`).
- Jalankan backend via proses manager (uvicorn/gunicorn) dan deploy frontend sebagai static build (`npm run build`).
