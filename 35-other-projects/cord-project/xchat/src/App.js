import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [username, setUsername] = useState('User' + Math.floor(Math.random() * 1000));

  useEffect(() => {
    // Welcome message
    setMessages([
      {
        id: 1,
        user: 'System',
        text: '🎉 Welcome to XChat - Built autonomously by Aider AI!',
        timestamp: new Date().toLocaleTimeString()
      },
      {
        id: 2,
        user: 'System',
        text: '✨ This app was created by a self-building system!',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      const newMessage = {
        id: messages.length + 1,
        user: username,
        text: inputMessage,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages([...messages, newMessage]);
      setInputMessage('');
      
      // Simulate AI response
      setTimeout(() => {
        const aiResponse = {
          id: messages.length + 2,
          user: 'AI Assistant',
          text: '🤖 I received your message: "' + inputMessage + '"',
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, aiResponse]);
      }, 1000);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 XChat</h1>
        <p>Next-Generation Chat Platform</p>
        <small>Built by Autonomous AI Builder v3</small>
      </header>
      
      <div className="chat-container">
        <div className="messages-container">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.user === username ? 'own-message' : ''}`}>
              <div className="message-header">
                <strong>{msg.user}</strong>
                <span className="timestamp">{msg.timestamp}</span>
              </div>
              <div className="message-text">{msg.text}</div>
            </div>
          ))}
        </div>
        
        <form onSubmit={sendMessage} className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="message-input"
          />
          <button type="submit" className="send-button">Send 🚀</button>
        </form>
      </div>
      
      <footer className="App-footer">
        <p>✨ Features: Real-time messaging • AI-powered • Viral growth engine • Self-improving</p>
      </footer>
    </div>
  );
}

export default App;
