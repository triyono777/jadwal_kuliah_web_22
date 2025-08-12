## Alur Tesis: Optimasi Penjadwalan Mata Kuliah dengan CSP + Algoritma Genetika

Dokumen ini menjelaskan alur lengkap dari pengumpulan data hingga hasil akhir, termasuk formulasi matematis utama.

### 1. Sumber dan Akuisisi Data
- **Tabel `dosen`**: nama, batas SKS, kesediaan mengajar (hari-jam), keahlian mata kuliah.
- **Tabel `matkul`**: nama, SKS, jenis ruangan.
- **Tabel `kelas`**: nama kelas, jumlah mahasiswa.
- **Tabel `kelas_matkul`**: relasi kelas ↔ mata kuliah yang diambil.
- **Tabel `ruangan`**: nama, jenis, kapasitas.
- **Tabel `slot_waktu`**: hari, waktu mulai, waktu selesai.

Data dimasukkan ke Supabase dan disiapkan dengan `schema.sql` + `seed.sql` untuk keperluan pengujian.

### 2. Pembersihan (Data Cleaning)
- Validasi domain nilai: kapasitas ruangan > 0, jumlah mahasiswa > 0, SKS ∈ {1,2,3,4}.
- Normalisasi teks: trim nama, konsistensi kapitalisasi jenis ruangan.
- Verifikasi konsistensi relasi: setiap `kelas_matkul.id_matkul` harus ada di `matkul`, dan `id_kelas` di `kelas`.
- Validasi ketersediaan dosen: format JSON kesediaan sesuai `{hari: ["HH:MM-HH:MM", ...]}`.
- Deteksi outlier: jumlah mahasiswa > kapasitas maksimum ruangan yang tersedia (beri peringatan).

### 3. Pemodelan Masalah (Formulasi CSP)
Kita bentuk himpunan tugas penjadwalan:
- Variabel keputusan per tugas t ∈ T: penentuan `(ruangan, slot_waktu, dosen)`.
- Domain:
  - Ruangan: sesuai jenis `jenis_ruangan(t)` dan kapasitas `kapasitas(ruang) ≥ jumlah_mahasiswa(kelas)`.
  - Slot waktu: salah satu slot pada `slot_waktu`.
  - Dosen: dosen yang memiliki `keahlian` relevan dengan `mata_kuliah(t)`.

#### Hard Constraints (keras)
- C1. Tidak ada dua perkuliahan menggunakan ruangan yang sama pada slot yang sama.
- C2. Seorang dosen tidak mengajar dua perkuliahan pada slot yang sama.
- C3. Satu kelas tidak boleh memiliki lebih dari satu mata kuliah pada slot yang sama.

Secara formal, untuk setiap slot s dan ruangan r:
- [C1] ∑_{t ∈ T} I[(t.slot=s) ∧ (t.ruang=r)] ≤ 1
- [C2] Untuk setiap dosen d: ∑_{t ∈ T} I[(t.slot=s) ∧ (t.dosen=d)] ≤ 1
- [C3] Untuk setiap kelas k: ∑_{t ∈ T} I[(t.slot=s) ∧ (t.kelas=k)] ≤ 1

#### Soft Constraints (lunak)
- S1. Kapasitas ruangan ≥ jumlah mahasiswa kelas (pelanggaran → penalti).
- S2. Preferensi waktu dosen dipenuhi (pelanggaran → penalti).

Penalti lunak berupa bobot w_S1 dan w_S2.

### 4. Fungsi Objektif (Fitness)
Maksimasi fungsi fitness:

- Fitness = C − (100 × V_hard) − (10 × V_soft)
- Dengan:
  - V_hard = jumlah pelanggaran hard (C1, C2).
  - V_soft = jumlah penalti soft berbobot (S1, S2).
  - C adalah konstanta skala (misal 1000) untuk memudahkan interpretasi.

### 5. Algoritma Genetika (GA)
- Inisialisasi populasi: sampling acak domain yang sudah dipersempit oleh CSP (room jenis cocok, kapasitas minimal, dosen berkeahlian).
- Evaluasi: hitung pelanggaran hard/soft → fitness.
- Seleksi: tournament selection ukuran k.
- Crossover: 1-cut crossover pada daftar tugas.
- Mutasi: mutasi salah satu komponen (slot/ruangan/dosen) dengan probabilitas p.
- Terminasi: generasi maksimum G atau konvergensi.

