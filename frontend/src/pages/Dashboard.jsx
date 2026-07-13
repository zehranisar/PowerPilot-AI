import { useState, useEffect } from 'react'
import api from '../services/api'
import { 
  Activity, 
  TrendingUp, 
  Clock, 
  Zap,
  Loader2,
  AlertCircle,
  Download,
  Upload,
  FileText,
  BarChart3
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'
import ModelComparison from '../components/ModelComparison'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [clusters, setClusters] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [hasData, setHasData] = useState(false)
  const [loadingData, setLoadingData] = useState(false)
  const [trainingStatus, setTrainingStatus] = useState(null)
  const [showDataSourceChoice, setShowDataSourceChoice] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [training, setTraining] = useState(false)
  const [showModelComparison, setShowModelComparison] = useState(false)

  useEffect(() => {
    checkTrainingStatusAndFetch()
  }, [])

  const checkTrainingStatusAndFetch = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Check training status
      const statusRes = await api.get('/data/training-status')
      setTrainingStatus(statusRes.data)
      
      if (!statusRes.data.data_source_chosen) {
        setShowDataSourceChoice(true)
        setLoading(false)
        return
      }
      
      if (!statusRes.data.model_trained) {
        // Data source chosen but model not trained yet
        setShowDataSourceChoice(false) // Hide data source choice, show training screen
        setLoading(false)
        return
      }
      
      // Model is trained, show dashboard with analyses
      setShowDataSourceChoice(false)
      
      // Check if user has data
      const dataCheck = await api.get('/data/has-data')
      setHasData(dataCheck.data.has_data)
      
      if (dataCheck.data.has_data) {
        // Fetch summary and clusters
        const [summaryRes, clustersRes] = await Promise.all([
          api.get('/predict/summary'),
          api.get('/predict/clusters')
        ])
        setSummary(summaryRes.data)
        setClusters(clustersRes.data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const chooseDataSource = async (useExisting) => {
    try {
      setError('')
      setTraining(true)
      const response = await api.post('/data/choose-data-source', { use_existing: useExisting })
      
      if (useExisting && response.data.model_trained) {
        // Model was automatically trained, refresh dashboard to show analyses
        setShowDataSourceChoice(false)
        await checkTrainingStatusAndFetch()
      } else if (!useExisting) {
        // User will upload their own file
        setShowDataSourceChoice(false)
        setTrainingStatus({ ...trainingStatus, data_source_chosen: true, uses_own_data: true })
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save data source choice')
      console.error(err)
    } finally {
      setTraining(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file')
      return
    }
    
    setSelectedFile(file)
    setError('')
  }

  const uploadFile = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }
    
    try {
      setUploading(true)
      setError('')
      
      // First, choose data source if not already chosen
      if (!trainingStatus || !trainingStatus.data_source_chosen) {
        await api.post('/data/choose-data-source', { use_existing: false })
        // Update local state
        if (trainingStatus) {
          setTrainingStatus({ ...trainingStatus, data_source_chosen: true, uses_own_data: true })
        }
      }
      
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      await api.post('/data/upload-data-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // Train model after upload - this will automatically show dashboard
      setUploading(false)
      setTraining(true)
      await trainModel()
      
      // After training completes, checkTrainingStatusAndFetch was called in trainModel
      // which will automatically show the dashboard with all analyses
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload file')
      console.error(err)
      setUploading(false)
      setTraining(false)
    }
  }

  const trainModel = async () => {
    try {
      setTraining(true)
      setError('')
      
      const response = await api.post('/data/train-model')
      
      // Refresh data and show dashboard with all analyses
      await checkTrainingStatusAndFetch()
      
      // The checkTrainingStatusAndFetch will automatically show the dashboard
      // No need for alert, just show the results
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to train model')
      console.error(err)
    } finally {
      setTraining(false)
    }
  }

  const loadSampleData = async () => {
    try {
      setLoadingData(true)
      setError('')
      const response = await api.post('/data/load-sample-data')
      setHasData(true)
      // Refresh data
      await checkTrainingStatusAndFetch()
      alert(`Success! ${response.data.records_added} records loaded from data.csv`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load sample data')
      console.error(err)
    } finally {
      setLoadingData(false)
    }
  }


  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  // Show data source choice if not chosen yet
  if (showDataSourceChoice) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Data Source Setup</h1>
          <p className="text-gray-600 mt-2">Choose your data source to train the model</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-200">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
            Choose Your Data Source
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Use Existing Data Option */}
            <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 hover:bg-primary-50 transition-all cursor-pointer"
                 onClick={() => chooseDataSource(true)}>
              <div className="flex flex-col items-center text-center">
                <div className="bg-blue-100 p-4 rounded-full mb-4">
                  <FileText className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Use Existing Data
                </h3>
                <p className="text-gray-600 mb-4">
                  Train the model using the existing data.csv file in the project
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    chooseDataSource(true)
                  }}
                  disabled={training}
                  className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {training ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                      Training...
                    </>
                  ) : (
                    'Use Existing Data'
                  )}
                </button>
              </div>
            </div>

            {/* Upload Own Data Option */}
            <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 hover:bg-primary-50 transition-all">
              <div className="flex flex-col items-center text-center">
                <div className="bg-green-100 p-4 rounded-full mb-4">
                  <Upload className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Upload Your Own Data
                </h3>
                <p className="text-gray-600 mb-4">
                  Upload your own CSV file to train the model on your data
                </p>
                <div className="w-full space-y-3">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                  {selectedFile && (
                    <p className="text-sm text-gray-600">Selected: {selectedFile.name}</p>
                  )}
                  <button
                    onClick={async () => {
                      await uploadFile()
                      // After upload and train, dashboard will automatically show
                    }}
                    disabled={!selectedFile || uploading || training}
                    className="w-full bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                        Uploading...
                      </>
                    ) : training ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                        Training...
                      </>
                    ) : (
                      'Upload & Train'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Show training in progress message
  if (trainingStatus && trainingStatus.data_source_chosen && !trainingStatus.model_trained) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Model Training</h1>
          <p className="text-gray-600 mt-2">Please upload your data file and train the model</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <Loader2 className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5 animate-spin" />
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-1">Model Training Required</h3>
              <p className="text-blue-800 text-sm mb-4">
                {trainingStatus.uses_own_data 
                  ? "Please upload your data file and train the model."
                  : "Click the button below to train the model using the existing data.csv file."}
              </p>
              {trainingStatus.uses_own_data ? (
                <div className="space-y-3">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                  {selectedFile && (
                    <p className="text-sm text-gray-600">Selected: {selectedFile.name}</p>
                  )}
                  <button
                    onClick={uploadFile}
                    disabled={!selectedFile || uploading || training}
                    className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin inline mr-2" />
                        Uploading...
                      </>
                    ) : training ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin inline mr-2" />
                        Training...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5 inline mr-2" />
                        Upload & Train Model
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <button
                  onClick={trainModel}
                  disabled={training}
                  className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {training ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin inline mr-2" />
                      Training Models...
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5 inline mr-2" />
                      Train Model with Existing Data
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const stats = [
    {
      name: 'Total Consumption',
      value: summary?.total_consumption?.toFixed(2) || '0.00',
      unit: 'kWh',
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Average Consumption',
      value: summary?.avg_consumption?.toFixed(2) || '0.00',
      unit: 'kWh',
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'Peak Hour',
      value: summary?.peak_hour !== null && summary?.peak_hour !== undefined 
        ? `${summary.peak_hour}:00` 
        : 'N/A',
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    },
    {
      name: 'Lowest Hour',
      value: summary?.lowest_hour !== null && summary?.lowest_hour !== undefined 
        ? `${summary.lowest_hour}:00` 
        : 'N/A',
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
  ]

  const clusterData = clusters?.cluster_centers?.map((center, idx) => ({
    name: `Cluster ${idx + 1}`,
    consumption: parseFloat(center).toFixed(2),
    count: clusters.cluster_counts?.[idx] || 0
  })) || []

  const hasNoData = !hasData

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your electricity consumption</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {!hasData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-1">No Consumption Data</h3>
              <p className="text-blue-800 text-sm mb-4">
                You don't have any consumption records yet. Click the button below to automatically 
                load sample data from data.csv file.
              </p>
              <button
                onClick={loadSampleData}
                disabled={loadingData}
                className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loadingData ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Loading Data...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Load Sample Data from data.csv
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid - Only show if user has data */}
      {hasData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon
            return (
              <div key={stat.name} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.name}</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stat.value} {stat.unit}
                    </p>
                  </div>
                  <div className={`${stat.bgColor} p-3 rounded-lg`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Clusters Chart - Only show if user has data */}
      {hasData && clusterData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Consumption Clusters</h2>
          <p className="text-sm text-gray-600 mb-4">
            These clusters represent different consumption patterns. The bars show average consumption 
            and the number of records in each cluster.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={clusterData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis yAxisId="left" orientation="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="consumption" fill="#0ea5e9" name="Avg Consumption (kWh)" />
              <Bar yAxisId="right" dataKey="count" fill="#10b981" name="Record Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/predictions"
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <h3 className="font-medium text-gray-900 mb-1">Make Prediction</h3>
            <p className="text-sm text-gray-600">Predict consumption for specific conditions</p>
          </a>
          <button
            onClick={() => setShowModelComparison(!showModelComparison)}
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-left"
          >
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 className="w-5 h-5 text-primary-600" />
              <h3 className="font-medium text-gray-900">Model Comparison</h3>
            </div>
            <p className="text-sm text-gray-600">Compare and select the best model</p>
          </button>
          <a
            href="/chat"
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <h3 className="font-medium text-gray-900 mb-1">Ask AI Assistant</h3>
            <p className="text-sm text-gray-600">Get insights using natural language</p>
          </a>
        </div>
      </div>

      {/* Model Comparison Section */}
      {showModelComparison && hasData && (
        <div className="mt-6">
          <ModelComparison />
        </div>
      )}
    </div>
  )
}
