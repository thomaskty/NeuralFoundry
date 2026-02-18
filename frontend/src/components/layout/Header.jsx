import { LogOut, Settings } from 'lucide-react'

export default function Header({ user, onLogout }) {
  return (
    <header className="bg-white/70 backdrop-blur border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-gradient-to-br from-indigo-600 via-blue-600 to-sky-500 rounded-xl flex items-center justify-center shadow-md">
          <span className="text-white font-bold text-lg">N</span>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            neural<span className="text-indigo-600">::</span>foundry
          </h1>
          <p className="text-xs text-slate-500">RAG Studio</p>
        </div>
      </div>

      {/* User Menu */}
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-semibold text-slate-800">{user.username}</p>
          <p className="text-xs text-slate-500">User ID: {user.id.slice(0, 8)}...</p>
        </div>

        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-slate-900 text-white flex items-center justify-center text-sm font-semibold">
            {user.username?.slice(0, 2)?.toUpperCase()}
          </div>
          <button
            className="p-2 hover:bg-slate-100 rounded-lg transition"
            title="Settings"
          >
            <Settings size={20} className="text-slate-600" />
          </button>

          <button
            onClick={onLogout}
            className="p-2 hover:bg-rose-50 rounded-lg transition"
            title="Logout"
          >
            <LogOut size={20} className="text-rose-600" />
          </button>
        </div>
      </div>
    </header>
  )
}
