from __future__ import annotations
import os
import json
from typing import List
from dotenv import load_dotenv
from supabase import create_client, Client

from .models import (
    Dosen, Matkul, Kelas, KelasMatkul, Ruangan, SlotWaktu, DataScheduling
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")


def get_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL or KEY not set. Create backend/.env from .env.example")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_all_data() -> DataScheduling:
    sb = get_client()

    def sel(table: str, select: str = "*"):
        res = sb.table(table).select(select).execute()
        return res.data or []

    dosen_rows = sel("dosen", "id,nama,batas_sks,kesediaan,keahlian_matkul_ids")
    dosen: List[Dosen] = []
    for row in dosen_rows:
        kesediaan = row.get("kesediaan")
        if isinstance(kesediaan, str):
            try:
                kesediaan = json.loads(kesediaan)
            except Exception:
                kesediaan = {}
        dosen.append(Dosen(
            id=row["id"],
            nama=row["nama"],
            batas_sks=row.get("batas_sks", 12),
            kesediaan=kesediaan or {},
            keahlian_matkul_ids=row.get("keahlian_matkul_ids") or [],
        ))

    matkul = [Matkul(**row) for row in sel("matkul", "id,nama,sks,jenis_ruangan")]  # type: ignore[arg-type]
    kelas = [Kelas(**row) for row in sel("kelas", "id,nama,jumlah_mahasiswa")]  # type: ignore[arg-type]
    kelas_matkul = [KelasMatkul(**row) for row in sel("kelas_matkul", "id,id_kelas,id_matkul")]  # type: ignore[arg-type]
    ruangan = [Ruangan(**row) for row in sel("ruangan", "id,nama,jenis,kapasitas")]  # type: ignore[arg-type]
    slot_rows = sel("slot_waktu", "id,hari,waktu_mulai,waktu_selesai")
    slot_waktu = [
        SlotWaktu(
            id=row["id"], hari=row["hari"], mulai=row["waktu_mulai"], selesai=row["waktu_selesai"]
        )
        for row in slot_rows
    ]

    return DataScheduling(
        dosen=dosen,
        matkul=matkul,
        kelas=kelas,
        kelas_matkul=kelas_matkul,
        ruangan=ruangan,
        slot_waktu=slot_waktu,
    )
