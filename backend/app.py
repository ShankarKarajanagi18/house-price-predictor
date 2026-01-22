from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import json
import numpy as np

app = Flask(__name__)
CORS(app)

# Global variables
__locations = None
__data_columns = None
__model = None

def load_saved_artifacts():
    """Load the pre-trained model and columns from artifacts folder"""
    print("🔄 Loading saved artifacts...")
    global __data_columns
    global __locations
    global __model
    
    try:
        # Load columns.json
        with open("./artifacts/columns.json", "r") as f:
            __data_columns = json.load(f)['data_columns']
            __locations = __data_columns[3:]  # first 3 columns are sqft, bath, bhk
        
        # Load trained model
        with open("./artifacts/banglore_home_prices_model.pickle", "rb") as f:
            __model = pickle.load(f)
        
        print("✅ Model and artifacts loaded successfully!")
        return True
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("⚠️  Please ensure model files exist in ./artifacts/ folder")
        return False

def get_estimated_price(location, sqft, bhk, bath):
    """
    Predict house price based on location, square feet, bedrooms, and bathrooms
    
    Args:
        location (str): Location name
        sqft (float): Total square feet area
        bhk (int): Number of bedrooms
        bath (int): Number of bathrooms
    
    Returns:
        float: Predicted price in lakhs
    """
    try:
        loc_index = __data_columns.index(location.lower())
    except:
        loc_index = -1
    
    # Create feature array
    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    
    if loc_index >= 0:
        x[loc_index] = 1
    
    return round(__model.predict([x])[0], 2)

def get_location_names():
    """Get list of all available locations"""
    return __locations

def get_data_columns():
    """Get list of all data columns"""
    return __data_columns

# ==================== API ROUTES ====================

@app.route('/', methods=['GET'])
def home():
    """Home endpoint - API information"""
    return jsonify({
        'message': '🏠 Bangalore House Price Prediction API',
        'status': 'running',
        'version': '1.0.0',
        'total_locations': len(__locations) if __locations else 0,
        'endpoints': {
            'home': '/ [GET]',
            'get_locations': '/get_location_names [GET]',
            'predict': '/predict_home_price [POST]'
        },
        'example_request': {
            'url': '/predict_home_price',
            'method': 'POST',
            'body': {
                'total_sqft': 1000,
                'location': '1st Phase JP Nagar',
                'bhk': 2,
                'bath': 2
            }
        }
    })

@app.route('/get_location_names', methods=['GET'])
def get_locations():
    """Get all available location names"""
    response = jsonify({
        'status': 'success',
        'total_locations': len(__locations),
        'locations': __locations
    })
    return response

@app.route('/predict_home_price', methods=['POST', 'OPTIONS'])
def predict_home_price():
    """
    Predict house price based on input parameters
    
    Expected JSON body:
    {
        "total_sqft": 1000,
        "location": "1st Phase JP Nagar",
        "bhk": 2,
        "bath": 2
    }
    """
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get JSON data from request
        data = request.json
        
        # Validate required fields
        required_fields = ['total_sqft', 'location', 'bhk', 'bath']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Extract and validate input values
        total_sqft = float(data['total_sqft'])
        location = data['location']
        bhk = int(data['bhk'])
        bath = int(data['bath'])
        
        # Validate positive values
        if total_sqft <= 0 or bhk <= 0 or bath <= 0:
            return jsonify({
                'status': 'error',
                'message': 'All numeric values must be positive'
            }), 400
        
        # Validate reasonable ranges
        if total_sqft > 50000:
            return jsonify({
                'status': 'error',
                'message': 'Total square feet seems unrealistic (max: 50000)'
            }), 400
        
        if bhk > 20:
            return jsonify({
                'status': 'error',
                'message': 'Number of bedrooms seems unrealistic (max: 20)'
            }), 400
        
        if bath > 20:
            return jsonify({
                'status': 'error',
                'message': 'Number of bathrooms seems unrealistic (max: 20)'
            }), 400
        
        # Make prediction
        estimated_price = get_estimated_price(location, total_sqft, bhk, bath)
        
        # Return successful response
        return jsonify({
            'status': 'success',
            'estimated_price': estimated_price,
            'currency': 'INR Lakhs',
            'input': {
                'location': location,
                'total_sqft': total_sqft,
                'bhk': bhk,
                'bath': bath
            }
        })
    
    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Missing required field: {str(e)}'
        }), 400
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid value type: {str(e)}'
        }), 400
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 BANGALORE HOUSE PRICE PREDICTION API")
    print("=" * 70)
    
    # Load model artifacts
    success = load_saved_artifacts()
    
    if success:
        print(f"📍 Total locations loaded: {len(__locations)}")
        print(f"📊 Total features: {len(__data_columns)}")
        print("🌐 Server running on: http://localhost:5000")
        print("📖 API Documentation: http://localhost:5000/")
        print("=" * 70)
        
        # Start Flask server
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("=" * 70)
        print("❌ Failed to start server. Please check artifact files.")
        print("=" * 70)
