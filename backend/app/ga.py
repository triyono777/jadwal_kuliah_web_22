from __future__ import annotations
import random
from typing import List, Tuple, Dict

from .models import Assignment, DataScheduling, Evaluasi


def build_tasks(data: DataScheduling) -> List[Tuple[int, int]]:
    # Each task is (id_kelas, id_matkul) from kelas_matkul
    return [(km.id_kelas, km.id_matkul) for km in data.kelas_matkul]


def feasible_domain(data: DataScheduling) -> Dict[str, Dict[int, List[int]]]:
    # Precompute feasible domains for rooms and lecturers per task
    idx = data.index_by_id()
    matkul_by_id = idx["matkul"]

    # Rooms per matkul
    rooms_for_matkul: Dict[int, List[int]] = {}
    for m in data.matkul:
        rooms_for_matkul[m.id] = [r.id for r in data.ruangan if r.jenis == m.jenis_ruangan]

    # Lecturer by matkul skill
    dosen_for_matkul: Dict[int, List[int]] = {}
    for m in data.matkul:
        allowed = [d.id for d in data.dosen if m.id in (d.keahlian_matkul_ids or [])]
        dosen_for_matkul[m.id] = allowed if allowed else [d.id for d in data.dosen]

    # All slots allowed initially
    slots_for_all = [s.id for s in data.slot_waktu]

    return {
        "rooms_for_matkul": rooms_for_matkul,
        "dosen_for_matkul": dosen_for_matkul,
        "slots": {0: slots_for_all},  # dummy key to reuse quickly
    }


def initialize_population(data: DataScheduling, pop_size: int) -> List[List[Assignment]]:
    tasks = build_tasks(data)
    domain = feasible_domain(data)

    population: List[List[Assignment]] = []
    for _ in range(pop_size):
        individual: List[Assignment] = []
        for (id_kelas, id_matkul) in tasks:
            rooms = domain["rooms_for_matkul"][id_matkul] or [r.id for r in data.ruangan]
            dosen = domain["dosen_for_matkul"][id_matkul] or [d.id for d in data.dosen]
            slot = random.choice(domain["slots"][0])
            individual.append(Assignment(
                id_kelas=id_kelas,
                id_matkul=id_matkul,
                id_dosen=random.choice(dosen),
                id_ruangan=random.choice(rooms),
                id_slot=slot,
            ))
        population.append(individual)
    return population


def evaluate_individual(data: DataScheduling, individual: List[Assignment], w_soft_capacity: int = 1, w_soft_pref: int = 1) -> Evaluasi:
    idx = data.index_by_id()
    slot_conf_room: Dict[Tuple[int, int], int] = {}
    slot_conf_dosen: Dict[Tuple[int, int], int] = {}
    slot_conf_kelas: Dict[Tuple[int, int], int] = {}

    pelanggaran_keras = 0
    detail_keras: List[str] = []

    pelanggaran_lunak = 0
    detail_lunak: List[str] = []

    # Count conflicts
    for a in individual:
        key_room = (a.id_slot, a.id_ruangan)
        key_dosen = (a.id_slot, a.id_dosen)
        key_kelas = (a.id_slot, a.id_kelas)
        slot_conf_room[key_room] = slot_conf_room.get(key_room, 0) + 1
        slot_conf_dosen[key_dosen] = slot_conf_dosen.get(key_dosen, 0) + 1
        slot_conf_kelas[key_kelas] = slot_conf_kelas.get(key_kelas, 0) + 1

    # Hard constraints
    for (slot_id, ruang_id), count in slot_conf_room.items():
        if count > 1:
            pelanggaran_keras += count - 1
            detail_keras.append(f"C1: konflik ruangan slot={slot_id} ruang={ruang_id} x{count}")
    for (slot_id, dosen_id), count in slot_conf_dosen.items():
        if count > 1:
            pelanggaran_keras += count - 1
            detail_keras.append(f"C2: konflik dosen slot={slot_id} dosen={dosen_id} x{count}")
    for (slot_id, kelas_id), count in slot_conf_kelas.items():
        if count > 1:
            pelanggaran_keras += count - 1
            detail_keras.append(f"C3: konflik kelas slot={slot_id} kelas={kelas_id} x{count}")

    # Soft constraints
    for a in individual:
        kelas = idx["kelas"][a.id_kelas]
        ruang = idx["ruangan"][a.id_ruangan]
        if kelas.jumlah_mahasiswa > ruang.kapasitas:
            pelanggaran_lunak += w_soft_capacity
            detail_lunak.append(f"S1: kapasitas kurang kelas={kelas.id} ruang={ruang.id}")
        # Dosen preference
        dosen = idx["dosen"][a.id_dosen]
        slot = idx["slot"][a.id_slot]
        prefer = dosen.kesediaan.get(slot.hari, []) if dosen.kesediaan else []
        time_range = f"{slot.mulai}-{slot.selesai}"
        if prefer and (time_range not in prefer):
            pelanggaran_lunak += w_soft_pref
            detail_lunak.append(f"S2: preferensi tidak cocok dosen={dosen.id} slot={slot.id}")

    fitness = 1000 - (100 * pelanggaran_keras) - (10 * pelanggaran_lunak)
    return Evaluasi(
        pelanggaran_keras=pelanggaran_keras,
        pelanggaran_lunak=pelanggaran_lunak,
        detail_keras=detail_keras,
        detail_lunak=detail_lunak,
        fitness=fitness,
    )


