import { useState, useEffect } from 'react'
import api from '../services/api'
import { Loader2, AlertCircle, CheckCircle, BarChart3, TrendingUp, TrendingDown } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function ModelComparison() {
  const [comparison, setComparison] = useState(null)
  const [selectedModel, setSelectedModel] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selecting, setSelecting] = useState(false)

  useEffect(() => {
    fetchComparison()
    fetchSelectedModel()
  }, [])

  const fetchComparison = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get('/data/model-comparison')
      setComparison(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load model comparison')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSelectedModel = async () => {
    try {
      const response = await api.get('/data/selected-model')
      setSelectedModel(response.data.selected_model)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSelectModel = async (modelName) => {
    try {
      setSelecting(true)
      setError('')
      await api.post('/data/select-model', { model_name: modelName })
      setSelectedModel(modelName)
      alert(`Model "${getModelDisplayName(modelName)}" selected successfully!`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to select model')
      console.error(err)
    } finally {
      setSelecting(false)
    }
  }

  const getModelDisplayName = (modelName) => {
    const names = {
      'linear_regression': 'Linear Regression',
      'decision_tree': 'Decision Tree',
      'random_forest': 'Random Forest',
      'knn': 'K-Nearest Neighbors'
    }
    return names[modelName] || modelName
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
        <AlertCircle className="w-5 h-5" />
        <span>{error}</span>
      </div>
    )
  }

  if (!comparison || !comparison.models || comparison.models.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800">No model comparison data available. Please train models first.</p>
      </div>
    )
  }

  // Prepare data for charts
  const chartData = comparison.models.map(model => ({
    name: getModelDisplayName(model.model_name),
    'R² Score': parseFloat((model.r2_score * 100).toFixed(2)),
    'RMSE': parseFloat(model.rmse.toFixed(2)),
    'MAE': model.mae ? parseFloat(model.mae.toFixed(2)) : 0
  }))

  // Sort by R² score (best first)
  const sortedModels = [...comparison.models].sort((a, b) => b.r2_score - a.r2_score)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Model Comparison</h2>
        <p className="text-gray-600 mt-2">Compare performance metrics and select the best model for predictions</p>
      </div>

      {/* Best Model Indicator */}
      {comparison.best_model && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">
              Best Model: <strong>{getModelDisplayName(comparison.best_model)}</strong> (Highest R² Score)
            </span>
          </div>
        </div>
      )}

      {/* Model Comparison Table */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Model</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">R² Score</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">RMSE</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">MAE</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedModels.map((model, idx) => {
                const isSelected = selectedModel === model.model_name
                const isBest = model.model_name === comparison.best_model
                return (
                  <tr 
                    key={model.model_name} 
                    className={`border-b border-gray-100 hover:bg-gray-50 ${
                      isSelected ? 'bg-primary-50' : ''
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          {getModelDisplayName(model.model_name)}
                        </span>
                        {isBest && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            Best
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="text-right py-3 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <span className="text-gray-900 font-medium">
                          {(model.r2_score * 100).toFixed(2)}%
                        </span>
                        {idx === 0 && <TrendingUp className="w-4 h-4 text-green-600" />}
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 text-gray-700">
                      {model.rmse.toFixed(2)}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-700">
                      {model.mae ? model.mae.toFixed(2) : 'N/A'}
                    </td>
                    <td className="text-center py-3 px-4">
                      {isSelected ? (
                        <span className="inline-flex items-center gap-1 text-primary-600 font-medium">
                          <CheckCircle className="w-4 h-4" />
                          Active
                        </span>
                      ) : (
                        <span className="text-gray-400">Inactive</span>
                      )}
                    </td>
                    <td className="text-center py-3 px-4">
                      <button
                        onClick={() => handleSelectModel(model.model_name)}
                        disabled={isSelected || selecting}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                          isSelected
                            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                            : 'bg-primary-600 text-white hover:bg-primary-700'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {selecting ? (
                          <Loader2 className="w-4 h-4 animate-spin inline" />
                        ) : isSelected ? (
                          'Selected'
                        ) : (
                          'Select'
                        )}
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* R² Score Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">R² Score Comparison</h3>
          <p className="text-sm text-gray-600 mb-4">
            Higher is better. R² score indicates how well the model fits the data (0-100%).
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="R² Score" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* RMSE Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">RMSE Comparison</h3>
          <p className="text-sm text-gray-600 mb-4">
            Lower is better. RMSE measures prediction error in the same units as consumption.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="RMSE" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Combined Metrics Chart */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">All Metrics Comparison</h3>
        <p className="text-sm text-gray-600 mb-4">
          Compare all performance metrics side by side
        </p>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
            <YAxis yAxisId="left" orientation="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="R² Score" fill="#0ea5e9" name="R² Score (%)" />
            <Bar yAxisId="right" dataKey="RMSE" fill="#ef4444" name="RMSE" />
            <Bar yAxisId="right" dataKey="MAE" fill="#f59e0b" name="MAE" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Model Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">About the Metrics:</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li><strong>R² Score:</strong> Measures how well the model explains the variance in data. Range: 0-1 (0-100%). Higher is better.</li>
          <li><strong>RMSE (Root Mean Squared Error):</strong> Average prediction error. Lower is better.</li>
          <li><strong>MAE (Mean Absolute Error):</strong> Average absolute difference between predictions and actual values. Lower is better.</li>
        </ul>
      </div>
    </div>
  )
}

