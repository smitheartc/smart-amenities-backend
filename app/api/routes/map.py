from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/route")
def get_route(request: Request, start: str, end: str):
    # Retrieve the service from the app state
    map_service = request.app.state.map_service
    
    if not map_service:
        raise HTTPException(status_code=503, detail="Map service unavailable")
        
    result = map_service.get_shortest_path(start, end)
    return result