from __future__ import annotations
import os
import json
from typing import List
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from .models import (
    Dosen, Matkul, Kelas, KelasMatkul, Ruangan, SlotWaktu, DataScheduling
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set. Create backend/.env from .env.example")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def fetch_all_data() -> DataScheduling:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nama, batas_sks, kesediaan, keahlian_matkul_ids FROM dosen ORDER BY id")
            dosen_rows = cur.fetchall()
            dosen: List[Dosen] = []
            for row in dosen_rows:
                kesediaan = row["kesediaan"]
                if isinstance(kesediaan, str):
                    try:
                        kesediaan = json.loads(kesediaan)
                    except Exception:
                        kesediaan = {}
                dosen.append(Dosen(
                    id=row["id"],
                    nama=row["nama"],
                    batas_sks=row["batas_sks"],
                    kesediaan=kesediaan or {},
                    keahlian_matkul_ids=row["keahlian_matkul_ids"] or [],
                ))

            cur.execute("SELECT id, nama, sks, jenis_ruangan FROM matkul ORDER BY id")
            matkul = [Matkul(**row) for row in cur.fetchall()]

            cur.execute("SELECT id, nama, jumlah_mahasiswa FROM kelas ORDER BY id")
            kelas = [Kelas(**row) for row in cur.fetchall()]

            cur.execute("SELECT id, id_kelas, id_matkul FROM kelas_matkul ORDER BY id")
            kelas_matkul = [KelasMatkul(**row) for row in cur.fetchall()]

            cur.execute("SELECT id, nama, jenis, kapasitas FROM ruangan ORDER BY id")
            ruangan = [Ruangan(**row) for row in cur.fetchall()]

            cur.execute("SELECT id, hari, waktu_mulai AS mulai, waktu_selesai AS selesai FROM slot_waktu ORDER BY id")
            slot_rows = cur.fetchall()
            slot_waktu = [SlotWaktu(**row) for row in slot_rows]

    return DataScheduling(
        dosen=dosen,
        matkul=matkul,
        kelas=kelas,
        kelas_matkul=kelas_matkul,
        ruangan=ruangan,
        slot_waktu=slot_waktu,
    )
