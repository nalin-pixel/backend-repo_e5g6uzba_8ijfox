"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Ice cream shop specific schemas

class Icecream(BaseModel):
    """
    Ice cream flavors
    Collection name: "icecream"
    """
    name: str = Field(..., description="Flavor name")
    description: Optional[str] = Field(None, description="Short flavor description")
    price: float = Field(..., ge=0, description="Price per scoop")
    tags: List[str] = Field(default_factory=list, description="Labels for filtering")
    image: Optional[str] = Field(None, description="Image URL")
    is_available: bool = Field(True, description="Is this flavor available today")

class OrderItem(BaseModel):
    flavor_id: str = Field(..., description="Referenced flavor _id as string")
    name: str = Field(..., description="Flavor name snapshot")
    scoops: int = Field(..., ge=1, le=5, description="Number of scoops")
    price: float = Field(..., ge=0, description="Unit price captured at order time")

class Order(BaseModel):
    """
    Orders collection
    Collection name: "order"
    """
    customer_name: str = Field(..., description="Customer full name")
    customer_phone: str = Field(..., description="Contact phone")
    items: List[OrderItem] = Field(..., description="Items in the order")
    total: float = Field(..., ge=0, description="Computed order total")
    notes: Optional[str] = Field(None, description="Special instructions")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
