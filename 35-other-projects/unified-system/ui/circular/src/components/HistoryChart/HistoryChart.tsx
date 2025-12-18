import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Box, Typography } from '@mui/material';

interface HistoryItem {
  timestamp: string;
  value: number;
  source: string;
}

interface HistoryChartProps {
  data: HistoryItem[];
}

const HistoryChart: React.FC<HistoryChartProps> = ({ data }) => {
  // Prepare data for the chart
  const chartData = data
    .slice()
    .reverse() // Show oldest to newest
    .map((item, index) => ({
      ...item,
      index,
      time: new Date(item.timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      fullTime: new Date(item.timestamp).toLocaleString()
    }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          sx={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid #ccc',
            borderRadius: 1,
            p: 1,
            boxShadow: 2
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            Love Quotient: {data.value.toFixed(3)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Time: {data.fullTime}
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            Source: {data.source}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <Box 
        sx={{ 
          height: 300, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}
      >
        <Typography variant="body1" color="text.secondary">
          No history data available. Send a message to start tracking!
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            domain={[0, 2]}
            tick={{ fontSize: 12 }}
            label={{ 
              value: 'Love Quotient', 
              angle: -90, 
              position: 'insideLeft',
              style: { textAnchor: 'middle' }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Reference line at 1.0 (neutral) */}
          <ReferenceLine 
            y={1.0} 
            stroke="#666" 
            strokeDasharray="5 5" 
            label={{ value: "Neutral", position: "topRight" }}
          />
          
          {/* Main love quotient line */}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#8884d8"
            strokeWidth={3}
            dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#8884d8', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Chart Summary */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap' }}>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Current
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            {data[0]?.value.toFixed(3) || 'N/A'}
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Highest
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            {Math.max(...data.map(d => d.value)).toFixed(3)}
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Lowest
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            {Math.min(...data.map(d => d.value)).toFixed(3)}
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Average
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            {(data.reduce((sum, d) => sum + d.value, 0) / data.length).toFixed(3)}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default HistoryChart;