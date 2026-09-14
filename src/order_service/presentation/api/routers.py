import uuid

from fastapi import APIRouter, Depends, HTTPException

from order_service.application.usecases.create_order import CreateOrderUseCase
from order_service.application.usecases.get_order import GetOrderUseCase
from order_service.domain.exceptions import ItemNotAvailableError, OrderNotFoundError
from order_service.presentation.api.dependencies import get_create_order_use_case, get_get_order_use_case
from order_service.presentation.api.schemas import CreateOrderRequest, order_to_response, OrderResponse

router = APIRouter()


@router.post("/orders", status_code=201, response_model=OrderResponse)
async def create_order(
        body: CreateOrderRequest,
        use_case: CreateOrderUseCase = Depends(get_create_order_use_case)
):
    dto = CreateOrderUseCase.OrderDTO(
        user_id=body.user_id,
        item_id=body.item_id,
        quantity=body.quantity,
        idempotency_key=body.idempotency_key
    )
    try:
        order = await use_case.execute(dto)
    except ItemNotAvailableError:
        raise HTTPException(status_code=400, detail="Item not available")
    return order_to_response(order)

@router.get("/orders/{order_id}", status_code=200, response_model=OrderResponse)
async def get_order_by_id(
        order_id: uuid.UUID,
        use_case: GetOrderUseCase = Depends(get_get_order_use_case)
):
    try:
        order = await use_case.execute(order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_to_response(order)

@router.get("/health")
def health():
    return {"status": "ok"}