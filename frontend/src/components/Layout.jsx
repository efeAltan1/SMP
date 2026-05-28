import { NavLink, Outlet } from 'react-router-dom'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/schedule', label: 'Schedule' },
  { to: '/grades', label: 'Grades' },
  { to: '/attendance', label: 'Attendance' },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-48 shrink-0 border-r bg-sidebar text-sidebar-foreground flex flex-col py-6 px-4 gap-1">
        <p className="text-lg font-bold mb-6 px-2">SMP</p>
        {links.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'rounded-md px-2 py-1.5 text-sm transition-colors',
                isActive
                  ? 'bg-sidebar-primary text-sidebar-primary-foreground font-medium'
                  : 'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
              )
            }
          >
            {label}
          </NavLink>
        ))}
      </aside>

      {/* Main */}
      <main className="flex-1 p-8 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
