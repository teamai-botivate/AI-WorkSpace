import React, { useState } from 'react';
import { Send, FileText, Clock } from 'lucide-react';

const HRSupportPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'requests'>('chat');
  const [message, setMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMsg = { role: 'user', content: message };
    setChatMessages(prev => [...prev, userMsg]);
    setMessage('');
    setLoading(true);

    try {
      const res = await fetch('/api/hr_support/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content, company_id: 1 }),
      });

      if (res.ok) {
        const data = await res.json();
        setChatMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
      }
    } catch {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Is the backend running?' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-full flex flex-col">
      {/* Tab Bar */}
      <div className="flex gap-1 p-1 bg-slate-800/50 rounded-xl mb-6">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'chat' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          💬 Chat with HR Bot
        </button>
        <button
          onClick={() => setActiveTab('requests')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'requests' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          📋 My Requests
        </button>
      </div>

      {activeTab === 'chat' && (
        <div className="flex-1 flex flex-col bg-slate-800/30 rounded-2xl border border-slate-700/50 overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {chatMessages.length === 0 && (
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-green-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-8 h-8 text-green-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">HR Support Bot</h3>
                <p className="text-slate-400 text-sm max-w-sm mx-auto">
                  Ask me about leave policies, company guidelines, request approvals, or any HR-related questions.
                </p>
              </div>
            )}
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-md'
                      : 'bg-slate-700/50 text-slate-200 rounded-bl-md'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-700/50 px-4 py-3 rounded-2xl rounded-bl-md">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-slate-700/30">
            <div className="flex gap-3">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask a question..."
                className="flex-1 bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-white placeholder-slate-400 text-sm focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !message.trim()}
                className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'requests' && (
        <div className="bg-slate-800/30 rounded-2xl border border-slate-700/50 p-6">
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-slate-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-white mb-2">Approval Requests</h3>
            <p className="text-slate-400 text-sm">
              Submit leave requests, grievances, and expenses here. Log in to view your requests.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default HRSupportPage;
