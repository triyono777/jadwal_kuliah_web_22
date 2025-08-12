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
    kelas_by_id = {k.id: k for k in data.kelas}
    for m in data.matkul:
        # room filter by type only; capacity will be validated per assignment using kelas size
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
        used_room_slot: Dict[Tuple[int, int], bool] = {}
        used_dosen_slot: Dict[Tuple[int, int], bool] = {}
        used_kelas_slot: Dict[Tuple[int, int], bool] = {}
        for (id_kelas, id_matkul) in tasks:
            kelas = next(k for k in data.kelas if k.id == id_kelas)
            # candidate rooms: correct type and capacity >= class size
            room_candidates = [r.id for r in data.ruangan if r.jenis == next(m for m in data.matkul if m.id==id_matkul).jenis_ruangan and r.kapasitas >= kelas.jumlah_mahasiswa]
            if not room_candidates:
                room_candidates = domain["rooms_for_matkul"][id_matkul] or [r.id for r in data.ruangan]
            dosen_candidates = domain["dosen_for_matkul"][id_matkul] or [d.id for d in data.dosen]
            slot_candidates = domain["slots"][0][:]

            # try to find non-conflicting assignment
            random.shuffle(slot_candidates)
            random.shuffle(room_candidates)
            random.shuffle(dosen_candidates)
            chosen = None
            for s in slot_candidates:
                # avoid class conflict first
                if used_kelas_slot.get((s, id_kelas)):
                    continue
                # pick a room not used at this slot
                room = next((rid for rid in room_candidates if not used_room_slot.get((s, rid))), None)
                if room is None:
                    continue
                # pick a dosen not used at this slot
                dos = next((did for did in dosen_candidates if not used_dosen_slot.get((s, did))), None)
                if dos is None:
                    continue
                chosen = (s, room, dos)
                break
            if chosen is None:
                # fallback: random
                s = random.choice(domain["slots"][0])
                room = random.choice(room_candidates)
                dos = random.choice(dosen_candidates)
            else:
                s, room, dos = chosen

            used_kelas_slot[(s, id_kelas)] = True
            used_room_slot[(s, room)] = True
            used_dosen_slot[(s, dos)] = True
            individual.append(Assignment(
                id_kelas=id_kelas,
                id_matkul=id_matkul,
                id_dosen=dos,
                id_ruangan=room,
                id_slot=s,
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
    idx_by = data.index_by_id()
    for (slot_id, ruang_id), count in slot_conf_room.items():
        if count > 1:
            pelanggaran_keras += count - 1
            slot = idx_by["slot"][slot_id]
            ruang = idx_by["ruangan"][ruang_id]
            detail_keras.append(f"C1: Konflik ruangan {ruang.nama} pada {slot.hari} {slot.mulai}-{slot.selesai} (x{count})")
    for (slot_id, dosen_id), count in slot_conf_dosen.items():
        if count > 1:
            pelanggaran_keras += count - 1
            slot = idx_by["slot"][slot_id]
            dosen = idx_by["dosen"][dosen_id]
            detail_keras.append(f"C2: Konflik dosen {dosen.nama} pada {slot.hari} {slot.mulai}-{slot.selesai} (x{count})")
    for (slot_id, kelas_id), count in slot_conf_kelas.items():
        if count > 1:
            pelanggaran_keras += count - 1
            slot = idx_by["slot"][slot_id]
            kelas = idx_by["kelas"][kelas_id]
            detail_keras.append(f"C3: Konflik kelas {kelas.nama} pada {slot.hari} {slot.mulai}-{slot.selesai} (x{count})")

    # Soft constraints
    for a in individual:
        kelas = idx["kelas"][a.id_kelas]
        ruang = idx["ruangan"][a.id_ruangan]
        if kelas.jumlah_mahasiswa > ruang.kapasitas:
            pelanggaran_lunak += w_soft_capacity
            detail_lunak.append(f"S1: Kapasitas kurang kelas {kelas.nama} ({kelas.jumlah_mahasiswa}) di ruang {ruang.nama} (kap {ruang.kapasitas})")
        # Dosen preference
        dosen = idx["dosen"][a.id_dosen]
        slot = idx["slot"][a.id_slot]
        prefer = dosen.kesediaan.get(slot.hari, []) if dosen.kesediaan else []
        time_range = f"{slot.mulai}-{slot.selesai}"
        if prefer and (time_range not in prefer):
            pelanggaran_lunak += w_soft_pref
            detail_lunak.append(f"S2: Preferensi tidak cocok dosen {dosen.nama} pada {slot.hari} {time_range}")

    fitness = 1000 - (100 * pelanggaran_keras) - (10 * pelanggaran_lunak)
    return Evaluasi(
        pelanggaran_keras=pelanggaran_keras,
        pelanggaran_lunak=pelanggaran_lunak,
        detail_keras=detail_keras,
        detail_lunak=detail_lunak,
        detail_keras_readable=detail_keras[:],
        detail_lunak_readable=detail_lunak[:],
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
                # pick room that matches matkul type and capacity if possible
                matkul = next(m for m in data.matkul if m.id == gene.id_matkul)
                kelas = next(k for k in data.kelas if k.id == gene.id_kelas)
                rooms = [r.id for r in data.ruangan if r.jenis == matkul.jenis_ruangan and r.kapasitas >= kelas.jumlah_mahasiswa] or [r.id for r in data.ruangan if r.jenis == matkul.jenis_ruangan] or [r.id for r in data.ruangan]
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

    elitism_count = max(1, population_size // 10)
    for _ in range(max_generations):
        new_pop: List[List[Assignment]] = []
        # Elitism: carry over top-k
        elite_indices = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)[:elitism_count]
        for ei in elite_indices:
            new_pop.append([Assignment(**vars(g)) for g in population[ei]])
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
