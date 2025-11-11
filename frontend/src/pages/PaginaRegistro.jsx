import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://127.0.0.1:8000';

function PaginaRegistro() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    try {
      await axios.post(`${API_URL}/usuarios`, {
        username: username,
        password: password,
      });

      setSuccessMessage('¡Registro exitoso! Serás redirigido al login...');
      
      // Redirige al login después de 2 segundos
      setTimeout(() => {
        navigate('/login');
      }, 2000);

    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error en el registro. Inténtalo de nuevo.';
      setError(errorMsg);
    }
  };

  return (
    <div className="form-section">
      <h2 className="section-title">Registro de Nuevo Usuario</h2>
      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}
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
        <button type="submit" className="btn btn-primary btn-full">Registrarse</button>
      </form>
    </div>
  );
}

export default PaginaRegistro;