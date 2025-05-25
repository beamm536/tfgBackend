# en este archivo vamos a crear nuestro servidor FastAPI

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
import os
from dotenv import load_dotenv

#cargar las variables de entorno desde el archivo .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

#creamos una instancia de FastAPI
app = FastAPI()

#configuramos CORS para permitir solicitudes desde el frontend (desde mi Android)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las direcciones IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#ruta principal para obtener los lugares cercanos - las recomendaciones
@app.get("/recommendations")
def get_recommendations(
    lat: float = Query(..., description="Latitud del usuario"),
    lng: float = Query(..., description="Longitud del usuario"),
    type: Optional[str] = Query("tourist_attraction", description="Tipo de lugar a buscar"),
):

    """
    Obtener recomendaciones de lugares cercanos a la ubicación del usuario.
    :param lat: Latitud del usuario.
    :param lng: Longitud del usuario.
    :param type: Tipo de lugar a buscar (por defecto "tourist_attraction").
    :return: Lista de lugares recomendados.
    """
    # URL de la API de Google Places
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": f"{lat},{lng}",
        "radius": 10000,  #radio de búsqueda en metros
        "type": type,
        "key": GOOGLE_API_KEY,
    }
    
    #peticion a google places
    response = requests.get(url, params=params)
    data = response.json()
    
    #respuesta que vamos a recibir desde mi app-android
    recommendations = []
    for place in data.get("results", []):
        recommendations.append({
            "placeId": place.get("place_id"),
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating"),
            "reviews": place.get("user_ratings_total"),
            "address": place.get("vicinity"),
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"],
            "categories": place.get("types", []),
            "photoUrl": get_photo_url(place),
        })
        
    return {"recommendations": recommendations}


#nuevo endpoint para los detalles de las recomendaciones - GOOGLE PLACES DETAILS
@app.get("/place-details")
def get_place_details(place_id: str):
    """
    Obtener detalles de un lugar específico.
    :param place_id: ID del lugar.
    :return: Detalles del lugar.
    """
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,photos,rating,editorial_summary,website,url",
        "key": GOOGLE_API_KEY,
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    result = data.get("result", {})
    
  
    return{
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "rating": result.get("rating"),
        "summary": result.get("editorial_summary", {}).get("overview", ""),
        "website": result.get("website"),
        "url": result.get("url"),
        "photoUrl": get_photo_url(result),
    }
  
  
#funcion para la obtencion de la foto
def get_photo_url(place):
    """
    Obtener la URL de la foto del lugar.
    :param place: Objeto del lugar.
    :return: URL de la foto del lugar.
    """
    photos = place.get("photos")
    if photos and len(photos) > 0:
        ref = photos[0]["photo_reference"]
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={ref}&key={GOOGLE_API_KEY}"
    return None