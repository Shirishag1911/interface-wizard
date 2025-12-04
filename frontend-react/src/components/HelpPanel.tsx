/**
 * Help Panel Component for React (URS IR-3)
 *
 * This component implements the contextual help and suggestions requirement
 * from URS v2.0. It provides inline guidance on:
 * - CSV/Excel file format requirements
 * - Example commands
 * - Field mappings
 * - Common errors and solutions
 */
import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Chip,
  Paper,
  Alert,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  HelpOutline as HelpOutlineIcon,
  FileUpload as FileUploadIcon,
  ChatBubble as ChatBubbleIcon,
  SwapHoriz as SwapHorizIcon,
  ErrorOutline as ErrorOutlineIcon,
  MonitorHeart as MonitorHeartIcon,
  ArrowForward as ArrowForwardIcon,
  Lightbulb as LightbulbIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface HelpPanelProps {
  showHealthStatus?: boolean;
}

export const HelpPanel: React.FC<HelpPanelProps> = ({ showHealthStatus = true }) => {
  const requiredColumns = ['FirstName', 'LastName', 'DOB', 'Gender'];
  const optionalColumns = ['Phone', 'Email', 'Address', 'City', 'State', 'Zip', 'SSN', 'MRN'];

  const commandExamples = [
    {
      title: 'Upload a CSV file',
      command: 'Upload the attached CSV file and create patients'
    },
    {
      title: 'Create a single patient',
      command: 'Create a patient named John Doe born on March 15, 1985'
    },
    {
      title: 'Create multiple patients',
      command: 'Create 5 test patients'
    },
  ];

  const fieldMappings = [
    {
      field: 'First Name',
      variants: ['FirstName', 'first_name', 'First', 'Given Name']
    },
    {
      field: 'Last Name',
      variants: ['LastName', 'last_name', 'Last', 'Surname', 'Family Name']
    },
    {
      field: 'Date of Birth',
      variants: ['DOB', 'DateOfBirth', 'Birth Date', 'Birthdate']
    },
    {
      field: 'Gender',
      variants: ['Gender', 'Sex', 'M/F']
    },
  ];

  const commonIssues = [
    {
      problem: 'File upload fails',
      solution: 'Ensure your file is in CSV, Excel (.xlsx, .xls), or PDF format and is properly formatted'
    },
    {
      problem: 'Missing required fields',
      solution: 'Verify your file contains at least FirstName, LastName, DOB, and Gender columns'
    },
    {
      problem: 'Date format errors',
      solution: 'Use ISO format (YYYY-MM-DD) or common formats like MM/DD/YYYY for dates'
    },
    {
      problem: 'Duplicate patient records',
      solution: 'Check MRN (Medical Record Number) uniqueness before uploading'
    },
  ];

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        borderRadius: 2,
        bgcolor: 'white',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, color: '#667eea' }}>
        <HelpOutlineIcon sx={{ fontSize: 28 }} />
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Quick Help & Tips
        </Typography>
      </Box>

      {/* CSV Upload Guide */}
      <Accordion elevation={1} sx={{ mb: 1, borderRadius: '8px !important' }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FileUploadIcon sx={{ color: '#667eea' }} />
            <Typography sx={{ fontWeight: 500 }}>CSV/Excel File Format</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1, color: '#666', textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Required Columns
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {requiredColumns.map((col) => (
                <Chip key={col} label={col} size="small" color="primary" />
              ))}
            </Box>

            <Typography variant="subtitle2" sx={{ mb: 1, color: '#666', textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Optional Columns
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {optionalColumns.map((col) => (
                <Chip key={col} label={col} size="small" variant="outlined" />
              ))}
            </Box>

            <Typography variant="subtitle2" sx={{ mb: 1, color: '#666', textTransform: 'uppercase', fontSize: '0.75rem' }}>
              Example Format
            </Typography>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                mb: 2,
                bgcolor: '#f5f7fa',
                border: '1px solid #e1e8ed',
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                overflowX: 'auto',
              }}
            >
              <code>
                FirstName,LastName,DOB,Gender,Phone,Email<br />
                John,Doe,1985-03-15,M,555-0100,john@example.com<br />
                Jane,Smith,1990-07-22,F,555-0101,jane@example.com
              </code>
            </Paper>

            <Alert icon={<LightbulbIcon />} severity="info">
              <Typography variant="body2">
                <strong>Tip:</strong> You can also upload Excel (.xlsx, .xls) and PDF files!
              </Typography>
            </Alert>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Example Commands */}
      <Accordion elevation={1} sx={{ mb: 1, borderRadius: '8px !important' }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ChatBubbleIcon sx={{ color: '#667eea' }} />
            <Typography sx={{ fontWeight: 500 }}>Example Commands</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            {commandExamples.map((example, index) => (
              <Paper
                key={index}
                elevation={0}
                sx={{
                  p: 1.5,
                  mb: 1.5,
                  bgcolor: '#f8f9fa',
                  borderRadius: 1,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                  <ArrowForwardIcon sx={{ fontSize: 18, color: '#667eea' }} />
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {example.title}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ pl: 3, fontStyle: 'italic', color: '#657786' }}>
                  "{example.command}"
                </Typography>
              </Paper>
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Field Mappings */}
      <Accordion elevation={1} sx={{ mb: 1, borderRadius: '8px !important' }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SwapHorizIcon sx={{ color: '#667eea' }} />
            <Typography sx={{ fontWeight: 500 }}>CSV Field Mappings</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            <Typography variant="body2" sx={{ mb: 2 }}>
              The system automatically maps common column name variations:
            </Typography>

            {fieldMappings.map((mapping, index) => (
              <Paper
                key={index}
                elevation={0}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  p: 1.5,
                  mb: 1.5,
                  bgcolor: '#f8f9fa',
                  borderRadius: 1,
                }}
              >
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {mapping.variants.map((variant) => (
                      <Chip key={variant} label={variant} size="small" />
                    ))}
                  </Box>
                </Box>
                <ArrowForwardIcon sx={{ color: '#8899a6' }} />
                <Box sx={{ flex: 1, textAlign: 'right' }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#667eea' }}>
                    {mapping.field}
                  </Typography>
                </Box>
              </Paper>
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Common Issues */}
      <Accordion elevation={1} sx={{ mb: 1, borderRadius: '8px !important' }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ErrorOutlineIcon sx={{ color: '#667eea' }} />
            <Typography sx={{ fontWeight: 500 }}>Common Issues & Solutions</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            {commonIssues.map((issue, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                  <WarningIcon sx={{ fontSize: 20, color: '#d32f2f' }} />
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#d32f2f' }}>
                    {issue.problem}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, pl: 3.5 }}>
                  <CheckCircleIcon sx={{ fontSize: 18, color: '#4caf50' }} />
                  <Typography variant="body2" sx={{ color: '#333' }}>
                    {issue.solution}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* System Status */}
      {showHealthStatus && (
        <Accordion elevation={1} sx={{ borderRadius: '8px !important' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <MonitorHeartIcon sx={{ color: '#667eea' }} />
              <Typography sx={{ fontWeight: 500 }}>System Status</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Paper
                elevation={0}
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1.5,
                  p: 2,
                  mb: 2,
                  bgcolor: '#f5f7fa',
                  borderRadius: 1,
                }}
              >
                <InfoIcon sx={{ color: '#667eea' }} />
                <Typography variant="body2">
                  Real-time connectivity status indicators show whether Mirth Connect and OpenEMR are available.
                </Typography>
              </Paper>

              <Box>
                {[
                  { status: 'healthy', color: '#4caf50', label: 'Healthy - All systems operational' },
                  { status: 'degraded', color: '#ff9800', label: 'Degraded - Partial functionality' },
                  { status: 'unhealthy', color: '#f44336', label: 'Unhealthy - System unavailable' },
                ].map((item) => (
                  <Box
                    key={item.status}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1.5,
                      mb: 1,
                    }}
                  >
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        bgcolor: item.color,
                      }}
                    />
                    <Typography variant="body2">{item.label}</Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}
    </Paper>
  );
};

export default HelpPanel;
