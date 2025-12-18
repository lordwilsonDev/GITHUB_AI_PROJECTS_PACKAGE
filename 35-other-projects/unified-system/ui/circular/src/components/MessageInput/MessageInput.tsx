import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Chip,
  Stack
} from '@mui/material';
import { Send as SendIcon, Favorite as FavoriteIcon } from '@mui/icons-material';

interface MessageInputProps {
  onMessageSent: (message: string) => Promise<void>;
}

const MessageInput: React.FC<MessageInputProps> = ({ onMessageSent }) => {
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastSentiment, setLastSentiment] = useState<string | null>(null);

  // Suggested love messages
  const loveMessages = [
    "I love you more than all the stars in the sky",
    "You make my heart sing with joy",
    "Your love is the light that guides me",
    "Together we create something beautiful",
    "You are my sunshine on cloudy days",
    "Our connection grows stronger every day"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || isLoading) {
      return;
    }

    setIsLoading(true);
    try {
      await onMessageSent(message.trim());
      
      // Determine sentiment for feedback
      const lowerMessage = message.toLowerCase();
      if (lowerMessage.includes('love') || lowerMessage.includes('heart') || 
          lowerMessage.includes('beautiful') || lowerMessage.includes('wonderful')) {
        setLastSentiment('positive');
      } else if (lowerMessage.includes('sad') || lowerMessage.includes('angry') || 
                 lowerMessage.includes('hate')) {
        setLastSentiment('negative');
      } else {
        setLastSentiment('neutral');
      }
      
      setMessage(''); // Clear the input
    } catch (error) {
      console.error('Error sending message:', error);
      setLastSentiment('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedMessage = (suggestedMessage: string) => {
    setMessage(suggestedMessage);
  };

  const getSentimentColor = (sentiment: string | null) => {
    switch (sentiment) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      case 'neutral': return 'info';
      case 'error': return 'error';
      default: return 'primary';
    }
  };

  const getSentimentMessage = (sentiment: string | null) => {
    switch (sentiment) {
      case 'positive': return '💖 Love detected! The system feels warmer.';
      case 'negative': return '💙 The system acknowledges your feelings.';
      case 'neutral': return '😊 Message received and processed.';
      case 'error': return '❌ Failed to send message. Please try again.';
      default: return '';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Message Input Form */}
      <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          variant="outlined"
          placeholder="Share your thoughts, feelings, or send some love to the system..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isLoading}
          sx={{ mb: 2 }}
          inputProps={{ maxLength: 500 }}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {message.length}/500 characters
          </Typography>
          
          <Button
            type="submit"
            variant="contained"
            disabled={!message.trim() || isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
            sx={{
              background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #FE6B8B 60%, #FF8E53 100%)',
              }
            }}
          >
            {isLoading ? 'Sending...' : 'Send Message'}
          </Button>
        </Box>
      </Box>

      {/* Sentiment Feedback */}
      {lastSentiment && (
        <Box sx={{ mb: 2 }}>
          <Chip
            icon={<FavoriteIcon />}
            label={getSentimentMessage(lastSentiment)}
            color={getSentimentColor(lastSentiment) as any}
            variant="outlined"
            sx={{ mb: 1 }}
          />
        </Box>
      )}

      {/* Suggested Messages */}
      <Box>
        <Typography variant="subtitle2" gutterBottom color="text.secondary">
          💡 Try these love-filled messages:
        </Typography>
        <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
          {loveMessages.slice(0, 3).map((loveMsg, index) => (
            <Chip
              key={index}
              label={loveMsg}
              variant="outlined"
              size="small"
              onClick={() => handleSuggestedMessage(loveMsg)}
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'rgba(254, 107, 139, 0.1)',
                  borderColor: '#FE6B8B'
                }
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* Instructions */}
      <Typography 
        variant="caption" 
        color="text.secondary" 
        sx={{ mt: 2, display: 'block', fontStyle: 'italic' }}
      >
        💭 The system learns from your messages and adjusts the Love Quotient based on sentiment.
        Positive, loving messages increase the quotient, while negative messages may decrease it.
      </Typography>
    </Box>
  );
};

export default MessageInput;