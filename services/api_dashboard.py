from flask import Flask, session, redirect, url_for
from sqlalchemy import desc
from app import db
from models import User, Items, ItemImages, SavedItems

def get_dashboard(user_id):
    # Check user is logged in
    user = db.session.get(User, user_id)
    if not user:
        return False, "Not logged in"
    try:
        # Get items not sold
        not_sold = Items.query.filter_by(is_sold=False, seller_id=user_id, is_approved=True).order_by(desc(Items.created_at)).all()
        selling_listings = []
        for item in not_sold:
            first_image = ItemImages.query.filter_by(item_id=item.item_id).first()
            image_id = first_image.image_id if first_image else None
            selling_listings.append({
                "item_id": item.item_id,
                "title": item.title,
                "price": float(item.price),
                "condition": item.item_condition,
                "created_at": item.created_at.isoformat(),
                "image_id": image_id
            })

        # Get items sold
        sold = Items.query.filter_by(is_sold=True, seller_id=user_id, is_approved=True).order_by(desc(Items.created_at)).all()
        sold_items = []
        for item in sold:
            first_image = ItemImages.query.filter_by(item_id=item.item_id).first()
            image_id = first_image.image_id if first_image else None
            sold_items.append({
                "item_id": item.item_id,
                "title": item.title,
                "price": float(item.price),
                "condition": item.item_condition,
                "created_at": item.created_at.isoformat(),
                "image_id": image_id
            })

        # ✅ Get saved items (fix: query Items, not SavedItems)
        saved = db.session.query(Items).join(SavedItems, Items.item_id == SavedItems.item_id) \
            .filter(SavedItems.user_id == user_id) \
            .order_by(desc(Items.created_at)).all()

        saved_items = []
        for item in saved:
            first_image = ItemImages.query.filter_by(item_id=item.item_id).first()
            image_id = first_image.image_id if first_image else None
            saved_items.append({
                "item_id": item.item_id,
                "title": item.title,
                "price": float(item.price),
                "condition": item.item_condition,
                "created_at": item.created_at.isoformat(),
                "image_id": image_id
            })

        return True, (selling_listings, sold_items, saved_items)

    except Exception as e:
        return False, str(e)
