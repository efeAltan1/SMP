export default function Modal({ open, onClose, title, children }) {
  if (!open) return null
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0,0,0,0.75)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="rounded-xl w-[580px] max-h-[80vh] overflow-y-auto" style={{ backgroundColor: 'var(--smp-surface)', border: '1px solid var(--smp-border)' }}>
        <div className="sticky top-0 flex items-center justify-between px-5 py-4" style={{ backgroundColor: 'var(--smp-surface)', borderBottom: '1px solid var(--smp-border)' }}>
          <span className="text-sm font-semibold text-smp-text">{title}</span>
          <button onClick={onClose} className="text-smp-muted hover:text-smp-text text-lg leading-none">✕</button>
        </div>
        {children}
      </div>
    </div>
  )
}
