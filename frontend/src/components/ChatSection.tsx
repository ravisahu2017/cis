'use client';

import { useEffect, useState } from 'react';
import { Bot, User, Send } from 'lucide-react';
import { ChatMessage } from '@/models/models';
import { getAnalysisChatMsg } from '@/models/dataFiller';
import { backendApi } from '@/utils/api';

interface ChatSectionProps {
  analysisResults: any;
}

export default function ChatSection({
  analysisResults
}: ChatSectionProps) {

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      message: 'Hello! I\'m your contract intelligence assistant. How can I help you analyze contracts today?',
      timestamp: '9:50 PM'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isChatStreaming, setIsChatStreaming] = useState(false);

  useEffect(() => {
    if(!analysisResults) return;
    const analysisMessage: ChatMessage = getAnalysisChatMsg(analysisResults, 1);
    setChatMessages(prev => [...prev, analysisMessage]);
  }, [analysisResults]);

    const handleSendMessage = async () => {
    if (!inputMessage.trim() || isChatStreaming) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      message: inputMessage,
      timestamp: new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsChatStreaming(true);
    setCurrentStreamingMessage('');
    
    // Create a placeholder for streaming response
    const botMessageId = (Date.now() + 1).toString();
    const botMessagePlaceholder: ChatMessage = {
      id: botMessageId,
      type: 'bot',
      message: '',
      timestamp: new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    };
    
    setChatMessages(prev => [...prev, botMessagePlaceholder]);
    
    try {
      // Prepare context from analysis results if available
      const context = analysisResults ? {
        contract_name: analysisResults.contract_name,
        overall_risk_score: analysisResults.overall_risk_score,
        clauses: analysisResults.clauses.map(c => ({
          type: c.clause_type,
          risk_score: c.risk_score,
          risk_tag: c.risk_tag,
          content: c.content.substring(0, 200) + '...'
        }))
      } : null;
      
      // Use regular HTTP API for chat
      const requestData = {
        message: inputMessage,
        context: context,
        session_id: null,
        user_id: null
      };

      const response = await backendApi.post('/chat', requestData);
      
      if (response.success && response.data) {
        const botResponse: ChatMessage = {
          id: botMessageId,
          type: 'bot',
          message: response.data.message || response.data.response || 'I received your message but couldn\'t generate a response.',
          timestamp: new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          })
        };
        setChatMessages(prev => prev.map(msg => 
          msg.id === botMessageId ? botResponse : msg
        ));
      } else {
        throw new Error(response.error || 'Chat request failed');
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: ChatMessage = {
        id: botMessageId,
        type: 'bot',
        message: `Sorry, I'm having trouble connecting right now. Please try again.`,
        timestamp: new Date().toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
      };
      
      setChatMessages(prev => prev.map(msg => 
        msg.id === botMessageId ? errorMessage : msg
      ));
    } finally {
      setIsChatStreaming(false);
      setCurrentStreamingMessage('');
    }
  };

  return (
    <div className="w-[500px] bg-white border-l border-gray-200 flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-medium">AI Assistant</h3>
            <p className="text-xs text-gray-500">Always here to help</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.type === 'user'
                  ? 'bg-[#1A1A1A] text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'bot' && (
                  <Bot className="w-4 h-4 mt-0.5 text-gray-600" />
                )}
                <div>
                  <p className="text-sm whitespace-pre-wrap">{message.message}</p>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-gray-300' : 'text-gray-500'
                  }`}>
                    {message.timestamp}
                  </p>
                </div>
                {message.type === 'user' && (
                  <User className="w-4 h-4 mt-0.5 text-gray-300" />
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Chat Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
            placeholder={isChatStreaming ? "AI is responding..." : "Ask about contracts, compliance, or analysis..."}
            disabled={isChatStreaming}
            className="flex-1 px-4 py-3 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={isChatStreaming || !inputMessage.trim()}
            className="px-4 py-3 bg-[#1A1A1A] text-white rounded-xl hover:bg-[#2A2A2A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isChatStreaming ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
        {analysisResults && (
          <div className="mt-2 text-xs text-gray-500">
            💡 I can help you analyze uploaded contract. Ask me about risks, clauses, or recommendations.
          </div>
        )}
      </div>
    </div>
  );
}
