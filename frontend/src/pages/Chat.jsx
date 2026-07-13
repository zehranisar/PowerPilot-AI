import { useState, useRef, useEffect } from 'react'
import api from '../services/api'
import { Send, Loader2, Bot, User, Trash2, History } from 'lucide-react'

// Format message content with clean, readable HTML styling
const formatMessage = (text) => {
  if (!text) return ''
  
  // Escape HTML to prevent XSS
  const escapeHtml = (str) => {
    const div = document.createElement('div')
    div.textContent = str
    return div.innerHTML
  }
  
  let formatted = escapeHtml(text)
  
  // Handle code blocks first (before other processing)
  formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
  
  // Bold text **text** or __text__
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>')
  
  // Inline code `code` (but not in code blocks)
  formatted = formatted.replace(/`([^`\n]+)`/g, '<code>$1</code>')
  
  // Headers
  formatted = formatted.replace(/^### (.*)$/gm, '<h3>$1</h3>')
  formatted = formatted.replace(/^## (.*)$/gm, '<h2>$1</h2>')
  formatted = formatted.replace(/^# (.*)$/gm, '<h1>$1</h1>')
  
  // Numbered lists (1. item)
  formatted = formatted.replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>')
  // Wrap consecutive list items in <ol>
  formatted = formatted.replace(/(<li>.*<\/li>(\n<li>.*<\/li>)*)/g, '<ol>$1</ol>')
  
  // Bullet lists (- item or * item)
  formatted = formatted.replace(/^[-*•]\s+(.+)$/gm, '<li>$1</li>')
  // Wrap consecutive bullet items in <ul> (but not if already in <ol>)
  formatted = formatted.replace(/(?<!<\/ol>\n)(<li>.*<\/li>(\n<li>.*<\/li>)*)(?!\n<ol>)/g, '<ul>$1</ul>')
  
  // Split into paragraphs (double line breaks)
  const paragraphs = formatted.split(/\n\n+/)
  formatted = paragraphs.map(p => {
    const trimmed = p.trim()
    if (!trimmed) return ''
    // If it's already HTML (starts with <), return as is
    if (trimmed.startsWith('<')) return trimmed
    // Otherwise wrap in paragraph
    return `<p>${trimmed}</p>`
  }).join('')
  
  // Convert single line breaks to <br> within paragraphs
  formatted = formatted.replace(/(<p>)([^<]*?)(\n)([^<]*?)(<\/p>)/g, '$1$2<br>$4$5')
  
  // Clean up: remove empty paragraphs
  formatted = formatted.replace(/<p>\s*<\/p>/g, '')
  
  return formatted
}

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const messagesEndRef = useRef(null)

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory()
  }, [])

  const loadChatHistory = async () => {
    try {
      setLoadingHistory(true)
      const response = await api.get('/chat/history')
      const history = response.data || []
      
      // Convert history to message format
      const historyMessages = []
      history.forEach((chat) => {
        historyMessages.push({
          role: 'user',
          content: chat.question,
          id: chat.id,
          timestamp: chat.created_at
        })
        historyMessages.push({
          role: 'assistant',
          content: chat.answer,
          id: chat.id,
          timestamp: chat.created_at
        })
      })
      
      // If no history, show welcome message
      if (historyMessages.length === 0) {
        setMessages([{
          role: 'assistant',
          content: 'Hello! I can help you with electricity consumption forecasting. Ask me about summaries, predictions, patterns, or anything related to your consumption data.',
          id: 'welcome'
        }])
      } else {
        setMessages(historyMessages)
      }
    } catch (error) {
      console.error('Error loading chat history:', error)
      // Show welcome message on error
      setMessages([{
        role: 'assistant',
        content: 'Hello! I can help you with electricity consumption forecasting. Ask me about summaries, predictions, patterns, or anything related to your consumption data.',
        id: 'welcome'
      }])
    } finally {
      setLoadingHistory(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message immediately
    const userMsg = { role: 'user', content: userMessage }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const response = await api.post('/chat', { question: userMessage })
      // Add assistant response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.answer,
        id: response.data.history_id
      }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.',
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const clearHistory = async () => {
    try {
      await api.delete('/chat/history')
      setMessages([{
        role: 'assistant',
        content: 'Hello! I can help you with electricity consumption forecasting. Ask me about summaries, predictions, patterns, or anything related to your consumption data.',
        id: 'welcome'
      }])
    } catch (error) {
      console.error('Error clearing history:', error)
      alert('Failed to clear chat history')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
          <p className="text-gray-600 mt-2">Ask questions about your electricity consumption data</p>
        </div>
        <button
          onClick={clearHistory}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-2"
          title="Clear chat history"
        >
          <Trash2 className="w-4 h-4" />
          Clear History
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col" style={{ height: 'calc(100vh - 250px)' }}>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {loadingHistory ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
          ) : (
            <>
              {messages.map((message, idx) => (
                <div
                  key={message.id || idx}
                  className={`flex gap-4 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                      <Bot className="w-6 h-6 text-primary-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-2xl rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900 border border-gray-200'
                    }`}
                  >
                    {message.role === 'assistant' ? (
                      <div 
                        className="chat-message"
                        dangerouslySetInnerHTML={{ 
                          __html: formatMessage(message.content) 
                        }}
                      />
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}
                    {message.timestamp && (
                      <p className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-primary-100' : 'text-gray-500'
                      }`}>
                        {new Date(message.timestamp).toLocaleString()}
                      </p>
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-gray-600" />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-4 justify-start">
                  <div className="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <Bot className="w-6 h-6 text-primary-600" />
                  </div>
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about electricity consumption..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              disabled={loading || loadingHistory}
            />
            <button
              type="submit"
              disabled={loading || !input.trim() || loadingHistory}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
