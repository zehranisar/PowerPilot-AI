import { useState } from 'react'
import api from '../services/api'
import { TrendingUp, Loader2, AlertCircle } from 'lucide-react'

export default function Predictions() {
  const [hour, setHour] = useState(12)
  const [temperature, setTemperature] = useState(20)
  const [isWeekend, setIsWeekend] = useState(false)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handlePredict = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/predict/knn', {
        hour,
        temperature,
        is_weekend: isWeekend
      })
      setPrediction(response.data.prediction)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get prediction')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Consumption Prediction</h1>
        <p className="text-gray-600 mt-2">Predict electricity consumption based on conditions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Input Parameters</h2>
          
          <form onSubmit={handlePredict} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hour of Day (0-23)
              </label>
              <input
                type="number"
                min="0"
                max="23"
                value={hour}
                onChange={(e) => setHour(parseInt(e.target.value))}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
              <input
                type="range"
                min="0"
                max="23"
                value={hour}
                onChange={(e) => setHour(parseInt(e.target.value))}
                className="w-full mt-2"
              />
              <p className="text-sm text-gray-500 mt-1">Selected: {hour}:00</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature (°C)
              </label>
              <input
                type="number"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
              <input
                type="range"
                min="-10"
                max="40"
                step="0.5"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full mt-2"
              />
              <p className="text-sm text-gray-500 mt-1">Selected: {temperature}°C</p>
            </div>

            <div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isWeekend}
                  onChange={(e) => setIsWeekend(e.target.checked)}
                  className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                />
                <span className="text-sm font-medium text-gray-700">Is Weekend</span>
              </label>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Predicting...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5" />
                  Get Prediction
                </>
              )}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Prediction Result</h2>
          
          {prediction !== null ? (
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-8 text-center">
                <div className="text-5xl font-bold text-primary-600 mb-2">
                  {prediction.toFixed(2)}
                </div>
                <div className="text-lg text-gray-600">kWh</div>
              </div>
              
              <div className="space-y-3 pt-4 border-t">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Hour:</span>
                  <span className="font-medium text-gray-900">{hour}:00</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Temperature:</span>
                  <span className="font-medium text-gray-900">{temperature}°C</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Day Type:</span>
                  <span className="font-medium text-gray-900">
                    {isWeekend ? 'Weekend' : 'Weekday'}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-gray-400">
              <TrendingUp className="w-16 h-16 mb-4 opacity-50" />
              <p>Enter parameters and click "Get Prediction" to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

