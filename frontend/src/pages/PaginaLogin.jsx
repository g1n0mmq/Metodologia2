import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://127.0.0.1:8000';

function PaginaLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      // --- CORRECCIÓN: El endpoint /token espera datos en formato 'form data', no JSON. ---
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(`${API_URL}/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // Guardamos el token en el almacenamiento local
      localStorage.setItem('authToken', response.data.access_token);

      // Redirigimos al inicio y recargamos para actualizar la UI
      navigate('/');
      window.location.reload();

    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.';
      setError(errorMsg);
    }
  };

  return (
    <div className="form-section">
      <h2 className="section-title">Iniciar Sesión</h2>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Usuario: </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Contraseña: </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary btn-full">Login</button>
      </form>
    </div>
  );
}

export default PaginaLogin;