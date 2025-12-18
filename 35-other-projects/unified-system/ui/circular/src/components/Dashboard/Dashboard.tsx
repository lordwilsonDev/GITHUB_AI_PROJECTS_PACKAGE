import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Paper, Grid } from '@mui/material';
import axios from 'axios';
import LoveMeter from '../LoveMeter/LoveMeter';
import HistoryChart from '../HistoryChart/HistoryChart';
import MessageInput from '../MessageInput/MessageInput';

interface LoveQuotientData {
  love_quotient: number;
}

interface HistoryItem {
  timestamp: string;
  value: number;
  source: string;
}

interface HistoryData {
  history: HistoryItem[];
}

const Dashboard: React.FC = () => {
  const [loveQuotient, setLoveQuotient] = useState<number>(1.0);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const fetchLoveQuotient = async () => {
    try {
      const response = await axios.get<LoveQuotientData>(`${API_BASE_URL}/api/love-quotient`);
      setLoveQuotient(response.data.love_quotient);
    } catch (err) {
      console.error('Error fetching love quotient:', err);
      setError('Failed to fetch love quotient');
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get<HistoryData>(`${API_BASE_URL}/api/history?limit=50`);
      setHistory(response.data.history);
    } catch (err) {
      console.error('Error fetching history:', err);
      setError('Failed to fetch history');
    }
  };

  const handleMessageSent = async (message: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/message`, {
        message,
        user_id: 'dashboard_user'
      });
      
      if (response.data.love_quotient) {
        setLoveQuotient(response.data.love_quotient);
        // Refresh history to show the new entry
        await fetchHistory();
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchLoveQuotient(), fetchHistory()]);
      setLoading(false);
    };

    loadData();

    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchLoveQuotient();
      fetchHistory();
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Loading Love Quotient System...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography 
        variant="h3" 
        component="h1" 
        gutterBottom 
        align="center"
        sx={{ 
          background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 'bold',
          mb: 4
        }}
      >
        💖 Unified Love System
      </Typography>

      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography>{error}</Typography>
        </Paper>
      )}

      <Grid container spacing={3}>
        {/* Love Meter Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              Current Love Quotient
            </Typography>
            <LoveMeter value={loveQuotient} />
          </Paper>
        </Grid>

        {/* Message Input Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Send a Message
            </Typography>
            <MessageInput onMessageSent={handleMessageSent} />
          </Paper>
        </Grid>

        {/* History Chart Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Love Quotient History
            </Typography>
            <HistoryChart data={history} />
          </Paper>
        </Grid>

        {/* System Stats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              System Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  Total Interactions
                </Typography>
                <Typography variant="h6">
                  {history.length}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  Current Value
                </Typography>
                <Typography variant="h6">
                  {loveQuotient.toFixed(3)}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  System Status
                </Typography>
                <Typography variant="h6" color="success.main">
                  Active
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">
                  Last Update
                </Typography>
                <Typography variant="h6">
                  {history.length > 0 ? new Date(history[0].timestamp).toLocaleTimeString() : 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;