import { useEffect, useState } from 'react'
import Modal from '@/components/Modal'
import {
  sync, syncStatus,
  getAnalyticsSummary, getUpcomingExams, getExams,
  getAnnouncements, getSubjects, getGrades,
} from '@/api'

// ── Constants ──────────────────────────────────────────────────
const JS_DAY_TO_TURKISH = {
  1: 'PAZARTESİ', 2: 'SALI', 3: 'ÇARŞAMBA',
  4: 'PERŞEMBE',  5: 'CUMA', 6: 'CUMARTESİ',
}
const TURKISH_DAY_DISPLAY = {
  'PAZARTESİ': 'Pazartesi', 'SALI': 'Salı', 'ÇARŞAMBA': 'Çarşamba',
  'PERŞEMBE': 'Perşembe', 'CUMA': 'Cuma', 'CUMARTESİ': 'Cumartesi',
}
const DAY_ORDER = ['PAZARTESİ', 'SALI', 'ÇARŞAMBA', 'PERŞEMBE', 'CUMA', 'CUMARTESİ']
const TURKISH_MONTHS = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
const LETTER_TO_GPA = { AA:4.0, BA:3.5, BB:3.0, CB:2.5, CC:2.0, DC:1.5, DD:1.0, FF:0.0, DZ:0.0, G:4.0 }

// ── Helpers ─────────────────────────────────────────────────────
function calcGPA(gradeList) {
  const graded = gradeList.filter(g => g.letter_grade in LETTER_TO_GPA)
  const pts = graded.reduce((s, g) => s + LETTER_TO_GPA[g.letter_grade] * (parseFloat(g.credits) || 0), 0)
  const cred = graded.reduce((s, g) => s + (parseFloat(g.credits) || 0), 0)
  return cred > 0 ? (pts / cred).toFixed(2) : null
}

function gradeBadgeClass(letter) {
  if (!letter) return 'bg-smp-surface2 text-smp-muted'
  if (['AA', 'BA'].includes(letter)) return 'bg-[#052e16] text-smp-green'
  if (['BB', 'CB', 'CC'].includes(letter)) return 'bg-[#2d1f00] text-smp-yellow'
  return 'bg-[#2d0a0a] text-smp-red'
}

function todayString() {
  const d = new Date()
  return `${d.getDate()} ${TURKISH_MONTHS[d.getMonth()]} ${d.getFullYear()}`
}

// ── Sub-components ──────────────────────────────────────────────
function SectionCard({ title, onExpand, children }) {
  return (
    <div className="bg-smp-surface border border-smp-border rounded-xl overflow-hidden">
      <div
        onClick={onExpand}
        className="flex items-center justify-between px-5 py-3.5 border-b border-smp-border cursor-pointer hover:bg-smp-surface2 group"
      >
        <span className="text-[11px] font-bold uppercase tracking-widest text-smp-muted">{title}</span>
        <span className="text-[11px] text-smp-accent opacity-40 group-hover:opacity-100 transition-opacity">↗</span>
      </div>
      {children}
    </div>
  )
}

function Row({ left, right }) {
  return (
    <div className="flex items-center justify-between px-5 py-3 border-t border-smp-border first:border-t-0 hover:bg-smp-surface2">
      <div className="flex flex-col gap-0.5">
        {left}
      </div>
      {right && <div className="text-right ml-4 shrink-0">{right}</div>}
    </div>
  )
}

