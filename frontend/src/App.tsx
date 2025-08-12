import React, { useEffect, useState, useMemo, useRef } from 'react'
import { GAParams, generate, getPresets, GenerateResponse } from './api'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

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
  const tableRef = useRef<HTMLTableElement|null>(null)

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
  const chartData = useMemo(() => {
    if (!result) return undefined
    return {
      labels: result.fitness_history.map((_, i) => i),
      datasets: [{
        label: 'Fitness terbaik',
        data: result.fitness_history,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37,99,235,0.2)'
      }]
    }
  }, [result])

  const makeTimestamp = () => {
    const d = new Date()
    const pad = (n: number) => String(n).padStart(2, '0')
    return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}`
  }

  const exportPDF = () => {
    if (!result) return
    const doc = new jsPDF()
    doc.text('Laporan Jadwal Kuliah (GA + CSP)', 14, 16)
    doc.setFontSize(10)
    doc.text(result.summary, 14, 24)

    // Tabel hasil
    const rows = result.hasil.map(h => [h.id_kelas, h.id_matkul, h.id_dosen, h.id_ruangan, h.id_slot])
    autoTable(doc, {
      startY: 30,
      head: [['Kelas','Matkul','Dosen','Ruangan','Slot']],
      body: rows,
    })

    // Simpan
    doc.save(`jadwal_kuliah_${makeTimestamp()}.pdf`)
  }

  const exportExcel = () => {
    if (!result) return
    const wb = XLSX.utils.book_new()
    const sheetData = [
      ['Summary'],
      [result.summary],
      [],
      ['Kelas','Matkul','Dosen','Ruangan','Slot'],
      ...result.hasil.map(h => [h.id_kelas, h.id_matkul, h.id_dosen, h.id_ruangan, h.id_slot])
    ]
    const ws = XLSX.utils.aoa_to_sheet(sheetData)
    XLSX.utils.book_append_sheet(wb, ws, 'Jadwal')
    const wbout = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
    saveAs(new Blob([wbout], { type: 'application/octet-stream' }), `jadwal_kuliah_${makeTimestamp()}.xlsx`)
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
          <div>Parameter: G={result.params.max_generations}, N={result.params.population_size}, p_m={result.params.mutation_rate}, k={result.params.tournament_size}</div>
          <p style={{marginTop: 8}}><i>{result.fitness_explanation}</i></p>
          <p style={{marginTop: 8}}>{result.summary}</p>

          {chartData && (
            <div style={{maxWidth: 800, marginTop: 8}}>
              <h4>Konvergensi Fitness</h4>
              <Line data={chartData} options={{responsive:true, plugins:{legend:{display:false}, title:{display:false}}}} />
            </div>
          )}

          <details style={{marginTop: 8}}>
            <summary>Detail pelanggaran</summary>
            <ul>
              {result.evaluasi.detail_keras.map((d, i) => <li key={'k'+i}>{d}</li>)}
              {result.evaluasi.detail_lunak.map((d, i) => <li key={'l'+i}>{d}</li>)}
            </ul>
          </details>

          <div style={{display:'flex', gap: 8, marginTop: 12}}>
            <button onClick={exportPDF}>Export PDF</button>
            <button onClick={exportExcel}>Export Excel</button>
          </div>

          <table ref={tableRef} style={{width:'100%', marginTop: 12, borderCollapse:'collapse'}}>
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
              {result.hasil_readable.map((h, i) => (
                <tr key={i}>
                  <td>{h.kelas}</td>
                  <td>{h.matkul}</td>
                  <td>{h.dosen}</td>
                  <td>{h.ruangan}</td>
                  <td>{h.slot}</td>
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
