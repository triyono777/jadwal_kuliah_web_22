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

- [6e37419] Chore: install frontend deps and update lockfile for chart/pdf/excel.
  - Memasang `react-chartjs-2`, `chart.js`, `jspdf`, `jspdf-autotable`, `xlsx`, `file-saver`.

- [8004c05] UI/Backend: human-readable schedule, fitness explanation, and explicit GA params.
  - Backend: menambah `hasil_readable` (nama entitas) dan `fitness_explanation`.
  - Frontend: menampilkan jadwal readable, parameter G/N/p_m/k, dan penjelasan fitness.

- [bc689cd] UX: append timestamp (tanggal_jam_menit) to export filenames.
  - Nama file ekspor sekarang `jadwal_kuliah_YYYYMMDD_HHMM.(pdf|xlsx)` agar unik.

- [7297b92] Export: include human-readable schedule in PDF and Excel outputs.
  - Ekspor menyertakan jadwal readable (kelas, matkul, dosen, ruangan, slot). 

- [8a7c4ae] Seed: adjust rooms capacity and clear lecturer availability to remove soft violations.
  - Naikkan kapasitas ruangan dan kosongkan preferensi dosen agar V_soft → 0.

- [fa57160] Seed: expand dataset (12 matkul, 6 kelas, 7 ruangan, 9 slot, 8 dosen, rich kelas_matkul).
  - Dataset lebih besar untuk pengujian performa dan kualitas solusi.

- [3fde448] Feature: schedule count validation (expected vs generated).
  - Backend menghitung expected dari `kelas_matkul` dan membandingkan dengan hasil; frontend menampilkan status.

- [765082d] Seed: conform to spec (39 dosen, 24 kelas, 24 matkul, 17 ruangan, Senin–Jumat 08:00–16:00, 4 slots/day).
  - Dataset dibangkitkan dengan pola terkontrol; dosen tanpa preferensi untuk fokus pada hard constraints.

- [0540b67] GA: conflict-aware init, capacity-aware rooms, elitism; readable conflicts.
  - Inisialisasi menghindari konflik slot (ruang/dosen/kelas), room mempertimbangkan kapasitas, elitism 10%, serta pesan konflik yang mudah dibaca.

- [c1c2fb4] GA: SKS-aware lecturer assignment; Seed: aktifkan preferensi waktu dosen.
  - Inisialisasi memperhatikan batas SKS dosen; seed menambahkan `kesediaan` untuk tekanan S2.
