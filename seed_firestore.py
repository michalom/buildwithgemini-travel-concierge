import os
from google.cloud import firestore

# CRITICAL: Hardcoding the project ID as requested to avoid issues with Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-67102be14323"

def seed_database():
    print(f"Initializing Firestore client for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    
    collection_name = "hotels"
    print(f"Seeding '{collection_name}' collection...")
    
    seed_data = [
        {
            "id": "hotel-sf-1",
            "name": "Golden Gate Inn",
            "destination": "San Francisco",
            "price_per_night": 250,
            "amenities": ["Free WiFi", "Breakfast included", "Fitness center"],
            "rating": 4.5
        },
        {
            "id": "hotel-sf-2",
            "name": "Bay View Resort",
            "destination": "San Francisco",
            "price_per_night": 400,
            "amenities": ["Pool", "Spa", "Ocean view", "Valet parking"],
            "rating": 4.8
        },
        {
            "id": "hotel-ny-1",
            "name": "Manhattan Central",
            "destination": "New York",
            "price_per_night": 350,
            "amenities": ["Free WiFi", "Rooftop bar", "Room service"],
            "rating": 4.3
        },
        {
            "id": "hotel-ny-2",
            "name": "Brooklyn Boutique",
            "destination": "New York",
            "price_per_night": 200,
            "amenities": ["Bicycle rental", "Coffee shop", "Pet friendly"],
            "rating": 4.6
        }
    ]
    
    for item in seed_data:
        doc_ref = db.collection(collection_name).document(item["id"])
        doc_ref.set(item)
        print(f"Added document: {item['id']}")
        
    print("Database seeding complete!")

if __name__ == "__main__":
    seed_database()
