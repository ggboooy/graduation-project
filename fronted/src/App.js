import React, { useState } from 'react';
import ChatRoom from './components/ChatRoom';
import UserSwitch from './components/UserSwitch';
import './App.css';

function App() {
  const [currentUser, setCurrentUser] = useState('张三');

  const handleUserSwitch = (user) => {
    setCurrentUser(user);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>协作学习对话系统</h1>
        <UserSwitch currentUser={currentUser} onUserSwitch={handleUserSwitch} />
      </header>
      <main>
        <ChatRoom currentUser={currentUser} />
      </main>
    </div>
  );
}

export default App;