def tournament_selection(population: List[List[Assignment]], fitnesses: List[float], k: int) -> List[Assignment]:
    candidates = random.sample(list(enumerate(population)), k=min(k, len(population)))
    best_idx = max(candidates, key=lambda t: fitnesses[t[0]])[0]
    return population[best_idx]


def one_point_crossover(parent1: List[Assignment], parent2: List[Assignment]) -> Tuple[List[Assignment], List[Assignment]]:
    if len(parent1) <= 1:
        return parent1[:], parent2[:]
    point = random.randint(1, len(parent1) - 1)
    child1 = [Assignment(**vars(g)) for g in (parent1[:point] + parent2[point:])]
    child2 = [Assignment(**vars(g)) for g in (parent2[:point] + parent1[point:])]
    return child1, child2


def mutate(individual: List[Assignment], data: DataScheduling, mutation_rate: float) -> None:
    if mutation_rate <= 0:
        return
    slot_ids = [s.id for s in data.slot_waktu]
    for gene in individual:
        if random.random() < mutation_rate:
            choice = random.choice(["slot", "ruang", "dosen"])
            if choice == "slot":
                gene.id_slot = random.choice(slot_ids)
            elif choice == "ruang":
                # pick room that matches matkul type if possible
                matkul = next(m for m in data.matkul if m.id == gene.id_matkul)
                rooms = [r.id for r in data.ruangan if r.jenis == matkul.jenis_ruangan] or [r.id for r in data.ruangan]
                gene.id_ruangan = random.choice(rooms)
            else:
                allowed = [d.id for d in data.dosen if gene.id_matkul in (d.keahlian_matkul_ids or [])] or [d.id for d in data.dosen]
                gene.id_dosen = random.choice(allowed)


def run_ga(
    data: DataScheduling,
    max_generations: int = 200,
    population_size: int = 60,
    mutation_rate: float = 0.2,
    tournament_size: int = 3,
):
    # Initialize
    population = initialize_population(data, population_size)

    def eval_pop(pop):
        evals = [evaluate_individual(data, ind) for ind in pop]
        return [e.fitness for e in evals], evals

    fitnesses, evals = eval_pop(population)
    best = max(zip(population, evals), key=lambda x: x[1].fitness)
    best_history: List[float] = [best[1].fitness]

    for _ in range(max_generations):
        new_pop: List[List[Assignment]] = []
        while len(new_pop) < population_size:
            p1 = tournament_selection(population, fitnesses, tournament_size)
            p2 = tournament_selection(population, fitnesses, tournament_size)
            c1, c2 = one_point_crossover(p1, p2)
            mutate(c1, data, mutation_rate)
            mutate(c2, data, mutation_rate)
            new_pop.extend([c1, c2])
        population = new_pop[:population_size]
        fitnesses, evals = eval_pop(population)
        cand_best = max(zip(population, evals), key=lambda x: x[1].fitness)
        if cand_best[1].fitness > best[1].fitness:
            best = cand_best
        best_history.append(best[1].fitness)

    best_individual, best_eval = best
    return best_individual, best_eval, best_history
