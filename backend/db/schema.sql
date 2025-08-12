-- Schema per alur_aplikasi.md
CREATE TABLE IF NOT EXISTS dosen (
  id SERIAL PRIMARY KEY,
  nama TEXT NOT NULL,
  batas_sks INTEGER NOT NULL DEFAULT 12,
  kesediaan JSONB DEFAULT '{}'::jsonb,
  keahlian_matkul_ids INTEGER[] DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS matkul (
  id SERIAL PRIMARY KEY,
  nama TEXT NOT NULL,
  sks INTEGER NOT NULL CHECK (sks >= 1 AND sks <= 4),
  jenis_ruangan TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kelas (
  id SERIAL PRIMARY KEY,
  nama TEXT NOT NULL,
  jumlah_mahasiswa INTEGER NOT NULL CHECK (jumlah_mahasiswa > 0)
);

CREATE TABLE IF NOT EXISTS kelas_matkul (
  id SERIAL PRIMARY KEY,
  id_kelas INTEGER NOT NULL REFERENCES kelas(id) ON DELETE CASCADE,
  id_matkul INTEGER NOT NULL REFERENCES matkul(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ruangan (
  id SERIAL PRIMARY KEY,
  nama TEXT NOT NULL,
  jenis TEXT NOT NULL,
  kapasitas INTEGER NOT NULL CHECK (kapasitas > 0)
);

CREATE TABLE IF NOT EXISTS slot_waktu (
  id SERIAL PRIMARY KEY,
  hari TEXT NOT NULL,
  waktu_mulai TEXT NOT NULL,
  waktu_selesai TEXT NOT NULL
);
