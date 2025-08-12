-- Expanded seed dataset
TRUNCATE kelas_matkul, dosen, matkul, kelas, ruangan, slot_waktu RESTART IDENTITY CASCADE;

-- Mata kuliah
INSERT INTO matkul (nama, sks, jenis_ruangan) VALUES
 ('Algoritma', 3, 'teori'),                  -- id=1
 ('Basis Data', 3, 'teori'),                 -- id=2
 ('Praktikum Basis Data', 1, 'lab'),         -- id=3
 ('Struktur Data', 3, 'teori'),              -- id=4
 ('Sistem Operasi', 3, 'teori'),             -- id=5
 ('Pemrograman Web', 3, 'teori'),            -- id=6
 ('Jaringan Komputer', 3, 'teori'),          -- id=7
 ('Praktikum Jaringan', 1, 'lab'),           -- id=8
 ('Praktikum Struktur Data', 1, 'lab'),      -- id=9
 ('Kecerdasan Buatan', 3, 'teori'),          -- id=10
 ('Analisis Algoritma', 3, 'teori'),         -- id=11
 ('Rekayasa Perangkat Lunak', 3, 'teori');   -- id=12

-- Kelas
INSERT INTO kelas (nama, jumlah_mahasiswa) VALUES
 ('IF-41-01', 32),  -- id=1
 ('IF-41-02', 36),  -- id=2
 ('IF-41-03', 30),  -- id=3
 ('IF-41-04', 40),  -- id=4
 ('IF-42-01', 28),  -- id=5
 ('IF-42-02', 35);  -- id=6

-- Relasi kelas-matkul (kurikulum ringkas)
INSERT INTO kelas_matkul (id_kelas, id_matkul) VALUES
 -- IF-41-01
 (1,1),(1,2),(1,3),(1,4),(1,6),(1,7),(1,8),(1,9),
 -- IF-41-02
 (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,9),
 -- IF-41-03
 (3,1),(3,2),(3,3),(3,4),(3,6),(3,7),(3,8),(3,10),
 -- IF-41-04
 (4,1),(4,2),(4,3),(4,5),(4,6),(4,7),(4,8),(4,11),
 -- IF-42-01
 (5,2),(5,3),(5,4),(5,6),(5,7),(5,9),(5,10),(5,12),
 -- IF-42-02
 (6,1),(6,2),(6,3),(6,4),(6,5),(6,6),(6,8),(6,12);

-- Ruangan
INSERT INTO ruangan (nama, jenis, kapasitas) VALUES
 ('R-101', 'teori', 40),  -- id=1
 ('R-102', 'teori', 45),  -- id=2
 ('LAB-1', 'lab', 40),    -- id=3
 ('R-103', 'teori', 50),  -- id=4
 ('R-104', 'teori', 35),  -- id=5
 ('LAB-2', 'lab', 35),    -- id=6
 ('LAB-3', 'lab', 45);    -- id=7

-- Slot waktu
INSERT INTO slot_waktu (hari, waktu_mulai, waktu_selesai) VALUES
 ('Senin', '07:00', '09:00'),
 ('Senin', '09:00', '11:00'),
 ('Senin', '13:00', '15:00'),
 ('Selasa', '07:00', '09:00'),
 ('Selasa', '09:00', '11:00'),
 ('Selasa', '13:00', '15:00'),
 ('Rabu', '07:00', '09:00'),
 ('Rabu', '09:00', '11:00'),
 ('Rabu', '13:00', '15:00');

-- Dosen (kesediaan kosong untuk hindari S2; sesuaikan di produksi)
INSERT INTO dosen (nama, batas_sks, kesediaan, keahlian_matkul_ids) VALUES
 ('Ani',   12, '{}'::jsonb, ARRAY[1,4,11]),
 ('Budi',  12, '{}'::jsonb, ARRAY[2,3,6]),
 ('Citra', 12, '{}'::jsonb, ARRAY[1,3,9,10]),
 ('Dedi',  12, '{}'::jsonb, ARRAY[5,7,8]),
 ('Eka',   12, '{}'::jsonb, ARRAY[6,12]),
 ('Faisal',12, '{}'::jsonb, ARRAY[2,4,5,11]),
 ('Gita',  12, '{}'::jsonb, ARRAY[7,8,10]),
 ('Hasan', 12, '{}'::jsonb, ARRAY[1,2,4,6,12]);
