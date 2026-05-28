import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  sync,
  syncStatus,
  getAnalyticsSummary,
  getUpcomingExams,
  getAnnouncements,
} from '@/api'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [exams, setExams] = useState([])
  const [announcements, setAnnouncements] = useState([])
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState('')
  const [loadError, setLoadError] = useState('')

  const load = async () => {
    setLoadError('')
    // Each call is independent — one failure doesn't block the others
    try {
      const s = await getAnalyticsSummary()
      setSummary(s.data.data)
    } catch (err) {
      setLoadError(prev => prev + ` summary: ${err.message};`)
    }
    try {
      const e = await getUpcomingExams()
      setExams(e.data.data)
    } catch (err) {
      setLoadError(prev => prev + ` exams: ${err.message};`)
    }
    try {
      const a = await getAnnouncements()
      setAnnouncements(a.data.data)
    } catch (err) {
      setLoadError(prev => prev + ` announcements: ${err.message};`)
    }
  }

  useEffect(() => { load() }, [])

  const handleSync = async () => {
    setSyncing(true)
    setSyncMsg('Syncing…')
    try {
      await sync()
      // Poll /sync/status every 3s until the background scrape finishes
      await new Promise((resolve) => {
        const interval = setInterval(async () => {
          try {
            const res = await syncStatus()
            const { status, errors } = res.data
            if (status === 'done') {
              clearInterval(interval)
              setSyncMsg('Sync complete!')
              resolve()
            } else if (status === 'partial') {
              clearInterval(interval)
              setSyncMsg(`Partial sync — errors in: ${Object.keys(errors).join(', ')}`)
              console.error('Sync errors:', errors)
              resolve()
            } else if (status === 'error') {
              clearInterval(interval)
              setSyncMsg(`Sync failed: ${errors.fatal || 'unknown error'}`)
              resolve()
            }
            // still "running" — keep polling
          } catch {
            clearInterval(interval)
            setSyncMsg('Lost connection to backend')
            resolve()
          }
        }, 3000)
      })
      await load()
    } catch (err) {
      setSyncMsg('Sync failed: ' + (err.response?.data?.message || err.message))
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-3">
          {syncMsg && <span className="text-sm text-muted-foreground">{syncMsg}</span>}
          <Button onClick={handleSync} disabled={syncing}>
            {syncing ? 'Syncing…' : 'Sync OBIS'}
          </Button>
        </div>
      </div>

      {loadError && (
        <div className="rounded-md border border-destructive px-4 py-2 text-sm text-destructive">
          Load errors: {loadError}
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">GPA</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{summary?.gpa ?? '—'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Attendance</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {summary?.overall_attendance_rate != null
                ? `${summary.overall_attendance_rate}%`
                : '—'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Subjects</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{summary?.total_subjects ?? '—'}</p>
          </CardContent>
        </Card>
      </div>

      {/* Upcoming exams */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Exams</CardTitle>
        </CardHeader>
        <CardContent>
          {exams.length === 0 ? (
            <p className="text-sm text-muted-foreground">No upcoming exams.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Location</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {exams.map((e, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-mono">{e.code}</TableCell>
                    <TableCell>{e.subject}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{e.type}</Badge>
                    </TableCell>
                    <TableCell>{e.date} {e.hour}</TableCell>
                    <TableCell>{e.location}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Announcements */}
      <Card>
        <CardHeader>
          <CardTitle>Announcements</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {announcements.length === 0 ? (
            <p className="text-sm text-muted-foreground">No announcements.</p>
          ) : (
            announcements.slice(0, 5).map((a, i) => (
              <div key={i} className="border-b pb-3 last:border-0 last:pb-0">
                <p className="font-medium">{a.title}</p>
                <p className="text-sm text-muted-foreground line-clamp-2">{a.content}</p>
                {a.date && <p className="text-xs text-muted-foreground mt-1">{a.date}</p>}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
