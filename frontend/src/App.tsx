import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts'
import { 
  FiUpload, FiDownload, FiFileText, FiTrendingUp, 
  FiAlertCircle, FiCheckCircle, FiBarChart2, FiDollarSign,
  FiCalendar, FiCreditCard, FiActivity, FiLock, FiX
} from 'react-icons/fi'
import CardSwipeLoader from './components/CardSwipeLoader'
import './App.css'

interface ParsedData {
  issuer?: string
  detected_issuer?: string
  card_last_four_digits?: string
  billing_cycle?: {
    start_date: string
    end_date: string
  }
  payment_due_date?: string
  total_balance?: string
  transaction_info?: {
    transaction_count: string
    total_charges: string
  }
  confidence_scores?: {
    [key: string]: number
    overall?: number
  }
  extraction_metadata?: {
    extracted_at: string
    pdf_pages: number
    text_length: number
  }
  analytics?: {
    spending_insights?: any
    payment_recommendations?: Array<{
      type: string
      message: string
      priority: string
    }>
    trends?: any
  }
  error?: string
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [parsedData, setParsedData] = useState<ParsedData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'insights'>('overview')
  const [showLoader, setShowLoader] = useState(true)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [pdfPassword, setPdfPassword] = useState('')
  const [passwordError, setPasswordError] = useState<string | null>(null)

