import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'

const API_URL = 'http://localhost:8000'

const starterPrompts = [
  "How can I reduce my carbon footprint at home?",
  "What's the air quality in Bloomington today?",
  "How much CO2 does driving 50 miles produce?",
  "What are the basics of composting?"
]

function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim()) return

    const userMsg = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: 'session1' })
      })
      const data = await res.json()
      const assistantMsg = { 
        role: 'assistant', 
        content: data.answer,
        sources: data.sources 
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'sorry, something went wrong. make sure the backend is running.' 
      }])
    }
    setLoading(false)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const clearChat = async () => {
    setMessages([])
    try {
      await fetch(`${API_URL}/clear?session_id=session1`, { method: 'POST' })
    } catch (err) {}
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="flex-shrink-0 border-b border-sage-200 dark:border-sage-800 px-6 py-4 bg-background-light dark:bg-background-dark">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="material-icons-outlined text-sage-500 text-2xl">eco</span>
            <h1 className="text-xl font-medium">ecohelper</h1>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="p-2 rounded-lg hover:bg-surface-light dark:hover:bg-surface-dark transition-colors"
                title="clear chat"
              >
                <span className="material-icons-outlined text-muted-light dark:text-muted-dark text-xl">delete_outline</span>
              </button>
            )}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg hover:bg-surface-light dark:hover:bg-surface-dark transition-colors"
            >
              <span className="material-icons-outlined text-xl">
                {darkMode ? 'light_mode' : 'dark_mode'}
              </span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
              <span className="material-icons-outlined text-sage-400 text-6xl mb-6">park</span>
              <h2 className="text-2xl font-medium mb-3">hey, i'm ecohelper</h2>
              <p className="text-muted-light dark:text-muted-dark mb-8 max-w-md">
                your friendly guide to sustainable living. ask me about recycling, energy, composting, air quality in your city, or carbon emissions from activities.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                {starterPrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(prompt)}
                    className="text-left p-4 rounded-xl border border-sage-200 dark:border-sage-800 hover:border-sage-400 dark:hover:border-sage-600 hover:bg-surface-light dark:hover:bg-surface-dark transition-all text-sm"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 pb-4">
              {messages.map((msg, i) => (
                <div key={i} className="flex gap-4">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === 'user' 
                      ? 'bg-sage-500 text-white' 
                      : 'bg-sage-100 dark:bg-sage-900 text-sage-600 dark:text-sage-400'
                  }`}>
                    <span className="material-icons-outlined text-lg">
                      {msg.role === 'user' ? 'person' : 'eco'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-muted-light dark:text-muted-dark mb-2">
                      {msg.role === 'user' ? 'you' : 'ecohelper'}
                    </p>
                    {msg.role === 'assistant' ? (
                      <div className="prose-container">
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
                            ul: ({ children }) => <ul className="mb-4 ml-4 space-y-2">{children}</ul>,
                            ol: ({ children }) => <ol className="mb-4 ml-4 space-y-2 list-decimal">{children}</ol>,
                            li: ({ children }) => (
                              <li className="flex gap-2">
                                <span className="text-sage-500">•</span>
                                <span>{children}</span>
                              </li>
                            ),
                            strong: ({ children }) => <strong className="font-semibold text-sage-600 dark:text-sage-400">{children}</strong>,
                            h1: ({ children }) => <h1 className="text-xl font-semibold mb-3 mt-4">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 mt-4">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-3">{children}</h3>,
                            code: ({ inline, children }) => 
                              inline 
                                ? <code className="bg-surface-light dark:bg-surface-dark px-1.5 py-0.5 rounded text-sm">{children}</code>
                                : <code className="block bg-surface-light dark:bg-surface-dark p-4 rounded-lg text-sm overflow-x-auto mb-4">{children}</code>,
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-2 border-sage-400 pl-4 italic text-muted-light dark:text-muted-dark mb-4">
                                {children}
                              </blockquote>
                            ),
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-sage-200 dark:border-sage-800">
                            <p className="text-xs text-muted-light dark:text-muted-dark mb-2 flex items-center gap-1">
                              <span className="material-icons-outlined text-sm">link</span>
                              sources
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {msg.sources.map((src, j) => (
                                <a
                                  key={j}
                                  href={src}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-xs bg-surface-light dark:bg-surface-dark px-2 py-1 rounded-md text-sage-600 dark:text-sage-400 hover:bg-sage-100 dark:hover:bg-sage-900 transition-colors"
                                >
                                  <span className="material-icons-outlined text-xs">open_in_new</span>
                                  {new URL(src).hostname.replace('www.', '')}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="leading-relaxed">{msg.content}</p>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-sage-100 dark:bg-sage-900 text-sage-600 dark:text-sage-400">
                    <span className="material-icons-outlined text-lg">eco</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-medium text-muted-light dark:text-muted-dark mb-2">ecohelper</p>
                    <div className="flex gap-1 py-2">
                      <span className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      <footer className="flex-shrink-0 border-t border-sage-200 dark:border-sage-800 px-6 py-4 bg-background-light dark:bg-background-dark">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="ask about sustainability..."
              disabled={loading}
              className="flex-1 bg-surface-light dark:bg-surface-dark rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-sage-400 transition-all placeholder:text-muted-light dark:placeholder:text-muted-dark"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-sage-500 hover:bg-sage-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl px-5 py-3 transition-colors"
            >
              <span className="material-icons-outlined">arrow_upward</span>
            </button>
          </div>
        </form>
      </footer>
    </div>
  )
}

export default App
