from __future__ import annotations
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .db import fetch_all_data
from .ga import run_ga
from .models import Assignment
from .schemas import GAParams, AssignmentOut, AssignmentReadableOut, EvaluateOut, GenerateResponse, PRESETS

load_dotenv()

app = FastAPI(title="Jadwal Kuliah GA+CSP API")

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/presets")
def presets():
    return [p.model_dump() for p in PRESETS]


@app.post("/generate", response_model=GenerateResponse)
def generate(params: GAParams):
    try:
        data = fetch_all_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    best_individual, best_eval, history = run_ga(
        data=data,
        max_generations=params.max_generations,
        population_size=params.population_size,
        mutation_rate=params.mutation_rate,
        tournament_size=params.tournament_size,
    )

    hasil: List[AssignmentOut] = [AssignmentOut(**vars(a)) for a in best_individual]
    idx = data.index_by_id()
    hasil_readable: List[AssignmentReadableOut] = []
    for a in best_individual:
        kelas = idx["kelas"][a.id_kelas]
        matkul = idx["matkul"][a.id_matkul]
        dosen = idx["dosen"][a.id_dosen]
        ruangan = idx["ruangan"][a.id_ruangan]
        slot = idx["slot"][a.id_slot]
        hasil_readable.append(AssignmentReadableOut(
            id_kelas=kelas.id,
            kelas=kelas.nama,
            id_matkul=matkul.id,
            matkul=matkul.nama,
            id_dosen=dosen.id,
            dosen=dosen.nama,
            id_ruangan=ruangan.id,
            ruangan=ruangan.nama,
            id_slot=slot.id,
            slot=f"{slot.hari} {slot.mulai}-{slot.selesai}",
        ))
    evaluasi = EvaluateOut(
        fitness=best_eval.fitness,
        pelanggaran_keras=best_eval.pelanggaran_keras,
        pelanggaran_lunak=best_eval.pelanggaran_lunak,
        detail_keras=best_eval.detail_keras,
        detail_lunak=best_eval.detail_lunak,
        detail_keras_readable=best_eval.detail_keras,
        detail_lunak_readable=best_eval.detail_lunak,
    )

    summary = (
        f"Fitness terbaik: {best_eval.fitness}. "
        f"Pelanggaran keras: {best_eval.pelanggaran_keras}, lunak: {best_eval.pelanggaran_lunak}. "
        f"Parameter: G={params.max_generations}, N={params.population_size}, p_m={params.mutation_rate}, k={params.tournament_size}."
    )

    fitness_explanation = (
        "Fitness lebih tinggi lebih baik. Dihitung sebagai 1000 - 100×(pelanggaran keras) - 10×(pelanggaran lunak). "
        "Pelanggaran keras: konflik ruangan/dosen/kelas pada slot yang sama. "
        "Pelanggaran lunak: kapasitas ruang kurang dan ketidaksesuaian preferensi waktu dosen."
    )

    expected_total = len(data.kelas_matkul)
    generated_total = len(hasil)
    schedule_count_ok = (generated_total == expected_total)
    schedule_count_message = (
        f"Total jadwal seharusnya {expected_total}, tergenerate {generated_total}. "
        + ("Sesuai." if schedule_count_ok else "Tidak sesuai, periksa integritas data/algoritma.")
    )

    return GenerateResponse(
        params=params,
        hasil=hasil,
        hasil_readable=hasil_readable,
        evaluasi=evaluasi,
        summary=summary,
        fitness_history=history,
        fitness_explanation=fitness_explanation,
        expected_total=expected_total,
        generated_total=generated_total,
        schedule_count_ok=schedule_count_ok,
        schedule_count_message=schedule_count_message,
    )


# Run with: uvicorn app.main:app --reload --port 8000
