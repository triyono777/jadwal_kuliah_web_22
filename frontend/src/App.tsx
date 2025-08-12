import React, { useEffect, useState } from 'react'
import { GAParams, generate, getPresets, GenerateResponse } from './api'

const defaultParams: GAParams = {
  max_generations: 200,
  population_size: 60,
  mutation_rate: 0.2,
  tournament_size: 3,
}

export default function App() {
  const [params, setParams] = useState<GAParams>(defaultParams)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|undefined>()
  const [result, setResult] = useState<GenerateResponse|undefined>()
  const [presets, setPresets] = useState<{G:number,N:number,p_m:number,k:number}[]>([])

  useEffect(() => {
    getPresets().then(setPresets).catch(console.error)
  }, [])

  const onRun = async () => {
    setLoading(true); setError(undefined); setResult(undefined)
    try {
      const res = await generate(params)
      setResult(res)
    } catch (e:any) {
      setError(e.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  const applyPreset = (p: {G:number,N:number,p_m:number,k:number}) => {
    setParams({
      max_generations: p.G,
      population_size: p.N,
      mutation_rate: p.p_m,
      tournament_size: p.k,
    })
  }

  return (
    <div style={{fontFamily: 'Inter, system-ui, Arial', padding: 24, maxWidth: 1100, margin: '0 auto'}}>
      <h1>Optimasi Jadwal Kuliah (CSP + GA)</h1>

      <section style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 12, alignItems: 'end'}}>
        <div>
          <label>Generasi (G)</label>
          <input type="number" value={params.max_generations} min={1} onChange={e => setParams({...params, max_generations: Number(e.target.value)})} />
        </div>
        <div>
          <label>Populasi (N)</label>
          <input type="number" value={params.population_size} min={2} onChange={e => setParams({...params, population_size: Number(e.target.value)})} />
        </div>
        <div>
          <label>Mutation Rate (p_m)</label>
          <input type="number" step="0.01" min={0} max={1} value={params.mutation_rate} onChange={e => setParams({...params, mutation_rate: Number(e.target.value)})} />
        </div>
        <div>
          <label>Tournament Size (k)</label>
          <input type="number" value={params.tournament_size} min={2} onChange={e => setParams({...params, tournament_size: Number(e.target.value)})} />
        </div>
        <div style={{gridColumn: '1 / -1', marginTop: 8}}>
          <button onClick={onRun} disabled={loading}>
            {loading ? 'Menghitung...' : 'Generate Jadwal'}
          </button>
        </div>
      </section>

      <section style={{marginTop: 24}}>
        <h3>Preset</h3>
        <div style={{display:'flex', flexWrap:'wrap', gap: 8}}>
          {presets.map((p, idx) => (
            <button key={idx} onClick={() => applyPreset(p)}>
              G={p.G}, N={p.N}, p_m={p.p_m}, k={p.k}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <div style={{color:'red', marginTop: 16}}>Error: {error}</div>
      )}

      {result && (
        <section style={{marginTop: 24}}>
          <h3>Hasil</h3>
          <div>Fitness: <b>{result.evaluasi.fitness}</b></div>
          <div>Pelanggaran keras: {result.evaluasi.pelanggaran_keras} | lunak: {result.evaluasi.pelanggaran_lunak}</div>

          <details style={{marginTop: 8}}>
            <summary>Detail pelanggaran</summary>
            <ul>
              {result.evaluasi.detail_keras.map((d, i) => <li key={'k'+i}>{d}</li>)}
              {result.evaluasi.detail_lunak.map((d, i) => <li key={'l'+i}>{d}</li>)}
            </ul>
          </details>

          <table style={{width:'100%', marginTop: 12, borderCollapse:'collapse'}}>
            <thead>
              <tr>
                <th style={{borderBottom:'1px solid #ddd', textAlign:'left'}}>Kelas</th>
                <th style={{borderBottom:'1px solid #ddd', textAlign:'left'}}>Matkul</th>
                <th style={{borderBottom:'1px solid #ddd', textAlign:'left'}}>Dosen</th>
                <th style={{borderBottom:'1px solid #ddd', textAlign:'left'}}>Ruangan</th>
                <th style={{borderBottom:'1px solid #ddd', textAlign:'left'}}>Slot</th>
              </tr>
            </thead>
            <tbody>
              {result.hasil.map((h, i) => (
                <tr key={i}>
                  <td>{h.id_kelas}</td>
                  <td>{h.id_matkul}</td>
                  <td>{h.id_dosen}</td>
                  <td>{h.id_ruangan}</td>
                  <td>{h.id_slot}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <footer style={{marginTop: 48, opacity: 0.7}}>
        <small>Pastikan database sudah di-initialize. Lihat README.</small>
      </footer>
    </div>
  )
}
