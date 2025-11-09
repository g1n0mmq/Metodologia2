import React from 'react';
import { Navigate } from 'react-router-dom';

function RutaProtegida({ children }) {
  const token = localStorage.getItem('authToken');

  // Si no hay token, redirige al usuario a la página de login
  return token ? children : <Navigate to="/login" />;
}

export default RutaProtegida;