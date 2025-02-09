import React from 'react';
import './MessageList.css';

function MessageList({ messages, currentUser }) {
  return (
    <div className="message-list">
      {messages && messages.length > 0 ? (
        messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender === currentUser ? 'sent' : 'received'}`}
          >
            <div className="message-header">
              <span className="sender">{message.sender}</span>
              <span className="timestamp">{message.timestamp}</span>
            </div>
            <div className="message-content">{message.content}</div>
          </div>
        ))
      ) : (
        <div className="no-messages">暂无消息</div>
      )}
    </div>
  );
}

export default MessageList; 