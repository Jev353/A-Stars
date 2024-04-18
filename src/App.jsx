import { useState } from 'react'
import './App.css'
import Dashboard from './components/Dashboard/Dashboard';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';




function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogin = () => {
    // Perform login authentication here (not implemented in this example)
    // For simplicity, let's just check if username and password are not empty
    if (username.trim() !== '' && password.trim() !== '') {
      setLoggedIn(true);
      history.push('/dashboard');
    } else {
      alert('Please enter valid username and password.');
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
    // You can also clear username and password fields if needed
  };

  return (
    <div className="App">
      {loggedIn ? (
        <div>
          <h2>Welcome, {username}!</h2>
          <button onClick={handleLogout}>Logout</button>
        </div>
      ) : (
        <div>
          <h2>Login</h2>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <br />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <br />
          <button onClick={handleLogin}>Login</button>
        </div>
      )}
    </div>
  );  
}

export default App
