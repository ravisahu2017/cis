'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, TrendingUp, AlertTriangle, Clock, Users, Settings, Send, Bot, User } from 'lucide-react';

interface DashboardTile {
  id: string;
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  message: string;
  timestamp: string;
}

export default function Home() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      message: 'Hello! I\'m your contract intelligence assistant. How can I help you analyze contracts today?',
      timestamp: '9:50 PM'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const dashboardTiles: DashboardTile[] = [
    {
      id: '1',
      title: 'Active Contracts',
      value: '24',
      subtitle: 'Currently under review',
      icon: <FileText className="w-6 h-6" />,
      color: 'bg-blue-50 text-blue-600',
      trend: '+3 this week'
    },
    {
      id: '2',
      title: 'Risk Score',
      value: '7.2',
      subtitle: 'Average risk level',
      icon: <AlertTriangle className="w-6 h-6" />,
      color: 'bg-orange-50 text-orange-600',
      trend: '-0.5 from last month'
    },
    {
      id: '3',
      title: 'Compliance Rate',
      value: '94%',
      subtitle: 'Meets standards',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'bg-green-50 text-green-600',
      trend: '+2% improvement'
    },
    {
      id: '4',
      title: 'Pending Reviews',
      value: '8',
      subtitle: 'Awaiting approval',
      icon: <Clock className="w-6 h-6" />,
      color: 'bg-purple-50 text-purple-600',
      trend: '2 urgent'
    },
    {
      id: '5',
      title: 'Team Members',
      value: '12',
      subtitle: 'Active users',
      icon: <Users className="w-6 h-6" />,
      color: 'bg-indigo-50 text-indigo-600',
      trend: 'All online'
    },
    {
      id: '6',
      title: 'System Health',
      value: '98%',
      subtitle: 'Operational status',
      icon: <Settings className="w-6 h-6" />,
      color: 'bg-emerald-50 text-emerald-600',
      trend: 'All systems normal'
    }
  ];

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const now = new Date();
      const timeString = now.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
      
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'user',
        message: inputMessage,
        timestamp: timeString
      };
      
      setChatMessages([...chatMessages, newMessage]);
      
      // Simulate bot response
      setTimeout(() => {
        const botTime = new Date();
        const botTimeString = botTime.toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        });
        
        const botResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          message: 'I\'m analyzing your request. Let me help you with that contract query.',
          timestamp: botTimeString
        };
        setChatMessages(prev => [...prev, botResponse]);
      }, 1000);
      
      setInputMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F8F8] text-[#1A1A1A]">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-[#E5E5E5]">
        <div className="max-w-full px-6 py-4 flex justify-between items-center">
          <div className="text-2xl font-light tracking-wide">Contract Intelligence System</div>
          <div className="flex items-center space-x-4">
            <button className="px-4 py-2 text-[#1A1A1A] hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors">
              Settings
            </button>
            <div className="w-8 h-8 bg-[#1A1A1A] rounded-full flex items-center justify-center text-white text-sm">
              U
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-20 h-screen flex">
        {/* Dashboard Section - Left */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-6xl">
            <div className="mb-8">
              <h1 className="text-3xl font-light mb-2">Dashboard Overview</h1>
              <p className="text-gray-600">Monitor your contract intelligence metrics</p>
            </div>

            {/* Dashboard Tiles Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {dashboardTiles.map((tile, index) => (
                <motion.div
                  key={tile.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg ${tile.color}`}>
                      {tile.icon}
                    </div>
                    <span className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded">
                      {tile.trend}
                    </span>
                  </div>
                  <div className="mb-1">
                    <h3 className="text-2xl font-semibold">{tile.value}</h3>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{tile.title}</h4>
                    <p className="text-xs text-gray-500">{tile.subtitle}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Recent Activity Section */}
            <div className="mt-8">
              <h2 className="text-xl font-light mb-4">Recent Activity</h2>
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Contract #1234 reviewed</p>
                      <p className="text-xs text-gray-500">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">High-risk contract flagged</p>
                      <p className="text-xs text-gray-500">4 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Compliance check completed</p>
                      <p className="text-xs text-gray-500">6 hours ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Section - Right */}
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
                      <p className="text-sm">{message.message}</p>
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
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about contracts, compliance, or analysis..."
                className="flex-1 px-4 py-3 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSendMessage}
                className="px-4 py-3 bg-[#1A1A1A] text-white rounded-xl hover:bg-[#2A2A2A] transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
