import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

interface LoveMeterProps {
  value: number;
}

const StyledLinearProgress = styled(LinearProgress)(({ theme, value }) => ({
  height: 20,
  borderRadius: 10,
  backgroundColor: theme.palette.grey[300],
  '& .MuiLinearProgress-bar': {
    borderRadius: 10,
    background: value < 0.5 
      ? 'linear-gradient(90deg, #2196F3 0%, #21CBF3 100%)'  // Cold - Blue
      : value < 1.0
      ? 'linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%)'  // Neutral - Green
      : value < 1.5
      ? 'linear-gradient(90deg, #FF9800 0%, #FFC107 100%)'  // Warm - Orange
      : 'linear-gradient(90deg, #F44336 0%, #E91E63 100%)', // Radiant - Red/Pink
  },
}));

const LoveMeter: React.FC<LoveMeterProps> = ({ value }) => {
  // Normalize value for display (0-2 range mapped to 0-100%)
  const normalizedValue = Math.max(0, Math.min(200, value * 100));
  const displayValue = Math.max(0, Math.min(2, value));

  const getStatusText = (val: number): string => {
    if (val < 0.5) return 'Cold ❄️';
    if (val < 1.0) return 'Neutral 😐';
    if (val < 1.5) return 'Warm 😊';
    return 'Radiant 🔥';
  };

  const getStatusColor = (val: number): string => {
    if (val < 0.5) return '#2196F3';
    if (val < 1.0) return '#4CAF50';
    if (val < 1.5) return '#FF9800';
    return '#F44336';
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      mt: 2,
      width: '100%'
    }}>
      {/* Main Love Quotient Display */}
      <Typography 
        variant="h3" 
        sx={{ 
          fontWeight: 'bold',
          color: getStatusColor(displayValue),
          mb: 1,
          textShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}
      >
        {displayValue.toFixed(3)}
      </Typography>

      {/* Progress Bar */}
      <Box sx={{ width: '100%', maxWidth: 300, mb: 2 }}>
        <StyledLinearProgress 
          variant="determinate" 
          value={normalizedValue} 
          sx={{ mb: 1 }}
        />
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="caption" color="text.secondary">
            0.0
          </Typography>
          <Typography variant="caption" color="text.secondary">
            2.0
          </Typography>
        </Box>
      </Box>

      {/* Status Text */}
      <Typography 
        variant="h6" 
        sx={{ 
          color: getStatusColor(displayValue),
          fontWeight: 'medium',
          mb: 1
        }}
      >
        {getStatusText(displayValue)}
      </Typography>

      {/* Description */}
      <Typography 
        variant="body2" 
        color="text.secondary" 
        align="center"
        sx={{ maxWidth: 250 }}
      >
        {displayValue < 0.5 
          ? "The system feels distant. Send some love to warm it up!"
          : displayValue < 1.0
          ? "The system is balanced and stable."
          : displayValue < 1.5
          ? "The system is feeling the love! Keep it flowing."
          : "The system is radiating with love and joy! ✨"}
      </Typography>

      {/* Pulse Animation for High Values */}
      {displayValue > 1.5 && (
        <Box
          sx={{
            position: 'absolute',
            width: 100,
            height: 100,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(244,67,54,0.3) 0%, rgba(244,67,54,0) 70%)',
            animation: 'pulse 2s infinite',
            '@keyframes pulse': {
              '0%': {
                transform: 'scale(0.8)',
                opacity: 1,
              },
              '50%': {
                transform: 'scale(1.2)',
                opacity: 0.5,
              },
              '100%': {
                transform: 'scale(0.8)',
                opacity: 1,
              },
            },
          }}
        />
      )}
    </Box>
  );
};

export default LoveMeter;