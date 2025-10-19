import { LogOut, Settings } from 'lucide-react'

export default function Header({ user, onLogout }) {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-lg">N</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-800">
          neural<span className="text-blue-600">::</span>foundry
        </h1>
      </div>

      {/* User Menu */}
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-medium text-gray-700">{user.username}</p>
          <p className="text-xs text-gray-500">User ID: {user.id.slice(0, 8)}...</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            className="p-2 hover:bg-gray-100 rounded-lg transition"
            title="Settings"
          >
            <Settings size={20} className="text-gray-600" />
          </button>

          <button
            onClick={onLogout}
            className="p-2 hover:bg-red-50 rounded-lg transition"
            title="Logout"
          >
            <LogOut size={20} className="text-red-600" />
          </button>
        </div>
      </div>
    </header>
  )
}
