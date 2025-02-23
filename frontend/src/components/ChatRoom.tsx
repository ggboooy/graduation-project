import React, { useState, useEffect } from 'react';

interface AIResponse {
  response: string;
  is_anomaly: boolean;
  reason: string;
  analysis: {
    attacker: string;
    victim: string;
  };
  responses: {
    to_attacker: string;
    to_victim: string;
    to_others: string;
  };
}

interface Message {
  id: string;
  content: string;
  sender: string;
  timestamp: string;
  aiResponse?: AIResponse;
}

const ChatRoom: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentUser, setCurrentUser] = useState('张三');

  const handleSendMessage = async (content: string) => {
    try {
      const timestamp = new Date().toISOString();
      
      // 添加用户消息
      const userMessage: Message = {
        id: `${timestamp}_user`,
        content,
        sender: currentUser,
        timestamp: new Date().toLocaleString()
      };
      
      setMessages(prev => [...prev, userMessage]);

      // 发送到后端
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          user: currentUser,
        }),
      });

      const data: AIResponse = await response.json();
      
      // 添加AI回应
      const aiMessage: Message = {
        id: `${timestamp}_ai`,
        content: data.responses[currentUser === data.analysis.attacker 
          ? 'to_attacker' 
          : currentUser === data.analysis.victim 
            ? 'to_victim' 
            : 'to_others'],
        sender: 'AI助手',
        timestamp: new Date().toLocaleString(),
        aiResponse: {
          is_anomaly: data.is_anomaly,
          reason: data.reason,
          analysis: data.analysis,
          responses: data.responses,
          response: data.response
        }
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('发送消息失败:', error);
    }
  };

  // 修改 getResponseForCurrentUser 函数
  const getResponseForCurrentUser = (message: Message): string => {
    if (!message.aiResponse?.responses) return message.content;
    
    const { analysis, responses } = message.aiResponse;
    
    // 根据当前用户身份返回对应的回应
    if (currentUser === analysis.attacker) {
      return responses.to_attacker;
    } else if (currentUser === analysis.victim) {
      return responses.to_victim;
    } else {
      return responses.to_others;
    }
  };

  useEffect(() => {
    // 获取历史消息
    const fetchHistory = async () => {
      try {
        const response = await fetch('http://localhost:5000/chat/history');
        const data = await response.json();
        if (data.messages) {
          setMessages(data.messages);
        }
      } catch (error) {
        console.error('获取历史消息失败:', error);
      }
    };

    fetchHistory();
  }, []);

  // 当用户切换时，重新获取历史消息
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch('http://localhost:5000/chat/history');
        const data = await response.json();
        if (data.messages) {
          setMessages(data.messages);
        }
      } catch (error) {
        console.error('获取历史消息失败:', error);
      }
    };

    fetchHistory();
  }, [currentUser]); // 添加 currentUser 作为依赖

  return (
    <div className="chat-room">
      <div className="user-switch">
        <button onClick={() => setCurrentUser('张三')} className={currentUser === '张三' ? 'active' : ''}>
          张三
        </button>
        <button onClick={() => setCurrentUser('李四')} className={currentUser === '李四' ? 'active' : ''}>
          李四
        </button>
      </div>
      <div className="messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender === currentUser ? 'sent' : 'received'}`}>
            <div className="message-header">
              <span className="sender">{message.sender}</span>
              <span className="timestamp">{message.timestamp}</span>
            </div>
            <div className="message-content">
              <p>
                {message.sender === 'AI助手' 
                  ? getResponseForCurrentUser(message)
                  : message.content
                }
              </p>
              {message.aiResponse?.is_anomaly && currentUser === message.aiResponse.analysis.victim && (
                <div className="ai-analysis">
                  <p className="reason">{message.aiResponse.reason}</p>
                  <p className="warning">检测到攻击行为，请保持冷静</p>
                </div>
              )}
              {message.aiResponse?.is_anomaly && currentUser === message.aiResponse.analysis.attacker && (
                <div className="ai-analysis warning">
                  <p className="reason">{message.aiResponse.reason}</p>
                  <p className="warning">请注意您的言行</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatRoom; 