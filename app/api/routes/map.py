# app/api/routes/map.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Amenity
from app.schemas.schemas import RouteRecommendRequest, RouteRecommendResponse


router = APIRouter()

@router.post("/api/route/recommend")
def get_navigation_route(route_request: RouteRecommendRequest, request: Request, db: Session = Depends(get_db)):
    # 1. Fetch the live data from the SQL database
    live_amenities = db.query(Amenity).all()
    
    # 2. Get the graph service from the app state
    map_service = request.app.state.map_service
    
    # 3. Inject the live data into the graph
    map_service.update_amenity_data(live_amenities)
    
    # 4. Calculate the path using the freshly updated graph
    try:
        results = map_service.get_recommendations(route_request.user_node, route_request.amenity_type)
        results.sort(key=lambda x: x.total_seconds)
        return RouteRecommendResponse(recommendations=results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))