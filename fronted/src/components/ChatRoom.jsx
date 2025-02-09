import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatRoom.css';

function ChatRoom({ currentUser }) {
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 加载历史记录
  const loadChatHistory = async () => {
    try {
      console.log("开始加载历史记录..."); // 添加调试日志
      const response = await fetch('http://localhost:5000/chat/history');
      const data = await response.json();
      console.log("收到的历史记录:", data); // 添加调试日志
      
      if (data.messages && Array.isArray(data.messages)) {
        // 按时间戳排序消息
        const sortedMessages = data.messages.sort((a, b) => 
          new Date(a.timestamp) - new Date(b.timestamp)
        );
        console.log("排序后的消息:", sortedMessages); // 添加调试日志
        setMessages(sortedMessages);
      } else {
        console.log("没有历史消息或消息格式不正确");
      }
    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  };

  // 组件加载时获取历史记录
  useEffect(() => {
    loadChatHistory();
  }, []);

  // 消息更新时滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content) => {
    if (!content.trim()) return;

    const timestamp = new Date().toLocaleString();
    const newMessage = {
      id: `${timestamp}_user`,
      content,
      sender: currentUser,
      timestamp,
    };

    setMessages(prev => [...prev, newMessage]);

    try {
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

      const data = await response.json();
      
      if (data.response) {
        const aiMessage = {
          id: `${timestamp}_ai`,
          content: data.response,
          sender: 'AI助手',
          timestamp: new Date().toLocaleString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('发送消息失败:', error);
    }
  };

  return (
    <div className="chat-room">
      <MessageList messages={messages} currentUser={currentUser} />
      <div ref={messagesEndRef} />
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatRoom; 