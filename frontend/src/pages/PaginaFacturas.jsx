import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

function PaginaFacturas() {
  // estados para guardar los datos que vienen del backend
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [listaFacturas, setListaFacturas] = useState([]);
  
  // estados para manejar el formulario de nueva factura
  const [selectedClientId, setSelectedClientId] = useState('');
  const [cart, setCart] = useState([]);
  const [currentItemId, setCurrentItemId] = useState('');
  const [currentItemQty, setCurrentItemQty] = useState(1);

  // estados para mostrar mensajes de error, carga o exito
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // estado para el popup que muestra el detalle de la factura
  const [detalleVisible, setDetalleVisible] = useState({ visible: false, items: [], facturaId: null });

  // efecto que se ejecuta una vez para cargar los datos iniciales
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // agarra el token para poder hacer las peticiones
        const token = localStorage.getItem('authToken');
        if (!token) {
          setError('No estás autenticado. Por favor, inicia sesión.');
          return;
        }
        const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

        // pide los clientes, productos y facturas al backend
        const clientesRes = await axios.get(`${API_URL}/clientes/`, authHeaders);
        setClientes(clientesRes.data);
        
        const productosRes = await axios.get(`${API_URL}/productos/`, authHeaders);
        setProductos(productosRes.data);

        const facturasRes = await axios.get(`${API_URL}/facturas/`, authHeaders);
        setListaFacturas(facturasRes.data);
        
      } catch (err) {
        const errorMsg = err.response ? err.response.data.detail : err.message;
        setError('Error al cargar datos: ' + errorMsg);
      }
    };
    loadInitialData();
  }, []);

  // funcion para agregar un producto al carrito de la factura
  const handleAddItemToCart = () => {
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

    // revisa si el producto ya esta en el carrito para no duplicarlo
    const existingItemIndex = cart.findIndex(item => item.producto_id === productoId);

    if (existingItemIndex > -1) {
      // si ya existe, solo suma la cantidad
      const updatedCart = [...cart];
      updatedCart[existingItemIndex].cantidad += cantidad;
      setCart(updatedCart);
    } else {
      const newItem = {
        producto_id: producto.id,
        nombre: producto.nombre,
        cantidad: cantidad
      };
      setCart([...cart, newItem]);
    }

    // limpia los inputs
    setCurrentItemId('');
    setCurrentItemQty(1);
    setError(null);
  };

  // funcion para guardar la factura completa
  const handleSubmitInvoice = async (e) => {
    e.preventDefault();
    
    if (!selectedClientId || cart.length === 0) {
      setError('Debes seleccionar un cliente y añadir al menos un producto.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No estás autenticado. Por favor, inicia sesión.');
      }
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

      // primero, crea la factura para obtener un id
      const facturaData = { cliente_id: parseInt(selectedClientId) };
      const facturaRes = await axios.post(`${API_URL}/facturas/`, facturaData, authHeaders);
      
      const newFacturaId = facturaRes.data.factura_id;
      if (!newFacturaId) {
        throw new Error('No se pudo obtener el ID de la nueva factura.');
      }

      // despues, agrega cada producto del carrito a esa factura (FastAPI maneja bien sin / aquí)
      await Promise.all(
        cart.map(item =>
          axios.post(`${API_URL}/facturas/${newFacturaId}/items`, {
            producto_id: item.producto_id,
            cantidad: item.cantidad,
          }, authHeaders),
        ),
      );

      // si todo sale bien, muestra un mensaje y limpia el formulario
      setSuccessMessage(`¡Factura #${newFacturaId} creada con éxito!`);
      setLoading(false);
      setCart([]);
      setSelectedClientId('');
      window.location.reload();

    } catch (err) {
      setLoading(false);
      const errorMessage = err.response ? JSON.stringify(err.response.data.detail) : err.message;
      setError('Error al crear la factura: ' + errorMessage);
    }
  };

  // funcion para pedir el detalle de una factura y mostrarlo en el popup
  const handleViewDetails = async (facturaId) => {
    setError(null);
    try {
      const token = localStorage.getItem('authToken');
      const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.get(`${API_URL}/facturas/${facturaId}/detalle/`, authHeaders);
      
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

  // funcion para pedir el pdf de la factura al backend
  const handlePrintInvoice = async (facturaId) => {
    setError(null);
    try {
      const token = localStorage.getItem('authToken');
      const authHeaders = { 
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob', // le decimos a axios que la respuesta sera un archivo
      };

      const response = await axios.get(`${API_URL}/facturas/${facturaId}/pdf/`, authHeaders);

      // crea un objeto blob, que es como un archivo temporal en el navegador
      const file = new Blob(
        [response.data], 
        { type: 'application/pdf' }
      );
      
      // crea una url temporal para ese archivo
      const fileURL = URL.createObjectURL(file);
      
      // abre la url en una nueva pestaña para que el navegador muestre el pdf
      window.open(fileURL, '_blank');

    } catch (err) {
      let errorMsg = 'No se pudo generar el PDF. ';
      if (err.response && err.response.data instanceof Blob) {
        try {
          const errorText = await err.response.data.text();
          const errorJson = JSON.parse(errorText);
          errorMsg += errorJson.detail || 'Error del servidor.';
        } catch {
          errorMsg += 'No se pudo leer el detalle del error del servidor.';
        }
      } else {
        errorMsg += err.response?.data?.detail || err.message;
      }
      setError(errorMsg);
    }
  };

  // aqui empieza el html que se va a mostrar
  return (
    <div className="fade-in">
      <h2 className="section-title">Gestión de Facturas</h2>

      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}
      {detalleVisible.visible && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content">
            <span className="close" onClick={() => setDetalleVisible({ visible: false, items: [], facturaId: null })}>&times;</span>
            <h3 className="section-title">Detalle de la Factura #{detalleVisible.facturaId}</h3>
            <table className="items-table">
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
            <button onClick={() => handlePrintInvoice(detalleVisible.facturaId)} className="btn btn-success" style={{ marginTop: '20px' }}>
              Imprimir PDF
            </button>
          </div>
        </div>
      )}

      <div className="form-section">
        <form onSubmit={handleSubmitInvoice}>
          <div className="form-group">
            <label>1. Seleccionar Cliente</label>
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
          </div>

          <div className="form-group">
            <label>2. Agregar Productos</label>
            <div className="form-row-triple">
              <select value={currentItemId} onChange={(e) => setCurrentItemId(e.target.value)}>
                <option value="">-- Elige un producto --</option>
                {productos.map(prod => (
                  <option key={prod.id} value={prod.id}>
                    {prod.nombre} (Stock: {prod.stock})
                  </option>
                ))}
              </select>
              <input 
                type="number" 
                value={currentItemQty} 
                onChange={(e) => setCurrentItemQty(e.target.value)} 
                min="1"
                placeholder="Cantidad"
              />
              <button type="button" onClick={handleAddItemToCart} className="btn btn-primary">
                Añadir al Carrito
              </button>
            </div>
          </div>

          <h3>Carrito de la Factura</h3>
          <table className="items-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Cantidad</th>
              </tr>
            </thead>
            <tbody>
              {cart.map((item, index) => (
                <tr key={index}>
                  <td>{item.nombre}</td>
                  <td style={{ textAlign: 'center' }}>{item.cantidad}</td>
                </tr>
              ))}
              {cart.length === 0 && (
                <tr>
                  <td colSpan="2" style={{ textAlign: 'center' }}>El carrito está vacío</td>
                </tr>
              )}
            </tbody>
          </table>
          
          <button type="submit" disabled={loading} className="btn btn-success btn-full">
            {loading ? <span className="loading"></span> : 'Crear Factura'}
          </button>
        </form>
      </div>

      <hr style={{ margin: '40px 0' }} />

      {/* --- 5. AÑADE ESTA NUEVA TABLA AL FINAL --- */}
      <h3>Facturas Creadas</h3>
      <table className="items-table">
        <thead>
          <tr>
            <th>Factura ID</th>
            <th>Fecha</th>
            <th>Cliente</th>
            <th>Creado por (Usuario)</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {listaFacturas.map(factura => (
            <tr key={factura.id}>
              <td>{factura.id}</td>
              <td>
                {new Date(factura.fecha).toLocaleString('es-AR', {
                  year: 'numeric', month: '2-digit', day: '2-digit',
                  hour: '2-digit', minute: '2-digit', second: '2-digit'
                })}
              </td>
              <td>{factura.cliente_nombre} {factura.cliente_apellido}</td>
              <td>{factura.creador_username}</td>
              <td style={{ textAlign: 'center' }}>
                <button onClick={() => handleViewDetails(factura.id)} className="btn btn-primary" style={{marginRight: '5px'}}>Ver Detalle</button>
                <button onClick={() => handlePrintInvoice(factura.id)} className="btn btn-success">Imprimir</button>
              </td>
            </tr>
          ))}
          {listaFacturas.length === 0 && (
            <tr>
              <td colSpan="5" style={{ textAlign: 'center' }}>
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