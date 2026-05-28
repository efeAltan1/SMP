import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { getAttendance } from '@/api'

const rateColor = (rate) => {
  if (rate >= 80) return 'default'
  if (rate >= 70) return 'secondary'
  return 'destructive'
}

export default function Attendance() {
  const [records, setRecords] = useState([])

  useEffect(() => {
    getAttendance().then(r => setRecords(r.data.data)).catch(console.error)
  }, [])

  const withRate = records.map(r => {
    const absence = parseFloat(r.theoretical_absence) || 0
    const max = parseFloat(r.theoretical_max) || 0
    const rate = max > 0 ? Math.round((1 - absence / max) * 100) : null
    return { ...r, rate }
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Attendance</h1>

      <Card>
        <CardHeader>
          <CardTitle>This Semester</CardTitle>
        </CardHeader>
        <CardContent>
          {records.length === 0 ? (
            <p className="text-sm text-muted-foreground">No attendance data. Run a sync first.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Absences</TableHead>
                  <TableHead>Max Hours</TableHead>
                  <TableHead>Attendance</TableHead>
                  <TableHead>Grade</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {withRate.map((r, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-mono">{r.code}</TableCell>
                    <TableCell>{r.subject}</TableCell>
                    <TableCell>{r.theoretical_absence}</TableCell>
                    <TableCell>{r.theoretical_max}</TableCell>
                    <TableCell>
                      {r.rate != null ? (
                        <Badge variant={rateColor(r.rate)}>{r.rate}%</Badge>
                      ) : '—'}
                    </TableCell>
                    <TableCell>{r.letter_grade || '—'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
