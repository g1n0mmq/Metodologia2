import React, { useState, useEffect } from 'react';
import axios from 'axios'; 

const API_URL = 'http://127.0.0.1:8000';

// Un formulario vacío para resetear
const formularioVacio = {
  nombre: '',
  descripcion: '',
  stock: 0,
  precio_compra: 0.0,
  precio_venta: 0.0
};

function PaginaProductos() {
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState(null);
  
  // Estado para el formulario (adaptado a Producto)
  const [formData, setFormData] = useState(formularioVacio);

  // Estado para saber si estamos editando
  const [editingId, setEditingId] = useState(null);

  // --- 1. FUNCIÓN PARA TRAER LOS DATOS ---
  const fetchProductos = async () => {
    try {
      // Usamos el token, ya que esta ruta debería ser segura
      const token = localStorage.getItem('authToken');
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };
      
      const response = await axios.get(`${API_URL}/productos`, authHeaders);
      setProductos(response.data);
    } catch (err) {
      setError('Error al cargar los productos: ' + err.message);
    }
  };

  useEffect(() => {
    fetchProductos();
  }, []);

  // --- 2. FUNCIÓN 'handleChange' (Maneja cambios en el formulario) ---
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // --- 3. FUNCIÓN 'handleSubmit' (Decide si Crear o Actualizar) ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    const token = localStorage.getItem('authToken');
    const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

    // Convertimos los precios y stock a números
    const dataParaAPI = {
      ...formData,
      stock: parseInt(formData.stock),
      precio_compra: parseFloat(formData.precio_compra),
      precio_venta: parseFloat(formData.precio_venta)
    };

    try {
      if (editingId) {
        // --- LÓGICA DE ACTUALIZAR (PUT) ---
        const response = await axios.put(`${API_URL}/productos/${editingId}`, dataParaAPI, authHeaders);
        setProductos(productos.map(p => 
          p.id === editingId ? response.data : p
        ));
      } else {
        // --- LÓGICA DE CREAR (POST) ---
        const response = await axios.post(`${API_URL}/productos`, dataParaAPI, authHeaders);
        setProductos([...productos, response.data]);
      }
      
      setFormData(formularioVacio);
      setEditingId(null);

    } catch (err) {
      const errorMsg = (err.response?.data?.detail) 
        ? JSON.stringify(err.response.data.detail) 
        : err.message;
      setError(`Error al guardar el producto: ${errorMsg}`);
    }
  };

  // --- 4. FUNCIÓN: Preparar para la edición ---
  const handleEdit = (producto) => {
    setFormData({
      nombre: producto.nombre,
      descripcion: producto.descripcion,
      stock: producto.stock,
      precio_compra: producto.precio_compra,
      precio_venta: producto.precio_venta
    });
    setEditingId(producto.id);
    window.scrollTo(0, 0); 
  };

  // --- 5. FUNCIÓN: Cancelar la edición ---
  const cancelEdit = () => {
    setFormData(formularioVacio);
    setEditingId(null);
    setError(null);
  };

  // --- 6. FUNCIÓN 'handleDelete' (Adaptada para Productos) ---
  const handleDelete = async (productoId) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar el producto ID ${productoId}?`)) {
      return;
    }
    try {
      const token = localStorage.getItem('authToken');
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };
      
      // Asegúrate que la ruta DELETE NO tenga la barra al final
      await axios.delete(`${API_URL}/productos/${productoId}`, authHeaders);
      
      setProductos(productos.filter(p => p.id !== productoId));
    } catch (err) {
      setError('Error al eliminar el producto: ' + err.message);
    }
  };

  return (
    <div>
      <h2>Productos</h2>
      
      {error && (
        <div style={{ color: 'red' }}>
          {error}
          <button onClick={() => setError(null)} style={{ marginLeft: '10px' }}>Cerrar</button>
        </div>
      )}

      {/* --- FORMULARIO (Crear y Editar) --- */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
        <h3>{editingId ? `Editando Producto ID: ${editingId}` : 'Nuevo Producto'}</h3>
        
        <label>Nombre: </label>
        <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} required /><br />
        
        <label>Descripción: </label>
        <input type="text" name="descripcion" value={formData.descripcion} onChange={handleChange} required /><br />
        
        <label>Stock: </label>
        <input type="number" name="stock" value={formData.stock} onChange={handleChange} required /><br />
        
        <label>Precio Compra: </label>
        <input type="number" step="0.01" name="precio_compra" value={formData.precio_compra} onChange={handleChange} required /><br />
        
        <label>Precio Venta: </label>
        <input type="number" step="0.01" name="precio_venta" value={formData.precio_venta} onChange={handleChange} required /><br />
        <br />

        <button type="submit">
          {editingId ? 'Actualizar Producto' : 'Guardar Producto'}
        </button>
        
        {editingId && (
          <button type="button" onClick={cancelEdit} style={{ marginLeft: '10px' }}>
            Cancelar Edición
          </button>
        )}
      </form>

      {/* --- TABLA DE PRODUCTOS (con botones) --- */}
      <table border="1" style={{ width: '100%', marginTop: '20px' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Descripción</th>
            <th>Stock</th>
            <th>Precio Venta</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {productos.map(producto => (
            <tr key={producto.id}>
              <td>{producto.id}</td>
              <td>{producto.nombre}</td>
              <td>{producto.descripcion}</td>
              <td>{producto.stock}</td>
              <td>{producto.precio_venta}</td>
              <td>
                <button onClick={() => handleEdit(producto)} style={{ marginRight: '5px' }}>
                  Editar
                </button>
                <button onClick={() => handleDelete(producto.id)}>
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

export default PaginaProductos;