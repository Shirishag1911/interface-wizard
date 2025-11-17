/**
 * Chat Message Component
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Alert,
  AlertTitle,
  Collapse,
} from '@mui/material';
import {
  Person,
  SmartToy,
  CheckCircle,
  Error,
  Warning,
} from '@mui/icons-material';
import { Message } from '../types';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';
  const isSuccess = message.type === 'success';

  const getBackgroundColor = () => {
    if (isUser) return '#1976d2';
    if (isError) return '#d32f2f';
    if (isSuccess) return '#2e7d32';
    return '#424242';
  };

  const getIcon = () => {
    if (isUser) return <Person />;
    if (isError) return <Error />;
    if (isSuccess) return <CheckCircle />;
    return <SmartToy />;
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={2}
        sx={{
          maxWidth: '75%',
          backgroundColor: isUser ? getBackgroundColor() : 'background.paper',
          color: isUser ? 'white' : 'text.primary',
          p: 2,
          borderRadius: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Box sx={{ mr: 1 }}>{getIcon()}</Box>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </Typography>
        </Box>

        <Box sx={{ whiteSpace: 'pre-wrap' }}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </Box>

        {message.operation && (
          <Box sx={{ mt: 2 }}>
            <Alert
              severity={
                message.operation.status === 'success'
                  ? 'success'
                  : message.operation.status === 'failed'
                  ? 'error'
                  : message.operation.status === 'partial_success'
                  ? 'warning'
                  : 'info'
              }
              sx={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
            >
              <AlertTitle>Operation Details</AlertTitle>
              <Typography variant="body2">
                Status: <strong>{message.operation.status}</strong>
              </Typography>
              <Typography variant="body2">
                Records Affected: {message.operation.records_affected} (
                {message.operation.records_succeeded} succeeded,{' '}
                {message.operation.records_failed} failed)
              </Typography>
              {message.operation.protocol_used && (
                <Chip
                  label={message.operation.protocol_used.toUpperCase()}
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
              {message.operation.errors && message.operation.errors.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="error">
                    Errors:
                  </Typography>
                  {message.operation.errors.slice(0, 3).map((err, idx) => (
                    <Typography key={idx} variant="caption" display="block">
                      • {err}
                    </Typography>
                  ))}
                </Box>
              )}
            </Alert>
          </Box>
        )}
      </Paper>
    </Box>
  );
};
