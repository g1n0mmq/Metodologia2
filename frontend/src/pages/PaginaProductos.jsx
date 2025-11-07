import React, { useState, useEffect } from 'react';
// 1. Importamos axios
import axios from 'axios'; 

function PaginaProductos() {
  // 2. Creamos estados para 'productos' y 'error'
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState(null);

  // 3. Llamamos a la API cuando carga la página
  useEffect(() => {
    const fetchProductos = async () => {
      try {
        // 4. Hacemos GET a la API de /productos
        const response = await axios.get('http://127.0.0.1:8000/productos');
        setProductos(response.data);
      } catch (err) {
        setError('Error al cargar los productos: ' + err.message);
      }
    };

    fetchProductos();
  }, []);

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  // 5. Renderizamos la tabla de productos
  return (
    <div>
      <h2>Productos</h2>
      
      <button>Nuevo Producto</button>

      <table border="1" style={{ width: '100%', marginTop: '20px' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Descripción</th>
            <th>Stock</th>
            <th>Precio Venta</th>
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PaginaProductos;