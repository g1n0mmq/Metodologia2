import React, { useState, useEffect } from 'react';
import axios from 'axios'; 

const API_URL = 'http://127.0.0.1:8000';

// Un formulario vacío para resetear
const formularioVacio = {
  nombre: '',
  apellido: '',
  dni: '',
  direccion: '',
  telefono: ''
};

function PaginaCliente() {
  const [clientes, setClientes] = useState([]);
  const [error, setError] = useState(null);
  
  // --- 1. ESTADO DEL FORMULARIO ---
  // Sigue guardando los datos del formulario
  const [formData, setFormData] = useState(formularioVacio);

  // --- 2. NUEVO ESTADO: ID DE EDICIÓN ---
  // Si es 'null', estamos creando. Si es un número, estamos editando.
  const [editingId, setEditingId] = useState(null);

  // --- 3. FUNCIÓN PARA TRAER LOS DATOS (sin cambios) ---
  const fetchClientes = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };
      const response = await axios.get(`${API_URL}/clientes`, authHeaders);
      setClientes(response.data);
    } catch (err) {
      setError('Error al cargar los clientes: ' + err.message);
    }
  };

  useEffect(() => {
    fetchClientes();
  }, []);

  // --- 4. FUNCIÓN 'handleChange' (sin cambios) ---
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // --- 5. FUNCIÓN 'handleSubmit' (¡MODIFICADA!) ---
  // Ahora decide si crear (POST) o actualizar (PUT)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    const token = localStorage.getItem('authToken');
    const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

    try {
      if (editingId) {
        // --- LÓGICA DE ACTUALIZAR (PUT) ---
        // Usamos la ruta PUT /clientes/{id}/
        const response = await axios.put(`${API_URL}/clientes/${editingId}`, formData, authHeaders);
        
        // Actualizamos la lista de clientes en la pantalla
        setClientes(clientes.map(c => 
          c.id === editingId ? response.data : c
        ));
        setSuccessMessage(`Cliente ID ${editingId} actualizado con éxito.`);

      } else {
        // --- LÓGICA DE CREAR (POST) (sin cambios) ---
        const response = await axios.post(`${API_URL}/clientes`, formData, authHeaders);
        setClientes([...clientes, response.data]);
        setSuccessMessage(`Cliente "${response.data.nombre}" creado con éxito.`);
      }
      
      // Limpiamos el formulario y el ID de edición
      setFormData(formularioVacio);
      setEditingId(null);

    } catch (err) {
      const errorMsg = (err.response?.data?.detail) 
        ? JSON.stringify(err.response.data.detail) 
        : err.message;
      setError(`Error: ${errorMsg}`);
    }
  };

  // --- 6. NUEVA FUNCIÓN: Preparar para la edición ---
  // Se llama al hacer clic en el botón "Editar" de una fila
  const handleEdit = (cliente) => {
    // 1. Rellena el formulario con los datos del cliente
    setFormData({
      nombre: cliente.nombre,
      apellido: cliente.apellido,
      dni: cliente.dni,
      direccion: cliente.direccion || '', // Usa '' si es null
      telefono: cliente.telefono || ''   // Usa '' si es null
    });
    // 2. Guarda el ID del cliente que estamos editando
    setEditingId(cliente.id);
    // 3. (Opcional) Sube la vista al formulario
    window.scrollTo(0, 0); 
  };

  // --- 7. NUEVA FUNCIÓN: Cancelar la edición ---
  const cancelEdit = () => {
    setFormData(formularioVacio);
    setEditingId(null);
    setError(null);
  };

  // --- 8. FUNCIÓN 'handleDelete' (sin cambios) ---
  const handleDelete = async (clienteId) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar al cliente ID ${clienteId}?`)) {
      return;
    }
    try {
      const token = localStorage.getItem('authToken');
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };
      await axios.delete(`${API_URL}/clientes/${clienteId}`, authHeaders);
      setClientes(clientes.filter(cliente => cliente.id !== clienteId));
    } catch (err) {
      setError('Error al eliminar el cliente: ' + err.message);
    }
  };

  // --- (ESTADO DE ÉXITO, opcional pero útil) ---
  const [successMessage, setSuccessMessage] = useState(null);

  return (
    <div>
      <h2>Clientes</h2>
      
      {/* Mostramos el error si existe */}
      {error && (
        <div style={{ color: 'red' }}>
          {error}
          <button onClick={() => setError(null)} style={{ marginLeft: '10px' }}>Cerrar</button>
        </div>
      )}
      {/* Mostramos mensaje de éxito */}
      {successMessage && (
        <div style={{ color: 'green' }}>
          {successMessage}
          <button onClick={() => setSuccessMessage(null)} style={{ marginLeft: '10px' }}>Cerrar</button>
        </div>
      )}

      {/* --- FORMULARIO (ahora es de "Editar" o "Nuevo") --- */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
        
        {/* Título dinámico */}
        <h3>{editingId ? `Editando Cliente ID: ${editingId}` : 'Nuevo Cliente'}</h3>
        
        {/* ... (campos del formulario, sin cambios) ... */}
        <label>Nombre: </label>
        <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} required /><br />
        <label>Apellido: </label>
        <input type="text" name="apellido" value={formData.apellido} onChange={handleChange} required /><br />
        <label>DNI: </label>
        <input type="number" name="dni" value={formData.dni} onChange={handleChange} required /><br />
        <label>Dirección: </label>
        <input type="text" name="direccion" value={formData.direccion} onChange={handleChange} /><br />
        <label>Teléfono: </label>
        <input type="text" name="telefono" value={formData.telefono} onChange={handleChange} /><br />
        <br />

        {/* Botón de envío dinámico */}
        <button type="submit">
          {editingId ? 'Actualizar Cliente' : 'Guardar Cliente'}
        </button>
        
        {/* NUEVO BOTÓN: Cancelar edición */}
        {editingId && (
          <button type="button" onClick={cancelEdit} style={{ marginLeft: '10px' }}>
            Cancelar Edición
          </button>
        )}
      </form>

      {/* --- TABLA DE CLIENTES (con botón de editar) --- */}
      <table border="1" style={{ width: '100%', marginTop: '20px' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellido</th>
            <th>DNI   </th>
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
                {/* --- NUEVO BOTÓN DE EDITAR --- */}
                <button onClick={() => handleEdit(cliente)} style={{ marginRight: '5px' }}>
                  Editar
                </button>
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