"""
Utility module for Bangalore House Price Prediction
Contains helper functions for model loading and prediction
"""

import pickle
import json
import numpy as np
import os

__locations = None
__data_columns = None
__model = None

def load_saved_artifacts(artifacts_path='./artifacts'):
    """
    Load the pre-trained model and columns from artifacts folder
    
    Args:
        artifacts_path (str): Path to artifacts folder
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Loading saved artifacts...")
    global __data_columns
    global __locations
    global __model
    
    try:
        # Check if artifacts folder exists
        if not os.path.exists(artifacts_path):
            raise FileNotFoundError(f"Artifacts folder not found: {artifacts_path}")
        
        # Load columns
        columns_path = os.path.join(artifacts_path, 'columns.json')
        with open(columns_path, "r") as f:
            __data_columns = json.load(f)['data_columns']
            __locations = __data_columns[3:]  # first 3 are sqft, bath, bhk
        
        print(f"Loaded {len(__data_columns)} columns")
        print(f"Loaded {len(__locations)} locations")
        
        # Load model
        model_path = os.path.join(artifacts_path, 'bangalore_home_prices_model.pickle')
        with open(model_path, "rb") as f:
            __model = pickle.load(f)
        
        print("Model loaded successfully")
        print("Loading artifacts...done")
        return True
    
    except Exception as e:
        print(f"Error loading artifacts: {e}")
        return False

def get_estimated_price(location, sqft, bhk, bath):
    """
    Predict house price
    
    Args:
        location (str): Location name
        sqft (float): Total square feet
        bhk (int): Number of bedrooms
        bath (int): Number of bathrooms
    
    Returns:
        float: Predicted price in lakhs (INR)
    """
    if __model is None:
        raise Exception("Model not loaded. Call load_saved_artifacts() first.")
    
    try:
        loc_index = __data_columns.index(location.lower())
    except:
        loc_index = -1
    
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

# ==================== TESTING ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Utility Module")
    print("=" * 60)
    
    # Load artifacts
    load_saved_artifacts()
    
    # Test predictions
    print("\n📍 Sample locations:")
    print(get_location_names()[:10])
    
    print("\n🧪 Test Predictions:")
    print("-" * 60)
    
    test_cases = [
        ('1st Phase JP Nagar', 1000, 2, 2),
        ('Indira Nagar', 1500, 3, 3),
        ('Whitefield', 1200, 2, 2),
        ('Rajaji Nagar', 2000, 4, 4),
    ]
    
    for location, sqft, bhk, bath in test_cases:
        try:
            price = get_estimated_price(location, sqft, bhk, bath)
            print(f"Location: {location:20s} | {sqft} sqft | {bhk} BHK | {bath} Bath")
            print(f"  → Predicted Price: ₹{price} Lakhs")
            print()
        except Exception as e:
            print(f"Error for {location}: {e}\n")
    
    print("=" * 60)
