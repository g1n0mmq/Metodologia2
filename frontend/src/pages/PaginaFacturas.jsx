import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

function PaginaFacturas() {
  // --- 1. ESTADOS DE DATOS ---
  // Listas completas de clientes y productos para los <select>
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);

  // --- 1. AÑADE ESTE NUEVO ESTADO ---
  // Guardará la lista de facturas creadas
  const [listaFacturas, setListaFacturas] = useState([]);
  
  // --- 2. ESTADOS DEL FORMULARIO ---
  // El cliente que el usuario seleccionó
  const [selectedClientId, setSelectedClientId] = useState('');
  // El "carrito" de items antes de guardar la factura
  const [cart, setCart] = useState([]); // Será una lista: [{ producto_id: 1, nombre: 'Laptop', cantidad: 1 }]
  
  // --- 3. ESTADOS PARA AÑADIR UN ITEM ---
  // El producto que el usuario está a punto de añadir
  const [currentItemId, setCurrentItemId] = useState('');
  // La cantidad que está a punto de añadir
  const [currentItemQty, setCurrentItemQty] = useState(1);

  // --- 4. ESTADOS DE UI (User Interface) ---
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // --- NUEVO ESTADO PARA VER DETALLES ---
  // Guardará los items de la factura seleccionada y controlará la visibilidad del modal
  const [detalleVisible, setDetalleVisible] = useState({ visible: false, items: [], facturaId: null });

  // --- 5. EFECTO: Cargar clientes y productos al inicio ---
  // Trae los datos para llenar los menús desplegables
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Obtenemos el token
        const token = localStorage.getItem('authToken');
        if (!token) {
          setError('No estás autenticado. Por favor, inicia sesión.');
          return;
        }
        const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

        // Trae clientes (como antes)
        const clientesRes = await axios.get(`${API_URL}/clientes`, authHeaders);
        setClientes(clientesRes.data);
        
        // Trae productos (como antes)
        const productosRes = await axios.get(`${API_URL}/productos`, authHeaders);
        setProductos(productosRes.data);

        // --- 3. AÑADE ESTA LLAMADA ---
        // Trae la lista de facturas
        const facturasRes = await axios.get(`${API_URL}/facturas`, authHeaders);
        setListaFacturas(facturasRes.data);
        
      } catch (err) {
        const errorMsg = err.response ? err.response.data.detail : err.message;
        setError('Error al cargar datos: ' + errorMsg);
      }
    };
    loadInitialData();
  }, []); // El [] vacío hace que solo se ejecute una vez

  // --- 6. FUNCIÓN: Añadir un item al carrito ---
  const handleAddItemToCart = () => {
    // Validaciones
    const productoId = parseInt(currentItemId);
    const cantidad = parseInt(currentItemQty);

    if (!productoId || cantidad <= 0) {
      setError('Por favor, selecciona un producto y una cantidad válida.');
      return;
    }
    const producto = productos.find(p => p.id === productoId);
    if (!producto) {
      setError('Producto no encontrado.');
      return;
    }

    // --- LÓGICA MEJORADA: NO DUPLICAR PRODUCTOS ---
    const existingItemIndex = cart.findIndex(item => item.producto_id === productoId);

    if (existingItemIndex > -1) {
      // Si el producto ya existe, actualiza la cantidad
      const updatedCart = [...cart];
      updatedCart[existingItemIndex].cantidad += cantidad;
      setCart(updatedCart);
    } else {
      // Si es un producto nuevo, lo añade al carrito
      const newItem = {
        producto_id: producto.id,
        nombre: producto.nombre,
        cantidad: cantidad
      };
      setCart([...cart, newItem]);
    }

    // Limpia los campos de selección de item
    setCurrentItemId('');
    setCurrentItemQty(1);
    setError(null);
  };

  // --- 7. FUNCIÓN PRINCIPAL: Guardar la factura (POST) ---
  const handleSubmitInvoice = async (e) => {
    e.preventDefault(); // Evita que el formulario recargue la página
    
    // Validaciones
    if (!selectedClientId || cart.length === 0) {
      setError('Debes seleccionar un cliente y añadir al menos un producto.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      // --- PASO 0: Obtener el token de autenticación ---
      const token = localStorage.getItem('authToken'); // O de donde lo estés guardando
      if (!token) {
        throw new Error('No estás autenticado. Por favor, inicia sesión.');
      }

      // Configura las cabeceras para enviar el token
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

      // --- PASO A: Crear la cabecera de la factura ---
      const facturaRes = await axios.post(`${API_URL}/facturas`, {
        cliente_id: parseInt(selectedClientId)
      }, authHeaders); // <-- ¡Enviamos las cabeceras aquí!
      
      const newFacturaId = facturaRes.data.factura_id;
      if (!newFacturaId) {
        throw new Error('No se pudo obtener el ID de la nueva factura.');
      }

      // --- PASO B: Añadir cada item del carrito a la factura ---
      // Usamos Promise.all para enviar todas las peticiones de items
      await Promise.all(
        cart.map(item => {
          return axios.post(`${API_URL}/facturas/${newFacturaId}/items`, {
            producto_id: item.producto_id,
            cantidad: item.cantidad,
            // Nota: No es necesario enviar el token aquí si la ruta de items no está protegida
          });
        })
      );

      // --- ÉXITO ---
      setSuccessMessage(`¡Factura #${newFacturaId} creada con éxito!`);
      setLoading(false);
      // Limpiamos el formulario
      setCart([]);
      setSelectedClientId('');
      // Recargamos la página para ver la nueva factura en la lista
      window.location.reload();

    } catch (err) {
      setLoading(false);
      const errorMessage = err.response ? JSON.stringify(err.response.data.detail) : err.message;
      setError('Error al crear la factura: ' + errorMessage);
    }
  };

  // --- NUEVA FUNCIÓN: VER DETALLE DE FACTURA ---
  const handleViewDetails = async (facturaId) => {
    setError(null);
    try {
      const token = localStorage.getItem('authToken');
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.get(`${API_URL}/facturas/${facturaId}/detalle`, authHeaders);
      
      setDetalleVisible({
        visible: true,
        items: response.data,
        facturaId: facturaId
      });

    } catch (err) {
      const errorMsg = err.response ? JSON.stringify(err.response.data.detail) : err.message;
      setError(`Error al cargar el detalle de la factura: ${errorMsg}`);
    }
  };


  // --- 8. RENDERIZADO (HTML) ---
  return (
    <div>
      <h2>Nueva Factura</h2>

      {error && <div style={{ color: 'red', border: '1px solid red', padding: '10px', margin: '10px 0' }}>{error}</div>}
      {successMessage && <div style={{ color: 'green', border: '1px solid green', padding: '10px', margin: '10px 0' }}>{successMessage}</div>}

      {/* --- MODAL PARA VER DETALLES --- */}
      {detalleVisible.visible && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '5px', width: '600px' }}>
            <h3>Detalle de la Factura #{detalleVisible.facturaId}</h3>
            <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Precio Unit.</th>
                  <th>Importe</th>
                </tr>
              </thead>
              <tbody>
                {detalleVisible.items.map(item => (
                  <tr key={item.producto_id}>
                    <td>{item.nombre}</td>
                    <td style={{ textAlign: 'center' }}>{item.cantidad}</td>
                    <td style={{ textAlign: 'right' }}>${parseFloat(item.precio).toFixed(2)}</td>
                    <td style={{ textAlign: 'right' }}>${parseFloat(item.importe).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button onClick={() => setDetalleVisible({ visible: false, items: [], facturaId: null })} style={{ marginTop: '20px' }}>Cerrar</button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmitInvoice}>
        
        <fieldset style={{ marginBottom: '20px' }}>
          <legend>1. Seleccionar Cliente</legend>
          <select 
            value={selectedClientId} 
            onChange={(e) => setSelectedClientId(e.target.value)}
            required
          >
            <option value="">-- Elige un cliente --</option>
            {clientes.map(cliente => (
              <option key={cliente.id} value={cliente.id}>
                {cliente.nombre} {cliente.apellido} (DNI: {cliente.dni})
              </option>
            ))}
          </select>
        </fieldset>

        <fieldset style={{ marginBottom: '20px' }}>
          <legend>2. Agregar Productos</legend>
          <div>
            <label>Producto: </label>
            <select value={currentItemId} onChange={(e) => setCurrentItemId(e.target.value)}>
              <option value="">-- Elige un producto --</option>
              {productos.map(prod => (
                <option key={prod.id} value={prod.id}>
                  {prod.nombre} (Stock: {prod.stock})
                </option>
              ))}
            </select>
            
            <label style={{ marginLeft: '10px' }}>Cantidad: </label>
            <input 
              type="number" 
              value={currentItemQty} 
              onChange={(e) => setCurrentItemQty(e.target.value)} 
              min="1"
              style={{ width: '60px' }}
            />
            
            <button type="button" onClick={handleAddItemToCart} style={{ marginLeft: '10px' }}>
              Añadir al Carrito
            </button>
          </div>
        </fieldset>

        <h3>Carrito de la Factura</h3>
        <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{padding: '8px'}}>Producto</th>
              <th style={{padding: '8px'}}>Cantidad</th>
            </tr>
          </thead>
          <tbody>
            {cart.map((item, index) => (
              <tr key={index}>
                <td style={{padding: '8px'}}>{item.nombre}</td>
                <td style={{padding: '8px', textAlign: 'center'}}>{item.cantidad}</td>
              </tr>
            ))}
            {cart.length === 0 && (
              <tr>
                <td colSpan="2" style={{padding: '8px', textAlign: 'center'}}>El carrito está vacío</td>
              </tr>
            )}
          </tbody>
        </table>
        
        <button 
          type="submit" 
          disabled={loading}
          style={{ marginTop: '20px', fontSize: '1.2em', padding: '10px' }}
        >
          {loading ? 'Guardando...' : 'Crear Factura'}
        </button>
      </form>

      <hr style={{ margin: '40px 0' }} />

      {/* --- 5. AÑADE ESTA NUEVA TABLA AL FINAL --- */}
      <h2>Facturas Creadas</h2>
      <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{padding: '8px'}}>Factura ID</th>
            <th style={{padding: '8px'}}>Fecha</th>
            <th style={{padding: '8px'}}>Cliente</th>
            <th style={{padding: '8px'}}>Creado por (Usuario)</th>
            <th style={{padding: '8px'}}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {listaFacturas.map(factura => (
            <tr key={factura.id}>
              <td style={{padding: '8px'}}>{factura.id}</td>
              <td style={{padding: '8px'}}>{new Date(factura.fecha).toLocaleString()}</td>
              <td style={{padding: '8px'}}>{factura.cliente_nombre} {factura.cliente_apellido}</td>
              <td style={{padding: '8px'}}>{factura.creador_username}</td>
              <td style={{padding: '8px', textAlign: 'center'}}>
                <button onClick={() => handleViewDetails(factura.id)}>Ver Detalle</button>
              </td>
            </tr>
          ))}
          {listaFacturas.length === 0 && (
            <tr>
              <td colSpan="5" style={{padding: '8px', textAlign: 'center'}}>
                No se encontraron facturas.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default PaginaFacturas;