from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import schemas.factura as schemas_factura
import schemas.auth as schemas_auth
from services import facturas_service, auth_service

router = APIRouter(
    prefix="/facturas",
    tags=["Facturas"]
)

@router.post("/", response_model=schemas_factura.FacturaIdOut)
async def crear_factura(
    data: schemas_factura.FacturaCreate,
    current_user = Depends(auth_service.get_current_user) 
):
    return await facturas_service.create_factura(data, current_user)

@router.get("/", response_model=list[schemas_factura.FacturaConNombresOut])
async def listar_facturas(
    current_user = Depends(auth_service.get_current_user)
):
    return await facturas_service.get_facturas(current_user)

@router.post("/{factura_id}/items", status_code=201)
async def agregar_item_factura(
    factura_id: int,
    item: schemas_factura.DetalleCreate,
    user = Depends(auth_service.get_current_user)
):
    return await facturas_service.add_item_to_factura(factura_id, item)

@router.get("/{factura_id}/detalle", response_model=list[schemas_factura.DetalleFacturaItemOut])
async def detalle_factura(
    factura_id: int,
    user = Depends(auth_service.get_current_user)
):
    return await facturas_service.get_detalle_factura(factura_id)

@router.get("/reporte/ventas-por-cliente", response_model=list[schemas_factura.ReporteVentasClienteOut])
async def reporte_ventas_cliente(
    user = Depends(auth_service.get_current_user)
):
    if user['rol'] != 'admin':
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este reporte")
    return await facturas_service.get_reporte_ventas_cliente()

@router.get("/{factura_id}/pdf", summary="Generar PDF de una factura")
async def generar_factura_pdf(
    factura_id: int,
    current_user = Depends(auth_service.get_current_user)
):
    return await facturas_service.generate_factura_pdf(factura_id, current_user)