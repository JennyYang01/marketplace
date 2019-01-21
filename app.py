from flask import Flask
import ast
import json

from config import marketplace_db
from flask import request, jsonify
from bson.json_util import dumps

app = Flask(__name__)


@app.route('/')
def get_initial_response():
    """Welcome message for the API."""

    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to the API'
    }

    # Make the message look good
    resp = jsonify(message)
    # Return the object
    return resp


products_collection = marketplace_db.products


@app.route('/api/v1/products/<product_id>', methods=['GET'])
def fetch_product(product_id):
    """
    Function to fetch one product by product_id.
    """
    try:
        # Find one product matching the product_id
        product_fetched = products_collection.find_one({"product_id": int(product_id)})

        # Check if product_fetched is not None
        if product_fetched:
            return dumps(product_fetched), 200
        else:
            # No records are found
            return "No records found", 404
    except:
        # Server internal error while trying to fetch the resource
        return "Server internal error", 500


@app.route('/api/v1/products', methods=['GET'])
def fetch_products():
    """
    Function to fetch all products.
    """
    try:
        available = request.args.get('available')

        if available:
            if available == '1' or available == 'T':
                # Fetch only the app with inventory_count greater than 0
                products_fetched = products_collection.find({"inventory_count": {"$gt": 0}})
            else:
                # Invalid argument
                return "Bad request, query string should be '?available=1' or " \
                       "'?available=T'", 400
        else:
            # Fetch all app
            products_fetched = products_collection.find({})

        if products_fetched.count() > 0:
            # Prepare the response
            return dumps(products_fetched), 200
        else:
            # No records are found
            return "No records found", 404
    except:
        # Server internal error while trying to fetch the resource
        return "Server internal error", 500


@app.route("/api/v1/products", methods=['POST'])
def create_products():
    """
    Function to create new products.
    """
    try:
        # Create new products
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            return "Bad request as request body is not available", 400

        record_created = products_collection.insert(body)

        if isinstance(record_created, list):
            # Prepare the response declaring success
            # Return list of Id of the newly created item
            return jsonify([str(v) for v in record_created]), 201
        else:
            # Return Id of the newly created item
            return jsonify(str(record_created)), 201
    except:
        # Server internal error while trying to fetch the resource
        return "Server internal error", 500


@app.route("/api/v1/products/<product_id>", methods=['PUT'])
def purchase_product(product_id):
    """
    Function to purchase products, decreasing inventory by 1.
    """
    try:
        # Get the value which needs to be updated
        purchasing_product = products_collection.find_one({"product_id": int(product_id)})

        if purchasing_product:
            # Find inventory count and decrease by one
            purchasing_product["inventory_count"] = purchasing_product["inventory_count"] - 1

            # Update product
            product_updated = \
                products_collection.update({"product_id": int(product_id)}, {"$set":purchasing_product}, upsert = False)

            if product_updated.modified_count > 0:
                # Prepare the response declaring success
                return "Resource successfully updated", 200
            else:
                # No records were found
                return "No records updated", 404
        else:
            # Bad request, there is no such product
            return "Bad request, there is no such product", 400
    except:
        # Server internal error while trying to fetch the resource
        return "Server internal error", 500


if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
