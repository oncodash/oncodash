import logo from './logo.svg';
import './App.css';
import Oncoview from './components/Oncoview/Oncoview'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Welcome to Oncodash.
        </p>
        <Oncoview />
      </header>
    </div>
  );
}

export default App;
