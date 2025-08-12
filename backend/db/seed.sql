-- Minimal seed sample
TRUNCATE kelas_matkul, dosen, matkul, kelas, ruangan, slot_waktu RESTART IDENTITY CASCADE;

INSERT INTO matkul (nama, sks, jenis_ruangan) VALUES
 ('Algoritma', 3, 'teori'),
 ('Basis Data', 3, 'teori'),
 ('Praktikum Basis Data', 1, 'lab');

INSERT INTO kelas (nama, jumlah_mahasiswa) VALUES
 ('IF-41-01', 32),
 ('IF-41-02', 36);

INSERT INTO kelas_matkul (id_kelas, id_matkul) VALUES
 (1, 1), (1, 2), (1, 3),
 (2, 1), (2, 2), (2, 3);

INSERT INTO ruangan (nama, jenis, kapasitas) VALUES
 ('R-101', 'teori', 40),
 ('R-102', 'teori', 35),
 ('LAB-1', 'lab', 30);

INSERT INTO slot_waktu (hari, waktu_mulai, waktu_selesai) VALUES
 ('Senin', '07:00', '09:00'),
 ('Senin', '09:00', '11:00'),
 ('Selasa', '07:00', '09:00'),
 ('Selasa', '09:00', '11:00');

INSERT INTO dosen (nama, batas_sks, kesediaan, keahlian_matkul_ids) VALUES
 ('Ani', 12, '{"Senin": ["07:00-09:00", "09:00-11:00"], "Selasa": ["07:00-09:00"]}', ARRAY[1,2]),
 ('Budi', 12, '{"Senin": ["09:00-11:00"], "Selasa": ["09:00-11:00"]}', ARRAY[2,3]),
 ('Citra', 12, '{"Senin": ["07:00-09:00"], "Selasa": ["07:00-09:00", "09:00-11:00"]}', ARRAY[1,3]);
