import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // Typing animation state
  const fullText = "Bangalore House Price Predictor"
  const [displayText, setDisplayText] = useState("")
  const [charIndex, setCharIndex] = useState(0)

  // Form state
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState('')
  const [sqft, setSqft] = useState('')
  const [bhk, setBhk] = useState('')
  const [bath, setBath] = useState('')
  
  // Result state
  const [predictedPrice, setPredictedPrice] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [locationsLoading, setLocationsLoading] = useState(true)

  // API base URL
  const API_URL = 'http://localhost:5000'

  // Typing animation effect
  useEffect(() => {
    if (charIndex < fullText.length) {
      const timer = setTimeout(() => {
        setDisplayText(fullText.substring(0, charIndex + 1))
        setCharIndex(charIndex + 1)
      }, 100)
      return () => clearTimeout(timer)
    } else {
      // Reset after completion and wait
      const resetTimer = setTimeout(() => {
        setCharIndex(0)
        setDisplayText("")
      }, 3000)
      return () => clearTimeout(resetTimer)
    }
  }, [charIndex, fullText])

  // Fetch locations on component mount
  useEffect(() => {
    fetchLocations()
  }, [])

  // Fetch all locations from backend
  const fetchLocations = async () => {
    try {
      setLocationsLoading(true)
      const response = await fetch(`${API_URL}/get_location_names`)
      const data = await response.json()
      
      if (data.status === 'success') {
        setLocations(data.locations)
        if (data.locations.length > 0) {
          setSelectedLocation(data.locations[0])
        }
      } else {
        setError('Failed to load locations')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure Flask is running on port 5000.')
      console.error('Error fetching locations:', err)
    } finally {
      setLocationsLoading(false)
    }
  }

  // Handle form submission
  const handlePredict = async (e) => {
    e.preventDefault()
    
    // Validation
    if (!selectedLocation || !sqft || !bhk || !bath) {
      setError('Please fill all fields')
      return
    }

    if (parseFloat(sqft) <= 0 || parseInt(bhk) <= 0 || parseInt(bath) <= 0) {
      setError('All values must be positive numbers')
      return
    }

    setLoading(true)
    setError(null)
    setPredictedPrice(null)

    try {
      const response = await fetch(`${API_URL}/predict_home_price`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          total_sqft: parseFloat(sqft),
          location: selectedLocation,
          bhk: parseInt(bhk),
          bath: parseInt(bath)
        })
      })

      const data = await response.json()

      if (data.status === 'success') {
        setPredictedPrice(data.estimated_price)
      } else {
        setError(data.message || 'Prediction failed')
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure Flask is running on port 5000.')
      console.error('Error predicting price:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle reset
  const handleReset = () => {
    setSqft('')
    setBhk('')
    setBath('')
    setPredictedPrice(null)
    setError(null)
    if (locations.length > 0) {
      setSelectedLocation(locations[0])
    }
  }

  return (
    <div className="app">
      {/* Header with Typing Animation */}
      <header className="header">
        <h1 className="typing-text">
          {displayText}
          <span className="cursor">|</span>
        </h1>
        <p>Predict house prices in Bangalore using Machine Learning</p>
      </header>

      {/* Main Container */}
      <div className="container">
        {/* Prediction Form */}
        <div className="card">
          <h2>Enter Property Details</h2>
          
          {locationsLoading ? (
            <div className="loading">Loading locations...</div>
          ) : (
            <form onSubmit={handlePredict}>
              {/* Location Dropdown */}
              <div className="form-group">
                <label htmlFor="location">
                  <span className="icon"></span>
                  Location
                </label>
                <select
                  id="location"
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  required
                >
                  {locations.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc.split(' ').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join(' ')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Square Feet Input */}
              <div className="form-group">
                <label htmlFor="sqft">
                  <span className="icon"></span>
                  Total Square Feet
                </label>
                <input
                  type="number"
                  id="sqft"
                  placeholder="e.g., 1000"
                  value={sqft}
                  onChange={(e) => setSqft(e.target.value)}
                  min="1"
                  step="1"
                  required
                />
              </div>

              {/* BHK Input */}
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="bhk">
                    <span className="icon"></span>
                    BHK
                  </label>
                  <input
                    type="number"
                    id="bhk"
                    placeholder="2"
                    value={bhk}
                    onChange={(e) => setBhk(e.target.value)}
                    min="1"
                    max="20"
                    required
                  />
                </div>

                {/* Bathrooms Input */}
                <div className="form-group">
                  <label htmlFor="bath">
                    <span className="icon"></span>
                    Bathrooms
                  </label>
                  <input
                    type="number"
                    id="bath"
                    placeholder="2"
                    value={bath}
                    onChange={(e) => setBath(e.target.value)}
                    min="1"
                    max="20"
                    required
                  />
                </div>
              </div>

              {/* Buttons */}
              <div className="button-group">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Predicting...' : 'Predict Price'}
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleReset}
                  disabled={loading}
                >
                  Reset
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Results Section */}
        {(predictedPrice !== null || error) && (
          <div className="card result-card">
            {/* Success - Show Predicted Price */}
            {predictedPrice !== null && (
              <div className="result success">
                <div className="result-icon">💰</div>
                <h3>Predicted Price</h3>
                <div className="price">
                  ₹ {predictedPrice} <span className="currency">Lakhs</span>
                </div>
                <div className="price-inr">
                  ≈ ₹ {(predictedPrice * 100000).toLocaleString('en-IN')}
                </div>
                <div className="result-details">
                  <p><strong>Location:</strong> {selectedLocation.split(' ').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}</p>
                  <p><strong>Area:</strong> {sqft} sq.ft</p>
                  <p><strong>Configuration:</strong> {bhk} BHK, {bath} Bath</p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="result error">
                <div className="result-icon">❌</div>
                <h3>Error</h3>
                <p>{error}</p>
              </div>
            )}
          </div>
        )}

        {/* Info Section */}
        <div className="info-section">
          <h3>ℹ️ How it works</h3>
          <ul>
            <li>Select your desired location from {locations.length}+ areas in Bangalore</li>
            <li>Enter the property size in square feet</li>
            <li>Specify the number of bedrooms (BHK) and bathrooms</li>
            <li>Click "Predict Price" to get an estimated price based on ML model</li>
          </ul>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Built with React + Flask + Machine Learning</p>
        <p>Data trained on 13,000+ Bangalore house prices</p>
      </footer>
    </div>
  )
}

export default App