#### Parameter Uji Coba
Daftar parameter yang digunakan untuk eksperimen beserta nilai awal dan rekomendasi rentangnya:

- **G (max_generations)**
  - **Default**: 200
  - **Deskripsi**: Batas jumlah generasi evolusi GA.
  - **Anjuran uji**: 100–1000 (bertambah meningkatkan kualitas namun menambah waktu komputasi).

- **N (population_size)**
  - **Default**: 60
  - **Deskripsi**: Ukuran populasi per generasi.
  - **Anjuran uji**: 30–200 (lebih besar memperkaya keragaman namun lebih lambat).

- **p_m (mutation_rate)**
  - **Default**: 0.2
  - **Deskripsi**: Probabilitas mutasi per gen (slot/ruangan/dosen) pada tiap individu.
  - **Anjuran uji**: 0.05–0.4 (terlalu kecil mudah stagnan; terlalu besar sulit konvergen).

- **k (tournament_size)**
  - **Default**: 3
  - **Deskripsi**: Jumlah kontestan pada tournament selection (tekanan seleksi).
  - **Anjuran uji**: 2–7 (lebih besar mempercepat seleksi namun berisiko premature convergence).

Catatan: seluruh parameter di atas dapat diubah dari UI frontend sebelum proses generate/ekspor.

#### Pasangan Parameter Uji (Preset)
Gunakan kombinasi berikut untuk eksperimen terstruktur. Notasi: (G=N generasi, N=populasi, p_m=mutation rate, k=tournament size)

| G | N  | p_m | k |
|---|----|-----|---|
| 200 | 60  | 0.20 | 3 |  
| 200 | 100 | 0.15 | 3 |  
| 300 | 80  | 0.20 | 4 |  
| 500 | 120 | 0.10 | 4 |  
| 100 | 60  | 0.30 | 3 |  
| 400 | 60  | 0.20 | 5 |  
| 300 | 150 | 0.15 | 4 |  
| 150 | 40  | 0.25 | 2 |  
| 800 | 80  | 0.10 | 5 |  
| 250 | 90  | 0.20 | 3 |

### 6. Alur Komputasi Sistem
1) Backend mengambil data dari Supabase.
2) Bentuk `tasks` (CSP) dari tabel normalized.
3) GA menghasilkan populasi awal, lalu iterasi seleksi-crossover-mutasi.
4) Evaluasi tiap individu dengan menghitung hard dan soft constraints.
5) Pilih individu terbaik sebagai jadwal akhir.
6) Kembalikan hasil ke frontend termasuk detail pelanggaran.

### 7. Evaluasi Manual (Contoh Perhitungan)
Misal terdapat dua assignment A dan B pada slot yang sama s dan ruangan yang sama r:
- Pelanggaran C1 bertambah 1 (V_hard += 1).

Jika dosen D mengajar A dan B pada slot yang sama s:
- Pelanggaran C2 bertambah 1 (V_hard += 1).

Jika `jumlah_mahasiswa=36` dan `kapasitas=32`:
- Pelanggaran S1 → penalti +3 (contoh bobot).

Jika preferensi dosen tidak memuat (hari=Senin, jam=07:00-09:00):
- Pelanggaran S2 → penalti +1.

Sehingga untuk sebuah individu:
- V_hard = 2, V_soft = 4 → Fitness = 1000 − (2×100) − (4×10) = 1000 − 200 − 40 = 760.

### 8. Keluaran Sistem
- Jadwal terbaik (kelas, matkul, dosen, ruangan, hari, jam).
- Nilai fitness.
- Rincian pelanggaran: jumlah dan pesan untuk hard/soft.

### 9. Pengembangan Lanjutan
- Tambah hard constraint: konflik kelas (satu kelas tidak boleh punya dua matkul pada slot yang sama).
- Tambah soft constraint: sebaran waktu dosen/kelas, minimal jarak antar kuliah, preferensi hari.
- Penalaan bobot penalti dan parameter GA (ukuran populasi, laju mutasi).
