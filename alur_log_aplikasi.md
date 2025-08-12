# Alur Log Aplikasi

Catatan ringkas setiap perubahan penting agar dapat dianalisis AI untuk memahami evolusi fitur dan arsitektur.

- [ed34bad] Initialize repository with spec and gitignore.
  - Tambah `alur_aplikasi.md` sebagai spesifikasi dan `.gitignore`.

- [22a0b75] Backend: FastAPI GA+CSP engine with Supabase-ready schema.
  - Endpoint `/health`, `/presets`, `/generate`.
  - GA: evaluasi hard (C1,C2,C3) dan soft (S1,S2), fitness `1000 - 100*V_hard - 10*V_soft`.
  - DB schema + seed SQL, script init; konfigurasi env.

- [bd6c878] Frontend: React + Vite UI for GA controls and results.
  - Form parameter GA, preset, tombol generate.
  - Tabel hasil assignment (ID) dan detail pelanggaran.

- [fc502a5] Docs: usage guide for backend, frontend, and DB setup.
  - Panduan setup dan run lokal.

- [a4d4f60] Backend: switch DB layer to Supabase client.
  - Ganti psycopg ke Supabase Python client; env `SUPABASE_URL` dan `SUPABASE_*KEY`.
  - Init DB via Supabase SQL editor.

- [8923c91] Fix: add @vitejs/plugin-react to devDependencies for Vite.
  - Perbaikan dependency dev agar `npm run dev` berjalan.

- [c196400] Docs: refine README Python venv command; add package-lock.json.
  - Ubah perintah venv ke `python3 -m venv` untuk kompatibilitas.
  - Tambahkan `frontend/package-lock.json` untuk instalasi deterministik.

- [b8bf601] Feature: summary, fitness convergence chart, and export (PDF/Excel).
  - Backend mengembalikan `summary` (memuat parameter) dan `fitness_history`.
  - Frontend menampilkan summary, grafik konvergensi (Chart.js), ekspor PDF (jsPDF) & Excel (xlsx).
