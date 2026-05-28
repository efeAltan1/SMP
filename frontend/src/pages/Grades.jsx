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
import { getGrades, getGPA } from '@/api'

const gradeColor = (letter) => {
  if (!letter) return 'secondary'
  if (['AA', 'BA'].includes(letter)) return 'default'
  if (['BB', 'CB', 'CC'].includes(letter)) return 'secondary'
  return 'destructive'
}

export default function Grades() {
  const [grades, setGrades] = useState([])
  const [gpa, setGpa] = useState(null)

  useEffect(() => {
    getGrades().then(r => setGrades(r.data.data)).catch(console.error)
    getGPA().then(r => setGpa(r.data.data?.gpa)).catch(console.error)
  }, [])

  // Group by semester
  const bySemester = grades.reduce((acc, g) => {
    const s = g.semester || 'Unknown'
    if (!acc[s]) acc[s] = []
    acc[s].push(g)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Grades</h1>
        {gpa != null && (
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Cumulative GPA</p>
            <p className="text-2xl font-bold">{gpa}</p>
          </div>
        )}
      </div>

      {Object.entries(bySemester).map(([semester, rows]) => (
        <Card key={semester}>
          <CardHeader>
            <CardTitle className="text-base">{semester}</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Credits</TableHead>
                  <TableHead>ECTS</TableHead>
                  <TableHead>Midterm</TableHead>
                  <TableHead>Final</TableHead>
                  <TableHead>Grade</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((g, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-mono">{g.code}</TableCell>
                    <TableCell>{g.subject}</TableCell>
                    <TableCell>{g.credits}</TableCell>
                    <TableCell>{g.ects}</TableCell>
                    <TableCell>{g.midterm || '—'}</TableCell>
                    <TableCell>{g.final || '—'}</TableCell>
                    <TableCell>
                      {g.letter_grade ? (
                        <Badge variant={gradeColor(g.letter_grade)}>
                          {g.letter_grade}
                        </Badge>
                      ) : '—'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ))}

      {grades.length === 0 && (
        <p className="text-sm text-muted-foreground">No grade data. Run a sync first.</p>
      )}
    </div>
  )
}
