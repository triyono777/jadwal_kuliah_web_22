-- Seed sesuai spesifikasi: 39 dosen, 24 kelas, 24 matkul, 17 ruangan, Senin–Jumat, 08:00–16:00
TRUNCATE kelas_matkul, dosen, matkul, kelas, ruangan, slot_waktu RESTART IDENTITY CASCADE;

-- 24 Mata kuliah (kombinasi teori/lab)
INSERT INTO matkul (nama, sks, jenis_ruangan) VALUES
 ('Matkul 01', 3, 'teori'),
 ('Matkul 02', 3, 'teori'),
 ('Matkul 03', 3, 'teori'),
 ('Matkul 04', 1, 'lab'),
 ('Matkul 05', 3, 'teori'),
 ('Matkul 06', 3, 'teori'),
 ('Matkul 07', 3, 'teori'),
 ('Matkul 08', 1, 'lab'),
 ('Matkul 09', 3, 'teori'),
 ('Matkul 10', 3, 'teori'),
 ('Matkul 11', 3, 'teori'),
 ('Matkul 12', 1, 'lab'),
 ('Matkul 13', 3, 'teori'),
 ('Matkul 14', 3, 'teori'),
 ('Matkul 15', 3, 'teori'),
 ('Matkul 16', 1, 'lab'),
 ('Matkul 17', 3, 'teori'),
 ('Matkul 18', 3, 'teori'),
 ('Matkul 19', 3, 'teori'),
 ('Matkul 20', 1, 'lab'),
 ('Matkul 21', 3, 'teori'),
 ('Matkul 22', 3, 'teori'),
 ('Matkul 23', 3, 'teori'),
 ('Matkul 24', 1, 'lab');

-- 24 Kelas
INSERT INTO kelas (nama, jumlah_mahasiswa)
SELECT 'KEL-' || LPAD(i::text, 2, '0') as nama,
       (25 + ((i*3) % 26))::int as jumlah_mahasiswa
FROM generate_series(1,24) s(i);

-- 17 Ruangan (12 teori, 5 lab)
INSERT INTO ruangan (nama, jenis, kapasitas) VALUES
 ('R-101', 'teori', 40),
 ('R-102', 'teori', 45),
 ('R-103', 'teori', 50),
 ('R-104', 'teori', 35),
 ('R-105', 'teori', 60),
 ('R-106', 'teori', 48),
 ('R-107', 'teori', 42),
 ('R-108', 'teori', 55),
 ('R-109', 'teori', 38),
 ('R-110', 'teori', 52),
 ('R-111', 'teori', 36),
 ('R-112', 'teori', 44),
 ('LAB-1', 'lab', 40),
 ('LAB-2', 'lab', 35),
 ('LAB-3', 'lab', 45),
 ('LAB-4', 'lab', 32),
 ('LAB-5', 'lab', 50);

-- Slot waktu: Senin s.d. Jumat, blok 2 jam dari 08:00-16:00 (4 slot per hari)
INSERT INTO slot_waktu (hari, waktu_mulai, waktu_selesai) VALUES
 ('Senin',  '08:00', '10:00'),
 ('Senin',  '10:00', '12:00'),
 ('Senin',  '12:00', '14:00'),
 ('Senin',  '14:00', '16:00'),
 ('Selasa', '08:00', '10:00'),
 ('Selasa', '10:00', '12:00'),
 ('Selasa', '12:00', '14:00'),
 ('Selasa', '14:00', '16:00'),
 ('Rabu',   '08:00', '10:00'),
 ('Rabu',   '10:00', '12:00'),
 ('Rabu',   '12:00', '14:00'),
 ('Rabu',   '14:00', '16:00'),
 ('Kamis',  '08:00', '10:00'),
 ('Kamis',  '10:00', '12:00'),
 ('Kamis',  '12:00', '14:00'),
 ('Kamis',  '14:00', '16:00'),
 ('Jumat',  '08:00', '10:00'),
 ('Jumat',  '10:00', '12:00'),
 ('Jumat',  '12:00', '14:00'),
 ('Jumat',  '14:00', '16:00');

-- 39 Dosen: keahlian 3 matkul, preferensi waktu realistis (subset slot)
INSERT INTO dosen (nama, batas_sks, kesediaan, keahlian_matkul_ids)
SELECT 'Dosen ' || LPAD(i::text,2,'0') as nama,
       12 as batas_sks,
       (
         -- Preferensi: untuk variasi, dosen genap suka pagi, ganjil suka siang
         CASE WHEN (i % 2) = 0 THEN
           '{"Senin":["08:00-10:00","10:00-12:00"],"Rabu":["08:00-10:00"],"Jumat":["08:00-10:00","10:00-12:00"]}'::jsonb
         ELSE
           '{"Selasa":["12:00-14:00","14:00-16:00"],"Kamis":["12:00-14:00","14:00-16:00"]}'::jsonb
         END
       ) as kesediaan,
       ARRAY[ ((i-1) % 24)+1,
              ((i+7-1) % 24)+1,
              ((i+13-1) % 24)+1 ]::int[] as keahlian_matkul_ids
FROM generate_series(1,39) s(i);

-- Relasi kelas_matkul: tiap kelas ambil 8 matkul (total 24*8 = 192)
INSERT INTO kelas_matkul (id_kelas, id_matkul)
SELECT k.id, m.id
FROM kelas k
CROSS JOIN LATERAL (
  SELECT id
  FROM matkul
  WHERE ((id + k.id) % 3) = 0
  ORDER BY id
  LIMIT 8
) m;
