from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class Dosen:
    id: int
    nama: str
    batas_sks: int
    kesediaan: Dict[str, List[str]]  # {"Senin": ["07:00-09:00", ...]}
    keahlian_matkul_ids: List[int]


@dataclass
class Matkul:
    id: int
    nama: str
    sks: int
    jenis_ruangan: str


@dataclass
class Kelas:
    id: int
    nama: str
    jumlah_mahasiswa: int


@dataclass
class KelasMatkul:
    id: int
    id_kelas: int
    id_matkul: int


@dataclass
class Ruangan:
    id: int
    nama: str
    jenis: str
    kapasitas: int


@dataclass
class SlotWaktu:
    id: int
    hari: str
    mulai: str  # HH:MM
    selesai: str  # HH:MM


# Schedule gene for a single task (kelas-matkul)
@dataclass
class Assignment:
    id_kelas: int
    id_matkul: int
    id_dosen: int
    id_ruangan: int
    id_slot: int


@dataclass
class Evaluasi:
    pelanggaran_keras: int
    pelanggaran_lunak: int
    detail_keras: List[str]
    detail_lunak: List[str]
    fitness: float


@dataclass
class DataScheduling:
    dosen: List[Dosen]
    matkul: List[Matkul]
    kelas: List[Kelas]
    kelas_matkul: List[KelasMatkul]
    ruangan: List[Ruangan]
    slot_waktu: List[SlotWaktu]

    def index_by_id(self):
        return {
            "dosen": {d.id: d for d in self.dosen},
            "matkul": {m.id: m for m in self.matkul},
            "kelas": {k.id: k for k in self.kelas},
            "ruangan": {r.id: r for r in self.ruangan},
            "slot": {s.id: s for s in self.slot_waktu},
        }
