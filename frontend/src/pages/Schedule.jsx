import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { getSubjects } from '@/api'

const DAY_ORDER = ['PAZARTESİ', 'SALI', 'ÇARŞAMBA', 'PERŞEMBE', 'CUMA', 'CUMARTESİ']

const DAY_LABELS = {
  'PAZARTESİ': 'Pazartesi',
  'SALI': 'Salı',
  'ÇARŞAMBA': 'Çarşamba',
  'PERŞEMBE': 'Perşembe',
  'CUMA': 'Cuma',
  'CUMARTESİ': 'Cumartesi',
}

export default function Schedule() {
  const [subjects, setSubjects] = useState([])

  useEffect(() => {
    getSubjects().then(r => setSubjects(r.data.data)).catch(console.error)
  }, [])

  const byDay = DAY_ORDER.reduce((acc, day) => {
    acc[day] = subjects.filter(s => s.day === day).sort((a, b) =>
      (a.time_start || '').localeCompare(b.time_start || ''))
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Schedule</h1>

      {DAY_ORDER.map(day => (
        byDay[day].length > 0 && (
          <Card key={day}>
            <CardHeader>
              <CardTitle className="text-base">{DAY_LABELS[day]}</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Code</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Room</TableHead>
                    <TableHead>Building</TableHead>
                    <TableHead>Teacher</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {byDay[day].map((s, i) => (
                    <TableRow key={i}>
                      <TableCell className="font-mono whitespace-nowrap">
                        {s.time_start} – {s.time_end}
                      </TableCell>
                      <TableCell className="font-mono">{s.code}</TableCell>
                      <TableCell>{s.name}</TableCell>
                      <TableCell>{s.room}</TableCell>
                      <TableCell>{s.building}</TableCell>
                      <TableCell>{s.teacher}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )
      ))}

      {subjects.length === 0 && (
        <p className="text-sm text-muted-foreground">No schedule data. Run a sync first.</p>
      )}
    </div>
  )
}
