from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class GAParams(BaseModel):
    max_generations: int = Field(200, ge=1, le=5000)
    population_size: int = Field(60, ge=2, le=5000)
    mutation_rate: float = Field(0.2, ge=0.0, le=1.0)
    tournament_size: int = Field(3, ge=2, le=50)


class AssignmentOut(BaseModel):
    id_kelas: int
    id_matkul: int
    id_dosen: int
    id_ruangan: int
    id_slot: int


class EvaluateOut(BaseModel):
    fitness: float
    pelanggaran_keras: int
    pelanggaran_lunak: int
    detail_keras: List[str]
    detail_lunak: List[str]


class GenerateResponse(BaseModel):
    params: GAParams
    hasil: List[AssignmentOut]
    evaluasi: EvaluateOut


class Preset(BaseModel):
    G: int
    N: int
    p_m: float
    k: int


PRESETS: List[Preset] = [
    Preset(G=200, N=60, p_m=0.20, k=3),
    Preset(G=200, N=100, p_m=0.15, k=3),
    Preset(G=300, N=80, p_m=0.20, k=4),
    Preset(G=500, N=120, p_m=0.10, k=4),
    Preset(G=100, N=60, p_m=0.30, k=3),
    Preset(G=400, N=60, p_m=0.20, k=5),
    Preset(G=300, N=150, p_m=0.15, k=4),
    Preset(G=150, N=40, p_m=0.25, k=2),
    Preset(G=800, N=80, p_m=0.10, k=5),
    Preset(G=250, N=90, p_m=0.20, k=3),
]
