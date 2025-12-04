/**
 * Confirmation Dialog Component for React (URS FR-3)
 *
 * This component implements the confirmation dialog requirement from URS v2.0.
 * It shows a preview of bulk operations before execution, allowing users to
 * review and confirm or cancel the operation.
 */
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  Chip,
  Divider,
  Paper,
  Alert,
} from '@mui/material';
import {
  Preview as PreviewIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon,
  Cake as CakeIcon,
  Wc as WcIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
} from '@mui/icons-material';

export interface PatientPreview {
  name: string;
  mrn?: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface ConfirmationDialogData {
  preview_id: string;
  operation_type: string;
  total_records: number;
  preview_records: PatientPreview[];
  validation_warnings: string[];
  estimated_time_seconds?: number;
  message: string;
}

interface ConfirmationDialogProps {
  open: boolean;
  data: ConfirmationDialogData | null;
  onConfirm: (previewId: string) => void;
  onCancel: () => void;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  data,
  onConfirm,
  onCancel,
}) => {
  if (!data) return null;

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  };

  const handleConfirm = () => {
    onConfirm(data.preview_id);
  };

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          maxHeight: '90vh',
        }
      }}
    >
      {/* Header */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          p: 2,
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            p: 0,
            color: 'inherit',
          }}
        >
          <PreviewIcon sx={{ fontSize: 28 }} />
          <Typography variant="h5" component="span">
            Confirm Operation
          </Typography>
        </DialogTitle>
      </Box>

      <DialogContent sx={{ p: 3 }}>
        {/* Message */}
        <Typography variant="body1" sx={{ mb: 3, fontSize: '1.1rem', color: '#333' }}>
          {data.message}
        </Typography>

        {/* Summary Stats */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Paper
            elevation={0}
            sx={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              p: 2,
              bgcolor: '#f5f7fa',
              border: '1px solid #e1e8ed',
              borderRadius: 2,
            }}
          >
            <PersonIcon sx={{ color: '#667eea', fontSize: 32 }} />
            <Box>
              <Typography variant="caption" sx={{ color: '#8899a6', textTransform: 'uppercase' }}>
                Total Records
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {data.total_records}
              </Typography>
            </Box>
          </Paper>

          {data.estimated_time_seconds && (
            <Paper
              elevation={0}
              sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                p: 2,
                bgcolor: '#f5f7fa',
                border: '1px solid #e1e8ed',
                borderRadius: 2,
              }}
            >
              <ScheduleIcon sx={{ color: '#667eea', fontSize: 32 }} />
              <Box>
                <Typography variant="caption" sx={{ color: '#8899a6', textTransform: 'uppercase' }}>
                  Estimated Time
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {formatTime(data.estimated_time_seconds)}
                </Typography>
              </Box>
            </Paper>
          )}
        </Box>

        {/* Validation Warnings */}
        {data.validation_warnings && data.validation_warnings.length > 0 && (
          <Alert
            severity="warning"
            icon={<WarningIcon />}
            sx={{ mb: 3 }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              Warnings
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {data.validation_warnings.map((warning, index) => (
                <Chip
                  key={index}
                  label={warning}
                  size="small"
                  color="warning"
                  variant="outlined"
                />
              ))}
            </Box>
          </Alert>
        )}

        {/* Preview Records */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <VisibilityIcon sx={{ color: '#667eea' }} />
            <Typography variant="h6">
              Preview (First {data.preview_records.length} of {data.total_records})
            </Typography>
          </Box>

          <List sx={{ p: 0 }}>
            {data.preview_records.map((patient, index) => (
              <Paper
                key={index}
                elevation={0}
                sx={{
                  mb: 2,
                  p: 2,
                  bgcolor: '#f8f9fa',
                  border: '1px solid #e1e8ed',
                  borderRadius: 2,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    borderColor: '#667eea',
                  },
                }}
              >
                {/* Patient Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 28,
                      height: 28,
                      bgcolor: '#667eea',
                      color: 'white',
                      borderRadius: '50%',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                    }}
                  >
                    {index + 1}
                  </Box>
                  <Typography variant="subtitle1" sx={{ flex: 1, fontWeight: 600 }}>
                    {patient.name}
                  </Typography>
                  {patient.mrn && (
                    <Chip label={`MRN: ${patient.mrn}`} size="small" />
                  )}
                </Box>

                {/* Patient Details */}
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: 1,
                    pl: 5,
                  }}
                >
                  {patient.date_of_birth && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.875rem', color: '#657786' }}>
                      <CakeIcon sx={{ fontSize: 18, color: '#8899a6' }} />
                      <Typography variant="body2">DOB: {patient.date_of_birth}</Typography>
                    </Box>
                  )}
                  {patient.gender && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.875rem', color: '#657786' }}>
                      <WcIcon sx={{ fontSize: 18, color: '#8899a6' }} />
                      <Typography variant="body2">{patient.gender}</Typography>
                    </Box>
                  )}
                  {patient.phone && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.875rem', color: '#657786' }}>
                      <PhoneIcon sx={{ fontSize: 18, color: '#8899a6' }} />
                      <Typography variant="body2">{patient.phone}</Typography>
                    </Box>
                  )}
                  {patient.email && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.875rem', color: '#657786' }}>
                      <EmailIcon sx={{ fontSize: 18, color: '#8899a6' }} />
                      <Typography variant="body2">{patient.email}</Typography>
                    </Box>
                  )}
                </Box>
              </Paper>
            ))}
          </List>

          {data.total_records > data.preview_records.length && (
            <Typography
              variant="body2"
              sx={{
                textAlign: 'center',
                color: '#8899a6',
                fontStyle: 'italic',
                mt: 2,
              }}
            >
              ...and {data.total_records - data.preview_records.length} more record(s)
            </Typography>
          )}
        </Box>
      </DialogContent>

      {/* Actions */}
      <Divider />
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button
          onClick={onCancel}
          variant="outlined"
          color="error"
          startIcon={<CancelIcon />}
        >
          Cancel
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          color="primary"
          startIcon={<CheckCircleIcon />}
        >
          Confirm and Proceed
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;
