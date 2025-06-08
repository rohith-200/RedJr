from flask import Flask, Blueprint, render_template, jsonify, request, session, url_for
from app import app, db
from models import Categories, Items, ItemImages
# need to remove this for flask import session to work
#from pip._internal.network import session
from sqlalchemy import case, or_

searchbp = Blueprint('search', __name__)

@searchbp.route('/search', methods=['GET', 'POST'])
def search():
    print(f"URL for search_results: {url_for('search.search_results')}")
    return render_template('search.html')

@searchbp.route('/search_results', methods=['POST'])
def search_results():
    cat_name = request.form['category']
    query = request.form['query'].strip()
    if cat_name == 'All':
        items = Items.query.filter_by(is_sold=False, is_approved=True)
    else:
        category = Categories.query.filter_by(category_name=cat_name).first()
        items = Items.query.filter_by(category_id=category.category_id, is_sold=False, is_approved=True)

    if not query == '':
        query_split = query.split()
        if len(query_split) > 2:
            rank_case = case (
                *[
                    (Items.title.ilike(f'%{query}%'), 1),
                    (Items.title.ilike(f'%{query_split[0]} {query_split[1]} {query_split[2]}%'), 2),
                    (Items.title.ilike(f'%{query_split[0]} {query_split[1]}%'), 3),
                    (Items.title.ilike(f'%{query_split[0]}%'), 4)
                ]
            )

            filters = or_ (
                Items.title.ilike(f'%{query}%'),
                Items.title.ilike(f'%{query_split[0]} {query_split[1]} {query_split[2]}%'),
                Items.title.ilike(f'%{query_split[0]} {query_split[1]}%'),
                Items.title.ilike(f'%{query_split[0]}%')
            )
        else:
            rank_case = case(
                *[
                    (Items.title.ilike(f'%{query}%'), 1),
                    (Items.title.ilike(f'%{query_split[0]}%'), 2)
                ]
            )

            filters = or_(
                Items.title.ilike(f'%{query}%'),
                Items.title.ilike(f'%{query_split[0]}%')
            )
        items = items.filter(filters).order_by(rank_case)

    items = items.all()

    images_map = {}
    for item in items:
        images = ItemImages.query.with_entities(ItemImages.image_id).filter_by(item_id=item.item_id).all()
        images_map[item.item_id] = [img.image_id for img in images]

    items_dict = [{
        'item_id': item.item_id,
        'title': item.title,
        'price': float(item.price),
        'created_at': item.created_at.isoformat() if item.created_at else '',
        'image_url': url_for('image', image_id=images_map[item.item_id][0]) if images_map.get(item.item_id) else None
    } for item in items]

    session['items'] = items_dict


    return render_template('search_results.html', category_name=cat_name, items = items , images_map=images_map, query=query, items_dict=items_dict)



@searchbp.route('/api/search')
def api_search():
    category = request.args.get('category', 'All')
    query = request.args.get('query', '').strip()

    items_query = Items.query

    # Filter by category if it's not 'All'
    if category != 'All':
        category_obj = Categories.query.filter_by(category_name=category).first()
        if category_obj:
            items_query = items_query.filter_by(category_id=category_obj.category_id)
        else:
            return jsonify({'results': [], 'message': 'Category not found'})

    # Add ranking and filtering logic if query is not empty
    if query:
        query_split = query.split()

        if len(query_split) > 2:
            rank_case = case(
                (Items.title.ilike(f'%{query}%'), 1),
                (Items.title.ilike(f'%{query_split[0]} {query_split[1]} {query_split[2]}%'), 2),
                (Items.title.ilike(f'%{query_split[0]} {query_split[1]}%'), 3),
                (Items.title.ilike(f'%{query_split[0]}%'), 4),
                else_=5
            )

            filters = or_(
                Items.title.ilike(f'%{query}%'),
                Items.title.ilike(f'%{query_split[0]} {query_split[1]} {query_split[2]}%'),
                Items.title.ilike(f'%{query_split[0]} {query_split[1]}%'),
                Items.title.ilike(f'%{query_split[0]}%')
            )
        else:
            rank_case = case(
                (Items.title.ilike(f'%{query}%'), 1),
                (Items.title.ilike(f'%{query_split[0]}%'), 2),
                else_=3
            )

            filters = or_(
                Items.title.ilike(f'%{query}%'),
                Items.title.ilike(f'%{query_split[0]}%')
            )

        items_query = items_query.filter(filters).order_by(rank_case)

    items = items_query.all()

    # Create response data
    response = []
    for item in items:
        image_ids = [img.image_id for img in ItemImages.query.with_entities(ItemImages.image_id).filter_by(item_id=item.item_id).all()]
        response.append({
            'id': item.item_id,
            'title': item.title,
            'price': float(item.price),
            'condition': item.item_condition,
            'image_ids': image_ids
        })

    return jsonify({
        'category': category,
        'query': query,
        'results': response
    })