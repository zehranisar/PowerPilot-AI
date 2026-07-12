import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useState, useEffect } from 'react'
import api from '../services/api'
import { 
  LayoutDashboard, 
  TrendingUp, 
  MessageSquare, 
  LogOut,
  Zap,
  History
} from 'lucide-react'

export default function Layout() {
  const { logout } = useAuth()
  const location = useLocation()
  const [chatHistoryCount, setChatHistoryCount] = useState(0)

  // Load chat history count
  useEffect(() => {
    loadHistoryCount()
  }, [location.pathname]) // Reload when navigating

  const loadHistoryCount = async () => {
    try {
      const response = await api.get('/chat/history?limit=1')
      // Count unique conversations (each has question and answer, so divide by 2)
      const count = response.data?.length || 0
      setChatHistoryCount(Math.floor(count / 2))
    } catch (error) {
      // Ignore errors, just don't show count
      setChatHistoryCount(0)
    }
  }

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Predictions', href: '/predictions', icon: TrendingUp },
    { name: 'AI Chat', href: '/chat', icon: MessageSquare },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-2 px-6 py-6 border-b">
            <Zap className="w-8 h-8 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">Energy Forecast</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isChat = item.href === '/chat'
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5" />
                    {item.name}
                  </div>
                  {isChat && chatHistoryCount > 0 && (
                    <span className="bg-primary-600 text-white text-xs px-2 py-1 rounded-full">
                      {chatHistoryCount}
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t">
            <button
              onClick={logout}
              className="flex items-center gap-3 w-full px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="pl-64">
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

