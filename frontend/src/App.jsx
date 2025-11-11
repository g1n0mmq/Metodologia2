import React from 'react';
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom';

// --- 1. Importa tus nombres de archivo ---
import PaginaHome from './pages/PaginaHome.jsx'; // <-- CORREGIDO
import PaginaCliente from './pages/PaginaCliente.jsx';
import PaginaProductos from './pages/PaginaProductos.jsx';
import PaginaFacturas from './pages/PaginaFacturas.jsx';
import PaginaLogin from './pages/PaginaLogin.jsx';
import PaginaRegistro from './pages/PaginaRegistro.jsx'; // <-- IMPORTA LA PÁGINA DE REGISTRO
import RutaProtegida from './pages/RutaProtegida.jsx'; // <-- IMPORTA EL COMPONENTE PROTECTOR

function App() {
  const navigate = useNavigate();
  const token = localStorage.getItem('authToken');

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    navigate('/login');
    window.location.reload();
  };

  return (
    <div className="container">
      <nav className="main-nav">
        <h3 className="nav-brand">TP Final</h3>
        <ul className="nav-links">
          <li><NavLink to="/">Inicio</NavLink></li>
          {token ? (
            <>
              <li><NavLink to="/clientes">Clientes</NavLink></li>
              <li><NavLink to="/productos">Productos</NavLink></li>
              <li><NavLink to="/facturas">Facturas</NavLink></li>
              <li><button onClick={handleLogout} className="btn-logout">Logout</button></li>
            </>
          ) : (
            <>
              <li><NavLink to="/login">Login</NavLink></li>
              <li><NavLink to="/registro">Registro</NavLink></li>
            </>
          )}
        </ul>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<PaginaHome />} />
          <Route path="/login" element={<PaginaLogin />} />
          <Route path="/registro" element={<PaginaRegistro />} />
          
          {/* --- RUTAS PROTEGIDAS --- */}
          <Route path="/clientes" element={<RutaProtegida><PaginaCliente /></RutaProtegida>} />
          <Route path="/productos" element={<RutaProtegida><PaginaProductos /></RutaProtegida>} />
          <Route path="/facturas" element={<RutaProtegida><PaginaFacturas /></RutaProtegida>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;