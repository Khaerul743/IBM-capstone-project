'use client'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Bot, Send, Trash2, User } from 'lucide-react'
import { useEffect, useState } from 'react'

// Define types
interface Message {
  id: number
  type: 'user' | 'ai'
  content: string
  isNew?: boolean
}

// Function to parse and format text
const formatText = (text: string) => {
  if (!text) return []
  
  // Split by lines to handle \n
  const lines = text.split('\n')
  
  return lines.map((line, lineIndex) => {
    // Handle bold text **text**
    const boldRegex = /\*\*(.*?)\*\*/g
    let lastIndex = 0
    const parts = []
    let match
    
    while ((match = boldRegex.exec(line)) !== null) {
      // Add text before bold
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: line.slice(lastIndex, match.index)
        })
      }
      
      // Add bold text
      parts.push({
        type: 'bold',
        content: match[1]
      })
      
      lastIndex = match.index + match[0].length
    }
    
    // Add remaining text
    if (lastIndex < line.length) {
      parts.push({
        type: 'text',
        content: line.slice(lastIndex)
      })
    }
    
    return {
      lineIndex,
      parts: parts.length > 0 ? parts : [{ type: 'text', content: line }]
    }
  })
}

// Custom hook for typing animation
const useTypingAnimation = (text: string, speed: number = 30) => {
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  useEffect(() => {
    if (!text) return

    setIsTyping(true)
    setDisplayedText('')
    
    let index = 0
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1))
        index++
      } else {
        setIsTyping(false)
        clearInterval(timer)
      }
    }, speed)

    return () => clearInterval(timer)
  }, [text, speed])

  return { displayedText, isTyping }
}

// Formatted message component
const FormattedMessage = ({ content, messageId }: { content: string; messageId: number }) => {
  const { displayedText, isTyping } = useTypingAnimation(content, 15)
  const formattedLines = formatText(displayedText)
  
  return (
    <div className="bg-gray-800 text-gray-100 p-3 rounded-lg rounded-bl-sm shadow-lg border border-gray-700">
      <div className="text-sm leading-relaxed whitespace-pre-wrap">
        {formattedLines.map((line, lineIndex) => (
          <div key={lineIndex} className="mb-1">
            {line.parts.map((part, partIndex) => (
              <span key={partIndex}>
                {part.type === 'bold' ? (
                  <strong className="font-bold text-white">{part.content}</strong>
                ) : (
                  <span>{part.content}</span>
                )}
              </span>
            ))}
          </div>
        ))}
        {isTyping && <span className="animate-pulse">|</span>}
      </div>
    </div>
  )
}

export default function AIAgent() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message to chat
    const newUserMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: userMessage
    }
    
    setMessages(prev => [...prev, newUserMessage])

    try {
      const response = await fetch('http://localhost:8080/api/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: userMessage
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response from AI agent')
      }

      const data = await response.json()
      
      // Add AI response to chat with typing animation
      const aiMessage: Message = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.response,
        isNew: true
      }
      
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error:', error)
      
      // Add error message
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Maaf, terjadi kesalahan saat menghubungi AI agent. Silakan coba lagi.',
        isNew: true
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">AI Agent Chat</h1>
          <p className="text-gray-400">Berbicara dengan AI agent Anda</p>
        </div>

        <Card className="shadow-2xl border border-gray-700 bg-gray-800">
          <CardHeader className="bg-gray-800 border-b border-gray-700">
            <div className="flex justify-between items-center">
              <CardTitle className="text-xl text-white flex items-center gap-2">
                <Bot className="w-6 h-6 text-blue-400" />
                AI Assistant
              </CardTitle>
              {messages.length > 0 && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={clearChat}
                  className="text-gray-300 hover:text-white border-gray-600 hover:border-gray-500 bg-transparent hover:bg-gray-700"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Clear Chat
                </Button>
              )}
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            {/* Chat Messages Area */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-900">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 mt-20">
                  <Bot className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                  <p className="text-lg">Mulai percakapan dengan AI agent</p>
                  <p className="text-sm">Ketik pesan Anda di bawah untuk memulai</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'ai' && (
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}
                    
                    <div className={`max-w-[70%] ${message.type === 'user' ? '' : ''}`}>
                      {message.type === 'user' ? (
                        <div className="bg-blue-600 text-white p-3 rounded-lg rounded-br-sm shadow-lg">
                          <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>
                        </div>
                      ) : (
                        <FormattedMessage content={message.content} messageId={message.id} />
                      )}
                    </div>
                    
                    {message.type === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-gray-800 p-3 rounded-lg rounded-bl-sm shadow-lg border border-gray-700">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-6 bg-gray-800 border-t border-gray-700">
              <form onSubmit={sendMessage} className="flex gap-3">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ketik pesan Anda di sini..."
                  disabled={isLoading}
                  className="flex-1 bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500"
                />
                <Button 
                  type="submit" 
                  disabled={isLoading || !input.trim()}
                  className="bg-blue-600 hover:bg-blue-700 px-6 disabled:bg-gray-600"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </form>
              
              {/* Status indicator */}
              <div className="mt-3 text-xs text-gray-500 flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                AI Agent siap membantu Anda
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
