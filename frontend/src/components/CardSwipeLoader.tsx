import React, { useState, useEffect } from 'react'
import './CardSwipeLoader.css'

interface CardSwipeLoaderProps {
  onComplete: () => void
}

const CardSwipeLoader: React.FC<CardSwipeLoaderProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0)
  const [showContent, setShowContent] = useState(true)

  useEffect(() => {
    // Progress animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + 2
      })
    }, 50)

    // Complete after 3 seconds
    const timer = setTimeout(() => {
      setShowContent(false)
      setTimeout(() => {
        onComplete()
      }, 800) // Wait for fade out animation
    }, 3000)

    return () => {
      clearInterval(progressInterval)
      clearTimeout(timer)
    }
  }, [onComplete])

  if (!showContent) return null

  return (
    <div className="card-swipe-loader">
      <div className="loader-background">
        {/* Animated gradient background */}
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      <div className="loader-content">
        {/* Swipe machine */}
        <div className="swipe-machine">
          <div className="machine-top"></div>
          <div className="machine-slot">
            {/* Magnetic stripe reading animation */}
            <div className="stripe-reader">
              <div className="stripe-light"></div>
            </div>
            
            {/* Credit Card */}
            <div className="credit-card">
              <div className="card-chip">
                <div className="chip-glow"></div>
              </div>
              <div className="card-number">
                <span className="number-segment">4532</span>
                <span className="number-segment">1234</span>
                <span className="number-segment">5678</span>
                <span className="number-segment">9010</span>
              </div>
              <div className="card-name">SURE FINANCE</div>
              <div className="card-expiry">12/25</div>
              
              
              
              {/* Card glow effect */}
              <div className="card-glow"></div>
            </div>
          </div>
        </div>

        {/* Loading text */}
        <div className="loading-text-container">
          <h2 className="loading-title">Initializing Your Financial Hub</h2>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">{progress}%</span>
        </div>

        {/* Sparkle effects */}
        <div className="sparkle sparkle-1"></div>
        <div className="sparkle sparkle-2"></div>
        <div className="sparkle sparkle-3"></div>
        <div className="sparkle sparkle-4"></div>
        <div className="sparkle sparkle-5"></div>
        <div className="sparkle sparkle-6"></div>
        <div className="sparkle sparkle-7"></div>
        <div className="sparkle sparkle-8"></div>
        
        {/* Particle effects around card */}
        <div className="particle particle-1"></div>
        <div className="particle particle-2"></div>
        <div className="particle particle-3"></div>
        <div className="particle particle-4"></div>
        <div className="particle particle-5"></div>
      </div>
    </div>
  )
}

export default CardSwipeLoader

