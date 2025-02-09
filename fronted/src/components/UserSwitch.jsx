import React from 'react';
import './UserSwitch.css';

function UserSwitch({ currentUser, onUserSwitch }) {
  return (
    <div className="user-switch">
      <span>当前用户：{currentUser}</span>
      <div className="switch-buttons">
        <button 
          className={currentUser === '张三' ? 'active' : ''} 
          onClick={() => onUserSwitch('张三')}
        >
          张三
        </button>
        <button 
          className={currentUser === '李四' ? 'active' : ''} 
          onClick={() => onUserSwitch('李四')}
        >
          李四
        </button>
      </div>
    </div>
  );
}

export default UserSwitch; 