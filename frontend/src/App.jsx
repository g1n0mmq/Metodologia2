import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';

// --- 1. Importa tus nombres de archivo ---
import PaginaHome from './pages/PaginaHome.jsx'; // <-- ¡CORREGIDO!
import PaginaCliente from './pages/PaginaCliente.jsx';
import PaginaProductos from './pages/PaginaProductos.jsx';

// (Aquí iría el import './App.css')

function App() {
  return (
    <div>
      <nav>
        <h3>TP Final</h3>
        <ul>
          <li>
            <NavLink to="/">Inicio</NavLink>
          </li>
          <li>
            <NavLink to="/clientes">Clientes</NavLink>
          </li>
          <li>
            <NavLink to="/productos">Productos</NavLink>
          </li>
        </ul>
      </nav>

      {/* --- 2. Usa tus componentes en las rutas --- */}
      <main>
        <Routes>
          <Route path="/" element={<PaginaHome />} />
          <Route path="/clientes" element={<PaginaCliente />} />
          <Route path="/productos" element={<PaginaProductos />} />
        </Routes>
      </main>
      
    </div>
  );
}

export default App;