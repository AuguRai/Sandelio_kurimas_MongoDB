from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
import uuid

def create_app():
    app = Flask(__name__)
    client = MongoClient("mongodb://localhost:27017/")
    db = client['warehouse']
    products_collection = db['products']
    warehouses_collection = db['warehouses']
    

    # Registruoti produktą
    @app.route('/products', methods=['PUT'])
    def put_product():
        data = request.get_json()
        name = data.get('name')
        id = data.get('id', str(uuid.uuid4()))
        category = data.get('category')
        price = data.get('price')

        if name ==  None or category == None or price == None:
            return {"message": "Invalid input, missing id, name, price or category"}, 400

        if isinstance(price, (int, float)) == False:
            return {'message': "Price should be numeric type"}, 406

        product = {
            '_id': id,
            'name': name,
            'category': category,
            'price': price}
        
        products_collection.insert_one(product)
        return {"id": id}, 201  
    

    # Gauti produktus (visus arba pagal kategoriją)
    @app.route('/products', methods=['GET'])
    def get_products():
        category = request.args.get('category')
        
        if category != None:
            products = products_collection.find({'category': category}, {'_id': 1,  'name': 1, 'category': 1, 'price': 1})
        else:
            products = products_collection.find({}, {'_id': 1, 'name': 1, 'category': 1, 'price': 1})
        
        products_list = list(products)
        return products_list, 200
    
    
    # Gauti produktą pagal id
    @app.route('/products/<productId>', methods=['GET'])
    def get_product(productId):
        product = products_collection.find_one({'_id': str(productId)})
        if product != None:
            return {"id": product['_id'], "name": product['name'], "category": product['category'], "price": product['price']}, 200
        return {"message": "Product not found"}, 404
    

    # Ištrinti produktą pagal id
    @app.route('/products/<productId>', methods=['DELETE'])
    def delete_product(productId):
        product = products_collection.find_one({'_id': str(productId)})
        if product != None:
            products_collection.delete_one({'_id': str(productId)})
            return {"message": "Product deleted"}, 204
        return {"message": "Product not found"}, 404


    # Registruoti sandėlį
    @app.route('/warehouses', methods=['PUT'])
    def put_warehouse():
        data = request.get_json()
        name = data.get('name')
        location = data.get('location')
        capacity = data.get('capacity')

        if name == None or location == None or capacity == None:
            return {"message": "Invalid input, missing name, location or capacity"}, 400
                
        if isinstance(capacity, int) == False:
            return {"message": "Capacity should be an integer"}, 406
        
        while True:
            id = str(uuid.uuid4())
            if warehouses_collection.find_one({'_id': id}) == None:
                break

        warehouse = {
            '_id': id,
            'name': name,
            'location': location,
            'capacity': capacity
        }
        warehouses_collection.insert_one(warehouse)

        return {"id": id}, 201


    # Gauti sandėlį pagal id
    @app.route('/warehouses/<warehouseId>', methods=['GET']) 
    def get_warehouse(warehouseId):
        warehouse = warehouses_collection.find_one({'_id': str(warehouseId)})
        if warehouse != None:
            return {"id": warehouse['_id'], "name": warehouse['name'], "location": warehouse['location'], "capacity": warehouse['capacity']}, 200
        return {"message": "Warehouse not found"}, 404
    

    # Ištrinti sandėlį pagal id
    @app.route('/warehouses/<warehouseId>', methods=['DELETE'])
    def delete_warehouse(warehouseId):
        warehouse = warehouses_collection.find_one({'_id': str(warehouseId)})
        if warehouse != None:
            warehouses_collection.delete_one({'_id': str(warehouseId)})
            return {"message": "Warehouse deleted"}, 204
        return {"message": "Warehouse not found"}, 404
    

    # Registruoti produktą sandėlyje
    @app.route('/warehouses/<warehouseId>/inventory', methods=['PUT'])
    def put_inventory(warehouseId):
        data = request.get_json()
        productId = data.get('productId')
        quantity = data.get('quantity')

        if productId == None or quantity == None:
            return {"message": "Invalid input, missing productId or quantity"}, 400

        if isinstance(quantity, int) == False:
            return {"message": "Quantity should be an integer"}, 406

        if products_collection.find_one({'_id': productId}) == None:
            return {"message": "Product not found"}, 404

        if warehouses_collection.find_one({'_id': str(warehouseId)}) == None:
            return {"message": "Warehouse not found"}, 404
        
        if warehouses_collection.find_one({'_id': str(warehouseId), 'inventory.productId': productId}) != None:
            return {"message": "Product already exists in inventory"}, 402

        inventory = {
            'productId': productId,
            'quantity': quantity
        }
        warehouses_collection.update_one({'_id': str(warehouseId)}, {'$push': {'inventory': inventory}})
        return {"id": productId}, 201


    # Gauti sandėlio inventorių
    @app.route('/warehouses/<warehouseId>/inventory', methods=['GET'])
    def get_inventory(warehouseId):
        warehouse = warehouses_collection.find_one({'_id': str(warehouseId)})
        if warehouse == None:
            return {"message": "Warehouse not found"}, 404
        return warehouse['inventory'], 200


    # Gauti sandėlio inventoriaus elementą pagal id
    @app.route('/warehouses/<warehouseId>/inventory/<inventoryId>', methods=['GET'])
    def get_inventory_item(warehouseId, inventoryId):
        warehouse = warehouses_collection.find_one({'_id': str(warehouseId)})
        if warehouse != None:
            for inventory in warehouse['inventory']:
                if inventory['productId'] == str(inventoryId):
                    return {"productId": inventory['productId'], "quantity": inventory['quantity']}, 200
        return {"message": "Inventory not found"}, 404
    

    # Ištrinti sandėlio inventoriaus elementą pagal id
    @app.route('/warehouses/<warehouseId>/inventory/<inventoryId>', methods=['DELETE'])
    def delete_inventory_item(warehouseId, inventoryId):
        warehouse = warehouses_collection.find_one({'_id': str(warehouseId)})
        if warehouse != None:
            for inventory in warehouse['inventory']:
                if inventory['productId'] == str(inventoryId):
                    warehouses_collection.update_one({'_id': str(warehouseId)}, {'$pull': {'inventory': {'productId': str(inventoryId)}}})
                    return {"message": "Inventory item deleted"}, 204
        return {"message": "Inventory not found"}, 404
    

    # Gauti pasirinkto sandėlio vertę
    @app.route('/warehouses/<warehouseId>/value', methods=['GET'])
    def get_warehouse_value(warehouseId):

        pipeline = [
            {'$match': {'_id': str(warehouseId)}},
            {'$unwind': '$inventory'},
            {'$lookup': {
                'from': 'products',
                'localField': 'inventory.productId',
                'foreignField': '_id',
                'as': 'productInfo'}
            },
            {'$group': {
                '_id': 0,
                'totalValue': {'$sum': {'$multiply': ['$inventory.quantity', {'$arrayElemAt': ['$productInfo.price', 0]}]}}
            }}
        ]

        result = list(warehouses_collection.aggregate(pipeline))
        if result != None:
            return {"value": result[0]['totalValue']}, 200
        return {"message": "Warehouse not found or empty inventory"}, 404


    # Gauti visų sandėlių talpą, užimamą vietą ir laisvą vietą
    @app.route('/statistics/warehouse/capacity', methods=['GET'])
    def get_warehouse_capacity():

        pipeline = [
            {'$unwind': '$inventory'},
            {'$group': {
            '_id': 0,
            'totalCapacity': {'$sum': '$capacity'},
            'usedCapacity': {'$sum': '$inventory.quantity'}
            }}
        ]

        result = list(warehouses_collection.aggregate(pipeline))
        if result != None:
            return {"totalCapacity": result[0]['totalCapacity'], "usedCapacity": result[0]['usedCapacity'], "freeCapacity": result[0]['totalCapacity'] - result[0]['usedCapacity']}, 200
        return {"message": "No warehouses found"}, 404


    # Gauti produktų kiekį pagal kategoriją
    @app.route('/statistics/products/by/category', methods=['GET'])
    def get_products_by_category():
        

        pipeline = [
            {'$group': {
            '_id': '$category',
            'count': {'$sum': 1}
            }},
            {'$project': {
                'category': '$_id',  
                '_id': 0,
                'count': 1
            }}
        ]

        result = list(products_collection.aggregate(pipeline))
        if result != None:
            return result, 200
        return {"message": "No products found"}, 404

      
    # Išvalyti duomenų bazę
    @app.route('/cleanup', methods=['POST'])
    def cleanup():
        products_collection.delete_many({})
        warehouses_collection.delete_many({})
        return {"message": "Cleanup completed."}, 200
    
    return app