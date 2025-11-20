import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Icecream, Order, OrderItem

app = FastAPI(title="Ice Cream Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Helpers ---------
class ObjectIdEncoder:
    @staticmethod
    def encode(doc):
        if isinstance(doc, list):
            return [ObjectIdEncoder.encode(d) for d in doc]
        if isinstance(doc, dict):
            new_doc = {}
            for k, v in doc.items():
                if isinstance(v, ObjectId):
                    new_doc[k] = str(v)
                elif isinstance(v, list) or isinstance(v, dict):
                    new_doc[k] = ObjectIdEncoder.encode(v)
                else:
                    new_doc[k] = v
            return new_doc
        return doc


# -------- Root & Health ---------
@app.get("/")
def read_root():
    return {"message": "Ice Cream Shop Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# -------- Animation config from backend ("low-level animation in backend") ---------
class AnimationConfig(BaseModel):
    hero: dict
    card: dict
    button: dict


@app.get("/api/animation", response_model=AnimationConfig)
def get_animation_config():
    return AnimationConfig(
        hero={
            "initial": {"opacity": 0, "y": 20},
            "animate": {"opacity": 1, "y": 0},
            "transition": {"duration": 0.8, "ease": [0.22, 1, 0.36, 1]}
        },
        card={
            "whileHover": {"scale": 1.02},
            "whileTap": {"scale": 0.98},
            "transition": {"type": "spring", "stiffness": 300, "damping": 20}
        },
        button={
            "whileHover": {"y": -1},
            "whileTap": {"y": 0},
            "transition": {"duration": 0.15}
        }
    )


# -------- Ice cream flavors ---------
@app.get("/api/flavors")
def get_flavors():
    docs = get_documents("icecream")
    return ObjectIdEncoder.encode(docs)


class SeedResponse(BaseModel):
    inserted: int


@app.post("/api/flavors/seed", response_model=SeedResponse)
def seed_flavors():
    existing = db["icecream"].count_documents({}) if db else 0
    if existing > 0:
        return SeedResponse(inserted=0)

    seed = [
        {
            "name": "Vanilla Bean",
            "description": "Classic Madagascar vanilla with real bean specks",
            "price": 3.5,
            "tags": ["classic", "creamy"],
            "image": "https://images.unsplash.com/photo-1563805042-7684c019e1cb",
            "is_available": True,
        },
        {
            "name": "Dark Chocolate",
            "description": "70% cocoa, rich and indulgent",
            "price": 3.75,
            "tags": ["chocolate", "rich"],
            "image": "https://images.unsplash.com/photo-1551024601-bec78aea704b",
            "is_available": True,
        },
        {
            "name": "Strawberry Swirl",
            "description": "Fresh strawberries and ribbons of jam",
            "price": 3.75,
            "tags": ["fruit", "fresh"],
            "image": "https://images.unsplash.com/photo-1497051788611-2c64812349b4",
            "is_available": True,
        },
        {
            "name": "Mint Choco Chip",
            "description": "Cool mint with dark chocolate chunks",
            "price": 3.75,
            "tags": ["mint", "choco"],
            "image": "https://images.unsplash.com/photo-1625944528146-0f4fee2f8559",
            "is_available": True,
        },
    ]

    inserted = 0
    for doc in seed:
        create_document("icecream", doc)
        inserted += 1
    return SeedResponse(inserted=inserted)


# -------- Orders ---------
class CreateOrder(BaseModel):
    customer_name: str
    customer_phone: str
    items: List[OrderItem]
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    total: float


@app.post("/api/orders", response_model=OrderResponse)
def create_order_endpoint(payload: CreateOrder):
    total = sum(item.price * item.scoops for item in payload.items)
    order_doc = Order(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        items=payload.items,
        total=total,
        notes=payload.notes,
    )
    oid = create_document("order", order_doc)
    return OrderResponse(order_id=oid, total=total)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
