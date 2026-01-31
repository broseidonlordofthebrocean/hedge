'use client'

import { useEffect, useState } from 'react'

interface SurvivalMeterProps {
  score: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const sizeStyles = {
  sm: 'h-2',
  md: 'h-4',
  lg: 'h-6',
}

const labelSizeStyles = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
}

function getGradientColor(score: number): string {
  if (score < 40) {
    return '#ef4444' // red
  } else if (score < 55) {
    return '#f97316' // orange
  } else if (score < 70) {
    return '#eab308' // gold
  } else if (score < 85) {
    return '#06b6d4' // cyan
  } else {
    return '#22c55e' // green
  }
}

export function SurvivalMeter({
  score,
  showLabel = false,
  size = 'md',
}: SurvivalMeterProps) {
  const [animatedWidth, setAnimatedWidth] = useState(0)
  const clampedScore = Math.max(0, Math.min(100, score))
  const fillColor = getGradientColor(clampedScore)

  useEffect(() => {
    // Trigger animation after mount
    const timer = requestAnimationFrame(() => {
      setAnimatedWidth(clampedScore)
    })
    return () => cancelAnimationFrame(timer)
  }, [clampedScore])

  return (
    <div className="w-full">
      {showLabel && (
        <div className={`mb-1 font-medium text-gray-300 ${labelSizeStyles[size]}`}>
          Survival Score: {clampedScore}%
        </div>
      )}
      <div
        className={`w-full rounded-full overflow-hidden ${sizeStyles[size]}`}
        style={{ backgroundColor: '#2a2a2a' }}
      >
        <div
          className={`${sizeStyles[size]} rounded-full transition-all duration-700 ease-out`}
          style={{
            width: `${animatedWidth}%`,
            backgroundColor: fillColor,
          }}
        />
      </div>
    </div>
  )
}
