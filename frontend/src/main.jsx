import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { BrowserRouter } from 'react-router-dom'; // <-- Importa el Router
import './index.css'; // (CSS global si lo usas)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter> {/* <-- Envuelve tu <App /> */}
      <App />
    </BrowserRouter>
  </React.StrictMode>
);