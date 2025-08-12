export type GAParams = {
  max_generations: number
  population_size: number
  mutation_rate: number
  tournament_size: number
}

export type AssignmentOut = {
  id_kelas: number
  id_matkul: number
  id_dosen: number
  id_ruangan: number
  id_slot: number
}

export type EvaluateOut = {
  fitness: number
  pelanggaran_keras: number
  pelanggaran_lunak: number
  detail_keras: string[]
  detail_lunak: string[]
}

export type GenerateResponse = {
  params: GAParams
  hasil: AssignmentOut[]
  hasil_readable: {
    id_kelas: number
    kelas: string
    id_matkul: number
    matkul: string
    id_dosen: number
    dosen: string
    id_ruangan: number
    ruangan: string
    id_slot: number
    slot: string
  }[]
  evaluasi: EvaluateOut
  summary: string
  fitness_history: number[]
  fitness_explanation: string
  expected_total: number
  generated_total: number
  schedule_count_ok: boolean
  schedule_count_message: string
}

const API_BASE = 'http://localhost:8000'

export async function getPresets() {
  const res = await fetch(`${API_BASE}/presets`)
  if (!res.ok) throw new Error('Failed to fetch presets')
  return res.json() as Promise<{G:number,N:number,p_m:number,k:number}[]>
}

export async function generate(params: GAParams) {
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<GenerateResponse>
}
