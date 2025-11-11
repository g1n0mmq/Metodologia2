const ClienteRow = ({ cliente, handleEdit, handleDelete }) => (
  <tr key={cliente.id}>
    <td>{cliente.id}</td>
    <td>{cliente.nombre}</td>
    <td>{cliente.apellido}</td>
    <td>{cliente.dni}</td>
    <td>{cliente.telefono}</td>
    <td>
      <button onClick={() => handleEdit(cliente)} className="btn btn-primary" style={{ marginRight: '5px' }}>
        Editar
      </button>
      <button onClick={() => handleDelete(cliente.id)} className="btn btn-danger">
        Eliminar
      </button>
    </td>
  </tr>
);

const ClienteTable = ({ clientes, handleEdit, handleDelete }) => (
    <table className="items-table" style={{marginTop: '20px'}}>
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
            <ClienteRow
              key={cliente.id}
              cliente={cliente}
              handleEdit={handleEdit}
              handleDelete={handleDelete}
            />
          ))}
        </tbody>
      </table>
);

export default ClienteTable;