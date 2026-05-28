import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import Schedule from '@/pages/Schedule'
import Grades from '@/pages/Grades'
import Attendance from '@/pages/Attendance'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="schedule" element={<Schedule />} />
          <Route path="grades" element={<Grades />} />
          <Route path="attendance" element={<Attendance />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