  useEffect(() => {
    // Show loader on initial mount
    const hasSeenLoader = sessionStorage.getItem('hasSeenLoader')
    if (hasSeenLoader) {
      setShowLoader(false)
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile)
        setError(null)
        setParsedData(null)
      } else {
        setError('Please upload a PDF file')
        setFile(null)
      }
    }
  }

  const handleSubmit = async (e?: React.FormEvent, password?: string) => {
    if (e) e.preventDefault()
    if (!file) {
      setError('Please select a PDF file')
      return
    }

    setLoading(true)
    setError(null)
    setParsedData(null)

    const formData = new FormData()
    formData.append('file', file)
    if (password) {
      formData.append('password', password)
    }

    try {
      const response = await axios.post('/api/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setParsedData(response.data)
      setActiveTab('overview')
      setShowPasswordModal(false)
      setPdfPassword('')
      setPasswordError(null)
    } catch (err: any) {
      console.error('Error:', err)
      
      // Check if password is required
      if (err.response?.status === 401 || 
          err.response?.headers?.['x-requires-password'] === 'true' ||
          (err.response?.data?.detail && err.response.data.detail.toLowerCase().includes('password'))) {
        const errorDetail = err.response?.data?.detail || ''
        if (errorDetail.toLowerCase().includes('incorrect')) {
          setPasswordError('Incorrect password. Please try again.')
        } else {
          setPasswordError(null)
        }
        setShowPasswordModal(true)
        setError(null)
        setLoading(false)
        return
      }
      
      if (err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else if (err.response?.data?.error) {
        setError(err.response.data.error)
      } else if (err.response?.data?.message) {
        setError(err.response.data.message)
      } else if (err.message) {
        setError(`Error: ${err.message}`)
      } else {
        setError('Failed to parse PDF. Please ensure it is a valid credit card statement.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordSubmit = () => {
    if (pdfPassword.trim()) {
      handleSubmit(undefined, pdfPassword)
    }
  }

  const handlePasswordCancel = () => {
    setShowPasswordModal(false)
    setPdfPassword('')
    setError(null)
    setPasswordError(null)
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPdfPassword(e.target.value)
    if (passwordError) {
      setPasswordError(null) // Clear error when user types
    }
  }

  const handleReset = () => {
    setFile(null)
    setParsedData(null)
    setError(null)
    setLoading(false)
    setActiveTab('overview')
    const fileInput = document.getElementById('file-input') as HTMLInputElement
    if (fileInput) fileInput.value = ''
  }

  const handleExportCSV = async () => {
    if (!parsedData) return
    try {
      const response = await axios.post('/api/export/csv', parsedData, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'statement_data.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  const handleExportJSON = async () => {
    if (!parsedData) return
    try {
      const response = await axios.post('/api/export/json', parsedData, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'statement_data.json')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  const handleDownloadBankDetails = async () => {
    try {
      const response = await axios.get('/api/export/bank-details', {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'bank_details.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return '#10b981'
    if (score >= 0.5) return '#f59e0b'
    return '#ef4444'
  }

  const prepareChartData = () => {
    if (!parsedData?.confidence_scores) return []
    const scores = parsedData.confidence_scores
    return [
      { name: 'Card Digits', value: scores.card_last_four_digits || 0 },
      { name: 'Billing Cycle', value: scores.billing_cycle || 0 },
      { name: 'Due Date', value: scores.payment_due_date || 0 },
      { name: 'Balance', value: scores.total_balance || 0 },
      { name: 'Transactions', value: scores.transaction_info || 0 },
    ]
  }

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

  const handleLoaderComplete = () => {
    setShowLoader(false)
    sessionStorage.setItem('hasSeenLoader', 'true')
  }

  return (
    <>
      {showLoader && <CardSwipeLoader onComplete={handleLoaderComplete} />}
      
      {/* Password Modal */}
      {showPasswordModal && (
        <div className="modal-overlay" onClick={handlePasswordCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <FiLock />
                PDF Password Required
              </h2>
              <button className="modal-close" onClick={handlePasswordCancel}>
                <FiX />
              </button>
            </div>
            <div className="modal-body">
              <p>This PDF is password-protected. Please enter the password to continue.</p>
              <div className="password-input-group">
                <label htmlFor="pdf-password">Password:</label>
                <input
                  id="pdf-password"
                  type="password"
                  value={pdfPassword}
                  onChange={handlePasswordChange}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && pdfPassword.trim()) {
                      handlePasswordSubmit()
                    }
                  }}
                  placeholder="Enter PDF password"
                  autoFocus
                  className={`password-input ${passwordError ? 'error' : ''}`}
                />
                {passwordError && (
                  <div className="password-error">
                    <FiAlertCircle />
                    {passwordError}
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={handlePasswordCancel}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handlePasswordSubmit}
                disabled={loading || !pdfPassword.trim()}
              >
                {loading ? 'Processing...' : 'Unlock & Parse'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="app">
        <div className="container">
        <header className="header">
          <div className="header-content">
            <h1>
              <FiCreditCard className="header-icon" />
              Credit Card Statement Parser
            </h1>
            <p className="subtitle">AI-Powered PDF Analysis & Financial Insights</p>
          </div>
          <div className="header-actions">
            {parsedData && (
              <>
                <button onClick={handleExportCSV} className="btn-icon" title="Export CSV">
                  <FiDownload /> CSV
                </button>
                <button onClick={handleExportJSON} className="btn-icon" title="Export JSON">
                  <FiDownload /> JSON
                </button>
              </>
            )}
            <button onClick={handleDownloadBankDetails} className="btn-icon" title="Download Bank Details">
              <FiDownload /> Bank Details
            </button>
          </div>
        </header>

        <div className="card upload-card">
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="file-input-wrapper">
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="file-input"
              />
              <label htmlFor="file-input" className="file-label">
                <FiUpload className="upload-icon" />
                {file ? file.name : 'Choose PDF Statement'}
              </label>
            </div>

            {file && (
              <div className="file-info">
                <FiFileText className="file-icon" />
                <span>{file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
              </div>
            )}

            <div className="button-group">
              <button
                type="submit"
                disabled={!file || loading}
                className={`btn btn-primary ${loading ? 'loading' : ''}`}
              >
                {loading ? (
                  <>
                    <div className="spinner"></div>
                    Parsing...
                  </>
                ) : (
                  <>
                    <FiActivity />
                    Parse Statement
                  </>
                )}
              </button>
              {(file || parsedData) && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="btn btn-secondary"
                >
                  Reset
                </button>
              )}
            </div>
          </form>

          {error && (
            <div className="error-message">
              <FiAlertCircle />
              <div>
                <strong>Error:</strong> {error}
              </div>
            </div>
          )}
        </div>

        {parsedData && !parsedData.error && (
          <>
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <FiFileText /> Overview
              </button>
              <button
                className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
                onClick={() => setActiveTab('analytics')}
              >
                <FiBarChart2 /> Analytics
              </button>
              <button
                className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
                onClick={() => setActiveTab('insights')}
              >
                <FiTrendingUp /> Insights
              </button>
            </div>

            {activeTab === 'overview' && (
              <div className="card results-card">
                <div className="results-header">
                  <h2>
                    <FiCheckCircle className="success-icon" />
                    Extracted Information
                  </h2>
                  {parsedData.confidence_scores?.overall && (
                    <div className="confidence-badge">
                      Confidence: {(parsedData.confidence_scores.overall * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
                
                <div className="data-grid">
                  <div className="data-card highlight">
                    <div className="data-icon">
                      <FiCreditCard />
                    </div>
                    <div className="data-label">Credit Card Issuer</div>
                    <div className="data-value large">
                      {parsedData.detected_issuer || parsedData.issuer || 'N/A'}
                    </div>
                    {parsedData.confidence_scores && (
                      <div className="confidence-bar">
                        <div 
                          className="confidence-fill"
                          style={{
                            width: `${(parsedData.confidence_scores.card_last_four_digits || 0) * 100}%`,
                            backgroundColor: getConfidenceColor(parsedData.confidence_scores.card_last_four_digits || 0)
                          }}
                        />
                      </div>
                    )}
                  </div>

                  <div className="data-card">
                    <div className="data-icon">
                      <FiCreditCard />
                    </div>
                    <div className="data-label">Card Last 4 Digits</div>
                    <div className="data-value">{parsedData.card_last_four_digits || 'N/A'}</div>
                    {parsedData.confidence_scores && (
                      <div className="confidence-score">
                        {(parsedData.confidence_scores.card_last_four_digits * 100).toFixed(0)}% confident
                      </div>
                    )}
                  </div>

                  <div className="data-card">
                    <div className="data-icon">
                      <FiCalendar />
                    </div>
                    <div className="data-label">Payment Due Date</div>
                    <div className="data-value">{parsedData.payment_due_date || 'N/A'}</div>
                    {parsedData.confidence_scores && (
                      <div className="confidence-score">
                        {(parsedData.confidence_scores.payment_due_date * 100).toFixed(0)}% confident
                      </div>
                    )}
                  </div>

                  <div className="data-card highlight balance-card">
                    <div className="data-icon">
                      <FiDollarSign />
                    </div>
                    <div className="data-label">Total Balance</div>
                    <div className="data-value balance large">{parsedData.total_balance || 'N/A'}</div>
                    {parsedData.confidence_scores && (
                      <div className="confidence-score">
                        {(parsedData.confidence_scores.total_balance * 100).toFixed(0)}% confident
                      </div>
                    )}
                  </div>

                  <div className="data-card wide">
                    <div className="data-icon">
                      <FiCalendar />
                    </div>
                    <div className="data-label">Billing Cycle</div>
                    <div className="data-value">
                      {parsedData.billing_cycle?.start_date && parsedData.billing_cycle?.end_date
                        ? `${parsedData.billing_cycle.start_date} → ${parsedData.billing_cycle.end_date}`
                        : 'N/A'}
                    </div>
                    {parsedData.confidence_scores && (
                      <div className="confidence-score">
                        {(parsedData.confidence_scores.billing_cycle * 100).toFixed(0)}% confident
                      </div>
                    )}
                  </div>

                  <div className="data-card wide">
                    <div className="data-icon">
                      <FiActivity />
                    </div>
                    <div className="data-label">Transaction Information</div>
                    <div className="data-value">
                      {parsedData.transaction_info?.transaction_count !== 'N/A'
                        ? `Count: ${parsedData.transaction_info.transaction_count}`
                        : ''}
                      {parsedData.transaction_info?.total_charges !== 'N/A'
                        ? ` • Total: ${parsedData.transaction_info.total_charges}`
                        : ''}
                      {(!parsedData.transaction_info || 
                         (parsedData.transaction_info.transaction_count === 'N/A' && 
                          parsedData.transaction_info.total_charges === 'N/A'))
                        ? 'N/A'
                        : ''}
                    </div>
                    {parsedData.confidence_scores && (
                      <div className="confidence-score">
                        {(parsedData.confidence_scores.transaction_info * 100).toFixed(0)}% confident
                      </div>
                    )}
                  </div>
                </div>

                {parsedData.extraction_metadata && (
                  <div className="metadata">
                    <div className="metadata-item">
                      <strong>Extracted:</strong> {new Date(parsedData.extraction_metadata.extracted_at).toLocaleString()}
                    </div>
                    <div className="metadata-item">
                      <strong>PDF Pages:</strong> {parsedData.extraction_metadata.pdf_pages}
                    </div>
                    <div className="metadata-item">
                      <strong>Text Length:</strong> {parsedData.extraction_metadata.text_length.toLocaleString()} chars
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'analytics' && parsedData.confidence_scores && (
              <div className="card analytics-card">
                <h2>Extraction Confidence Analytics</h2>
                <div className="charts-container">
                  <div className="chart-card">
                    <h3>Confidence Scores by Data Point</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={prepareChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis domain={[0, 1]} />
                        <Tooltip 
                          formatter={(value: number) => `${(value * 100).toFixed(0)}%`}
                        />
                        <Bar dataKey="value" fill="#667eea" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="chart-card">
                    <h3>Overall Distribution</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={prepareChartData()}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {prepareChartData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'insights' && parsedData.analytics && (
              <div className="card insights-card">
                <h2>AI-Generated Insights</h2>
                {parsedData.analytics.payment_recommendations && parsedData.analytics.payment_recommendations.length > 0 && (
                  <div className="recommendations">
                    <h3>
                      <FiTrendingUp />
                      Payment Recommendations
                    </h3>
                    {parsedData.analytics.payment_recommendations.map((rec, idx) => (
                      <div key={idx} className={`recommendation ${rec.priority}`}>
                        <div className="recommendation-icon">
                          {rec.priority === 'high' ? <FiAlertCircle /> : <FiCheckCircle />}
                        </div>
                        <div className="recommendation-content">
                          <div className="recommendation-priority">{rec.priority.toUpperCase()}</div>
                          <div className="recommendation-message">{rec.message}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {parsedData.analytics.spending_insights && Object.keys(parsedData.analytics.spending_insights).length > 0 && (
                  <div className="spending-insights">
                    <h3>
                      <FiDollarSign />
                      Spending Insights
                    </h3>
                    <div className="insights-grid">
                      {parsedData.analytics.spending_insights.current_balance && (
                        <div className="insight-item">
                          <div className="insight-label">Current Balance</div>
                          <div className="insight-value">
                            ₹{parseFloat(parsedData.analytics.spending_insights.current_balance.toString()).toLocaleString('en-IN', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        <footer className="footer">
          <div className="footer-content">
            <p>✨ Extracts 5 key data points with AI-powered confidence scoring</p>
            <p className="footer-links">
              Supports: HDFC Bank • ICICI Bank • SBI • Axis Bank • Kotak Mahindra • DCB Bank • Yes Bank • IndusInd Bank • OneCard
            </p>
          </div>
        </footer>
      </div>
    </div>
    </>
  )
}

export default App
