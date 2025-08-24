import React from 'react';
import { Box, Typography } from '@mui/material';

const ScoreGauge = ({ score, size = 120, showLabel = true }) => {
  const radius = size / 2 - 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  
  // Convert score (300-850) to percentage (0-100)
  const percentage = Math.max(0, Math.min(100, ((score - 300) / 550) * 100));
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  const getColor = (score) => {
    if (score >= 750) return '#4caf50'; // Green
    if (score >= 650) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const color = getColor(score);

  return (
    <Box display="flex" flexDirection="column" alignItems="center">
      <Box position="relative" display="inline-flex">
        <svg width={size} height={size}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e0e0e0"
            strokeWidth="8"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
            style={{
              transition: 'stroke-dashoffset 0.5s ease-in-out',
            }}
          />
        </svg>
        <Box
          position="absolute"
          top={0}
          left={0}
          bottom={0}
          right={0}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography variant="h6" component="div" color={color} fontWeight="bold">
            {Math.round(score)}
          </Typography>
        </Box>
      </Box>
      {showLabel && (
        <Typography variant="body2" color="text.secondary" mt={1}>
          Credit Score
        </Typography>
      )}
    </Box>
  );
};

export default ScoreGauge;