// ── Main component ──────────────────────────────────────────────
export default function Dashboard() {
  const [summary, setSummary]           = useState(null)
  const [upcomingExams, setUpcomingExams] = useState([])
  const [allExams, setAllExams]         = useState([])
  const [announcements, setAnnouncements] = useState([])
  const [subjects, setSubjects]         = useState([])
  const [grades, setGrades]             = useState([])
  const [syncing, setSyncing]           = useState(false)
  const [syncMsg, setSyncMsg]           = useState('')
  const [modal, setModal]               = useState(null)

  const todayKey = JS_DAY_TO_TURKISH[new Date().getDay()] || null
  const todayDisplay = todayKey ? TURKISH_DAY_DISPLAY[todayKey] : null

  // Current semester = last alphabetically (most recent)
  const semesters = [...new Set(grades.map(g => g.semester))].sort()
  const currentSemester = semesters[semesters.length - 1]
  const currentGrades = grades.filter(g => g.semester === currentSemester)

  // Today's lessons sorted by start time
  const todayLessons = subjects
    .filter(s => s.day === todayKey)
    .sort((a, b) => (a.time_start || '').localeCompare(b.time_start || ''))

  const load = async () => {
    try { const r = await getAnalyticsSummary(); setSummary(r.data.data) } catch {}
    try { const r = await getUpcomingExams();    setUpcomingExams(r.data.data) } catch {}
    try { const r = await getExams();            setAllExams(r.data.data) } catch {}
    try { const r = await getAnnouncements();    setAnnouncements(r.data.data) } catch {}
    try { const r = await getSubjects();         setSubjects(r.data.data) } catch {}
    try { const r = await getGrades();           setGrades(r.data.data) } catch {}
  }

  useEffect(() => { load() }, [])

  const handleSync = async () => {
    setSyncing(true)
    setSyncMsg('Syncing…')
    try {
      await sync()
      await new Promise(resolve => {
        const iv = setInterval(async () => {
          try {
            const r = await syncStatus()
            const { status, errors } = r.data
            if (status === 'done') {
              clearInterval(iv); setSyncMsg('Sync complete!'); resolve()
            } else if (status === 'partial') {
              clearInterval(iv)
              setSyncMsg(`Partial — errors in: ${Object.keys(errors).join(', ')}`)
              resolve()
            } else if (status === 'error') {
              clearInterval(iv); setSyncMsg(`Error: ${errors.fatal || 'unknown'}`); resolve()
            }
          } catch { clearInterval(iv); setSyncMsg('Connection lost'); resolve() }
        }, 3000)
      })
      await load()
    } catch (e) {
      setSyncMsg('Failed: ' + (e.response?.data?.message || e.message))
    } finally { setSyncing(false) }
  }

  // ── Modal content builders ──────────────────────────────────
  const renderGPAModal = () => {
    const byS = semesters.map(sem => ({
      sem,
      gpa: calcGPA(grades.filter(g => g.semester === sem))
    })).reverse()
    return (
      <>
        {byS.map(({ sem, gpa }) => (
          <div key={sem} className="flex items-center justify-between px-5 py-3.5 border-t border-smp-border first:border-t-0 hover:bg-smp-surface2">
            <span className="text-sm text-smp-text">{sem}</span>
            <span className="text-sm font-bold text-smp-text">{gpa ?? '—'}</span>
          </div>
        ))}
        {semesters.length === 0 && <p className="px-5 py-4 text-sm text-smp-muted">No grade history.</p>}
      </>
    )
  }

  const renderExamsModal = () => (
    <>
      {allExams.map((e, i) => (
        <div key={i} className="flex items-center justify-between px-5 py-3.5 border-t border-smp-border first:border-t-0 hover:bg-smp-surface2">
          <div>
            <div className="text-[11px] font-mono text-smp-muted">{e.code}</div>
            <div className="text-sm text-smp-text">{e.subject}</div>
          </div>
          <div className="text-right">
            <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-smp-accent-dim text-[#a5b4fc]`}>{e.type}</span>
            <div className="text-xs text-smp-muted mt-1">{e.date} {e.hour}</div>
          </div>
        </div>
      ))}
      {allExams.length === 0 && <p className="px-5 py-4 text-sm text-smp-muted">No exams.</p>}
    </>
  )

  const renderAnnouncementsModal = () => (
    <>
      {announcements.map((a, i) => (
        <div key={i} className="px-5 py-3.5 border-t border-smp-border first:border-t-0 hover:bg-smp-surface2">
          <div className="text-sm font-medium text-smp-text">{a.title}</div>
          <div className="text-xs text-smp-muted mt-0.5">{a.content}</div>
        </div>
      ))}
      {announcements.length === 0 && <p className="px-5 py-4 text-sm text-smp-muted">No announcements.</p>}
    </>
  )

  const renderScheduleModal = () => (
    <>
      {DAY_ORDER.map(day => {
        const lessons = subjects.filter(s => s.day === day).sort((a, b) => (a.time_start||'').localeCompare(b.time_start||''))
        if (!lessons.length) return null
        return (
          <div key={day}>
            <div className="px-5 py-2 text-[11px] font-bold uppercase tracking-wider text-smp-accent bg-smp-surface2">
              {TURKISH_DAY_DISPLAY[day]}
            </div>
            {lessons.map((s, i) => (
              <div key={i} className="flex items-center gap-4 px-5 py-3 border-t border-smp-border hover:bg-smp-surface2">
                <span className="font-mono text-[11px] text-smp-accent min-w-[100px]">{s.time_start} – {s.time_end}</span>
                <div>
                  <div className="text-sm text-smp-text">{s.name}</div>
                  <div className="text-xs text-smp-muted">{s.building} · {s.room}</div>
                </div>
              </div>
            ))}
          </div>
        )
      })}
      {subjects.length === 0 && <p className="px-5 py-4 text-sm text-smp-muted">No schedule data.</p>}
    </>
  )

  const renderGradesModal = () => (
    <>
      {currentGrades.map((g, i) => (
        <div key={i} className="flex items-center justify-between px-5 py-3.5 border-t border-smp-border first:border-t-0 hover:bg-smp-surface2">
          <div>
            <div className="text-[11px] font-mono text-smp-muted">{g.code}</div>
            <div className="text-sm text-smp-text">{g.subject}</div>
            <div className="text-xs text-smp-muted mt-0.5">
              Midterm: {g.midterm || '—'} · Final: {g.final || '—'} · ECTS: {g.ects}
            </div>
          </div>
          <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${gradeBadgeClass(g.letter_grade)}`}>
            {g.letter_grade || '—'}
          </span>
        </div>
      ))}
      {currentGrades.length === 0 && <p className="px-5 py-4 text-sm text-smp-muted">No grade data.</p>}
    </>
  )

  // ── Render ──────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-smp-bg text-smp-text font-sans">

      {/* Top bar */}
      <div className="flex items-center justify-between px-8 py-5 bg-smp-surface border-b border-smp-border">
        <span className="text-base font-bold tracking-tight">
          SM<span className="text-smp-accent">P</span>
        </span>
        <span className="text-sm font-medium text-smp-muted">Overview</span>
        <div className="flex items-center gap-3">
          {syncMsg && <span className="text-xs text-smp-muted">{syncMsg}</span>}
          <button
            onClick={handleSync}
            disabled={syncing}
            className="bg-smp-accent hover:bg-[#4f52d4] disabled:opacity-50 text-white text-xs font-semibold px-4 py-2 rounded-md transition-colors"
          >
            {syncing ? 'Syncing…' : '↻  Sync OBIS'}
          </button>
        </div>
      </div>

      <div className="px-8 py-7 flex flex-col gap-5">

        {/* GPA — centered, clickable */}
        <div
          className="flex items-baseline justify-center gap-2.5 cursor-pointer group py-2"
          onClick={() => setModal('gpa')}
        >
          <span className="text-[11px] font-bold uppercase tracking-widest text-smp-muted group-hover:text-smp-accent transition-colors">GPA</span>
          <span className="text-4xl font-bold tracking-tight">{summary?.gpa ?? '—'}</span>
          <span className="text-[11px] text-smp-muted opacity-0 group-hover:opacity-100 transition-opacity">↗</span>
        </div>

        {/* Three columns */}
        <div className="grid grid-cols-3 gap-4">

          {/* Upcoming Exams */}
          <SectionCard title="Upcoming Exams" onExpand={() => setModal('exams')}>
            {upcomingExams.slice(0, 4).map((e, i) => (
              <Row key={i}
                left={<>
                  <span className="text-[11px] font-mono text-smp-muted">{e.code}</span>
                  <span className="text-sm text-smp-text">{e.subject}</span>
                </>}
                right={<>
                  <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-smp-accent-dim text-[#a5b4fc]`}>{e.type}</span>
                  <div className="text-xs text-smp-muted mt-1">{e.date}</div>
                </>}
              />
            ))}
            {upcomingExams.length === 0 && (
              <p className="px-5 py-4 text-sm text-smp-muted">No upcoming exams.</p>
            )}
          </SectionCard>

          {/* Announcements */}
          <SectionCard title="Announcements" onExpand={() => setModal('announcements')}>
            {announcements.slice(0, 5).map((a, i) => (
              <Row key={i}
                left={<>
                  <span className="text-sm text-smp-text">{a.title}</span>
                  <span className="text-xs text-smp-muted">{a.content}</span>
                </>}
              />
            ))}
            {announcements.length === 0 && (
              <p className="px-5 py-4 text-sm text-smp-muted">No announcements.</p>
            )}
          </SectionCard>

          {/* Lesson Today */}
          <SectionCard title="Lesson Today" onExpand={() => setModal('schedule')}>
            {todayKey ? (
              <>
                <div className="px-5 pt-3 pb-1 text-[11px] font-semibold text-smp-accent">
                  {todayDisplay} — {todayString()}
                </div>
                {todayLessons.length > 0 ? todayLessons.map((s, i) => (
                  <Row key={i}
                    left={<>
                      <span className="text-sm text-smp-text">{s.name}</span>
                      <span className="text-xs text-smp-muted">{s.building} · {s.room}</span>
                    </>}
                    right={
                      <span className="font-mono text-[11px] text-smp-accent">{s.time_start}<br/>{s.time_end}</span>
                    }
                  />
                )) : (
                  <p className="px-5 py-4 text-sm text-smp-muted">No classes today.</p>
                )}
              </>
            ) : (
              <p className="px-5 py-4 text-sm text-smp-muted">No classes on weekends.</p>
            )}
          </SectionCard>

        </div>

        {/* Grades — full width */}
        <SectionCard title={`Grades${currentSemester ? ` · ${currentSemester}` : ''}`} onExpand={() => setModal('grades')}>
          {currentGrades.length > 0 ? (
            <div className="grid" style={{ gridTemplateColumns: `repeat(${currentGrades.length}, 1fr)` }}>
              {currentGrades.map((g, i) => (
                <div key={i} className={`px-5 py-4 ${i > 0 ? 'border-l border-smp-border' : ''}`}>
                  <div className="text-[11px] font-mono text-smp-muted mb-0.5">{g.code}</div>
                  <div className="text-sm text-smp-text mb-3 leading-tight">{g.subject}</div>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-smp-muted">Midterm</span>
                    <span className="text-smp-text font-medium">{g.midterm || '—'}</span>
                  </div>
                  <div className="flex justify-between text-xs mb-3">
                    <span className="text-smp-muted">Final</span>
                    <span className="text-smp-text font-medium">{g.final || '—'}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-smp-muted">Grade</span>
                    <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${gradeBadgeClass(g.letter_grade)}`}>
                      {g.letter_grade || '—'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="px-5 py-4 text-sm text-smp-muted">No grade data. Run a sync first.</p>
          )}
        </SectionCard>

      </div>

      {/* Modals */}
      <Modal open={modal === 'gpa'} onClose={() => setModal(null)} title="GPA History">
        {renderGPAModal()}
      </Modal>
      <Modal open={modal === 'exams'} onClose={() => setModal(null)} title="All Exams">
        {renderExamsModal()}
      </Modal>
      <Modal open={modal === 'announcements'} onClose={() => setModal(null)} title="All Announcements">
        {renderAnnouncementsModal()}
      </Modal>
      <Modal open={modal === 'schedule'} onClose={() => setModal(null)} title="Full Schedule">
        {renderScheduleModal()}
      </Modal>
      <Modal open={modal === 'grades'} onClose={() => setModal(null)} title={`Grades — ${currentSemester || 'Current Semester'}`}>
        {renderGradesModal()}
      </Modal>

    </div>
  )
}
