import React, { useState, useEffect } from 'react';
import axios from 'axios'; 

// --- 1. CORRECCIÓN: Quita la barra de aquí ---
const API_URL = 'http://127.0.0.1:8000';

function PaginaCliente() {
  const [clientes, setClientes] = useState([]);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    dni: '',
    direccion: '',
    telefono: ''
  });

  const fetchClientes = async () => {
    try {
      // --- 2. CORRECCIÓN: Añade la ruta completa con la barra al final ---
      const response = await axios.get(`${API_URL}/clientes/`);
      setClientes(response.data);
    } catch (err) {
      setError('Error al cargar los clientes: ' + err.message);
    }
  };

  useEffect(() => {
    fetchClientes();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      // --- 3. CORRECCIÓN: Esta ya estaba bien, pero ahora funciona con el API_URL limpio ---
      const response = await axios.post(`${API_URL}/clientes/`, formData);
      setClientes([...clientes, response.data]);
      setFormData({
        nombre: '',
        apellido: '',
        dni: '',
        direccion: '',
        telefono: ''
      });
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError('Error al crear el cliente: ' + JSON.stringify(err.response.data.detail));
      } else {
        setError('Error al crear el cliente: ' + err.message);
      }
    }
  };

  const handleDelete = async (clienteId) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar al cliente ID ${clienteId}?`)) {
      return;
    }
    try {
      // --- 4. CORRECCIÓN: Añade la barra al final ---
      await axios.delete(`${API_URL}/clientes/${clienteId}/`);
      
      setClientes(clientes.filter(cliente => cliente.id !== clienteId));
    } catch (err) {
      setError('Error al eliminar el cliente: ' + err.message);
    }
  };


  return (
    <div>
      <h2>Clientes</h2>
      
      {error && (
        <div style={{ color: 'red' }}>
          {error}
          <button onClick={() => setError(null)} style={{ marginLeft: '10px' }}>Cerrar</button>
        </div>
      )}

      {/* --- FORMULARIO --- */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
        <h3>Nuevo Cliente</h3>
        <label>Nombre: </label>
        <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} required />
        <br />
        <label>Apellido: </label>
        <input type="text" name="apellido" value={formData.apellido} onChange={handleChange} required />
        <br />
        <label>DNI: </label>
        <input type="number" name="dni" value={formData.dni} onChange={handleChange} required />
        <br />
        <label>Dirección: </label>
        <input type="text" name="direccion" value={formData.direccion} onChange={handleChange} />
        <br />
        <label>Teléfono: </label>
        <input type="text" name="telefono" value={formData.telefono} onChange={handleChange} />
        <br />
        <br />
        <button type="submit">Guardar Cliente</button>
      </form>

      {/* --- TABLA --- */}
      <table border="1" style={{ width: '100%', marginTop: '20px' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellido</th>
            <th>DNI</th>
            <th>Teléfono</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {clientes.map(cliente => (
            <tr key={cliente.id}>
              <td>{cliente.id}</td>
              <td>{cliente.nombre}</td>
              <td>{cliente.apellido}</td>
              <td>{cliente.dni}</td>
              <td>{cliente.telefono}</td>
              <td>
                <button onClick={() => handleDelete(cliente.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PaginaCliente;