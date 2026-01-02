import { useState, useCallback } from 'react';
import { X, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { StepIndicator } from './StepIndicator';
import { UploadStep } from './wizard-steps/UploadStep';
import { ParseStep } from './wizard-steps/ParseStep';
import { SelectPatientsStep } from './wizard-steps/SelectPatientsStep';
import { CreateHL7Step } from './wizard-steps/CreateHL7Step';
import { PushToEMRStep } from './wizard-steps/PushToEMRStep';
import { CompleteStep } from './wizard-steps/CompleteStep';
import { toast } from 'sonner';
import API_ENDPOINTS from '../services/api';

export interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: string;
  mrn: string;
  ssn?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  phone?: string;
}

export interface ValidationIssue {
  type: 'error' | 'warning' | 'info';
  field?: string;
  message: string;
  patientId?: string;
  line?: number;
}

const STEPS = [
  { id: 1, name: 'Upload CSV', description: 'Select your file' },
  { id: 2, name: 'Select Patients', description: 'Review & select' },
  { id: 3, name: 'Create HL7', description: 'Generate messages' },
  { id: 4, name: 'Push to EMR', description: 'Send to OpenEMR' },
  { id: 5, name: 'Complete', description: 'View results' },
];

interface UploadWizardProps {
  onClose: () => void;
  onComplete: (messages: string[]) => void;
}

export function UploadWizard({ onClose, onComplete }: UploadWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatients, setSelectedPatients] = useState<Patient[]>([]);
  const [hl7Messages, setHL7Messages] = useState<string[]>([]);
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);  // Store session ID


  // Normalize patient data for consistency
  function normalizePatients(apiPatients: any[]): Patient[] {
    return apiPatients.map((p, index) => {
      // Backend v3.0 format: {firstName, lastName, dateOfBirth, gender, mrn, uuid, ...}
      return {
        id: p.uuid ?? p.id ?? `patient-${index}`, // v3.0 uses uuid
        firstName: p.firstName?.trim() ?? '',
        lastName: p.lastName?.trim() ?? '',
        dateOfBirth: p.dateOfBirth ?? '',
        gender: p.gender ?? '',
        mrn: p.mrn ?? '',
        ssn: p.ssn ?? undefined,
        address: p.address ?? undefined,
        city: p.city ?? undefined,
        state: p.state ?? undefined,
        zip: p.zip?.padStart(5, '0') ?? undefined,
        phone: p.phone ?? undefined,
      };
    });
  }

    const addValidationIssue = useCallback((issue: ValidationIssue) => {
    setValidationIssues(prev => [...prev, issue]);
    if (issue.type === 'error') {
      toast.error(issue.message);
    } else if (issue.type === 'warning') {
      toast.warning(issue.message);
    } else {
      toast.info(issue.message);
    }
  }, []);

  const clearValidationIssues = useCallback(() => {
    setValidationIssues([]);
  }, []);

  // Move to next step
  const handleNext = useCallback(() => {
    setCurrentStep(prev => Math.min(prev + 1, STEPS.length));
    clearValidationIssues();
  }, [clearValidationIssues]);

  // Handle file upload and backend interaction
  const handleFileUpload = useCallback(async (file: File) => {
    clearValidationIssues();
    
    // Validate file size
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      addValidationIssue({
        type: 'error',
        message: `File size exceeds maximum allowed size (10MB).`,
      });
      return;
    }

    // Validate file type (CSV)
    if (!file.name.toLowerCase().endsWith('.csv')) {
      addValidationIssue({
        type: 'error',
        message: 'Invalid file format. Please upload a CSV file.',
      });
      return;
    }

    setCsvFile(file);
    addValidationIssue({
      type: 'info',
      message: `File "${file.name}" uploaded successfully.`,
    });

    // Send the file to API for processing
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(API_ENDPOINTS.upload, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload the file');
      }

      const data = await response.json();
      // Backend v3.0 returns session_id and patients array
      setSessionId(data.session_id);  // Store the session_id for later use
      // Backend v3.0 returns patients array directly
      const normalizedPatients = normalizePatients(data.patients || []);
      setPatients(normalizedPatients);

      addValidationIssue({
        type: 'info',
        message: `File "${file.name}" processed successfully. Found ${data.valid_records || normalizedPatients.length} valid patient records out of ${data.total_records || normalizedPatients.length} total.`,
      });
      handleNext();
    } catch (error: any) {
      addValidationIssue({
        type: 'error',
        message: `Error uploading file: ${error.message}`,
      });
    }
  }, [clearValidationIssues, addValidationIssue, handleNext]);

  // Handle patient selection and confirmation with the second API
  const handlePatientsSelected = useCallback(async (selected: Patient[]) => {
    clearValidationIssues();
    
    if (selected.length === 0) {
      addValidationIssue({
        type: 'error',
        message: 'Please select at least one patient to continue',
      });
      return;
    }

    setSelectedPatients(selected);
    addValidationIssue({
      type: 'info',
      message: `${selected.length} patient(s) selected for HL7 message creation`,
    });
    handleNext();

    if (!sessionId) {
      addValidationIssue({
        type: 'error',
        message: 'Session ID is missing. Please upload the file again.',
      });
      return;
    }

    // Prepare selected patient indices
    const selectedIndices = selected.map(patient => patients.indexOf(patient));

    try {
      const response = await fetch(API_ENDPOINTS.confirm, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,          // Backend v3.0 expects session_id
          selected_indices: selectedIndices,  // Array of indices to process
          send_to_mirth: true,            // Send to Mirth Connect
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to confirm the selection');
      }

      const data = await response.json();
      addValidationIssue({
        type: 'info',
        message: `Successfully processed ${data.processed_count || selected.length} patients and sent to Mirth!`,
      });
    } catch (error: any) {
      addValidationIssue({
        type: 'error',
        message: `Error confirming selection: ${error.message}`,
      });
    }
  }, [sessionId, patients, clearValidationIssues, handleNext, addValidationIssue]);

  // Handle HL7 message creation
  const handleHL7Created = useCallback((messages: string[]) => {
    clearValidationIssues();
    
    if (messages.length === 0) {
      addValidationIssue({
        type: 'error',
        message: 'Failed to generate HL7 messages',
      });
      return;
    }

    setHL7Messages(messages);
    addValidationIssue({
      type: 'info',
      message: `Successfully generated ${messages.length} HL7 messages.`,
    });
    handleNext();
  }, [clearValidationIssues, handleNext, addValidationIssue]);

  // Handle pushing to EMR
  const handlePushedToEMR = useCallback(() => {
    clearValidationIssues();
    addValidationIssue({
      type: 'info',
      message: `Successfully pushed ${hl7Messages.length} message(s) to OpenEMR`,
    });
    handleNext();
  }, [clearValidationIssues, handleNext, addValidationIssue, hl7Messages.length]);

  // Handle completion of the process
  const handleComplete = useCallback(() => {
    onComplete(hl7Messages);
  }, [onComplete, hl7Messages]);

  const errors = validationIssues.filter(i => i.type === 'error');
  const warnings = validationIssues.filter(i => i.type === 'warning');
  const infos = validationIssues.filter(i => i.type === 'info');



return (
  <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="text-white">Interface Wizard</h2>
            <p className="text-blue-100 text-sm">
              Step {currentStep} of {STEPS.length}: {STEPS[currentStep - 1].name}
            </p>
          </div>
          {/* Status Indicators */}
          <div className="flex items-center gap-2">
            {errors.length > 0 && (
              <div className="flex items-center gap-1 bg-red-500/20 text-white px-3 py-1 rounded-full text-sm">
                <AlertTriangle className="w-4 h-4" />
                <span>{errors.length}</span>
              </div>
            )}
            {warnings.length > 0 && (
              <div className="flex items-center gap-1 bg-yellow-500/20 text-white px-3 py-1 rounded-full text-sm">
                <AlertTriangle className="w-4 h-4" />
                <span>{warnings.length}</span>
              </div>
            )}
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Step Indicator */}
      <div className="px-6 py-4 border-b bg-slate-50">
        <StepIndicator steps={STEPS} currentStep={currentStep} />
      </div>

      {/* Validation Issues Panel */}
      {validationIssues.length > 0 && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="border-b bg-slate-50"
        >
          <div className="px-6 py-3 max-h-32 overflow-y-auto">
            <div className="space-y-2">
              {validationIssues.slice(-5).map((issue, index) => (
                <motion.div
                  key={index}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className={`flex items-start gap-2 text-sm p-2 rounded ${
                    issue.type === 'error'
                      ? 'bg-red-50 text-red-800'
                      : issue.type === 'warning'
                      ? 'bg-yellow-50 text-yellow-800'
                      : 'bg-blue-50 text-blue-800'
                  }`}
                >
                  {issue.type === 'error' && <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {issue.type === 'warning' && <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  {issue.type === 'info' && <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                  <div className="flex-1">
                    {issue.field && <span className="font-semibold">{issue.field}: </span>}
                    <span>{issue.message}</span>
                    {issue.line && <span className="text-xs ml-2">(Line {issue.line})</span>}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence mode="wait">
          {/* Dynamic Step Content */}
          {currentStep === 1 && (
            <UploadStep key="upload" onFileUpload={handleFileUpload} />
          )}
          {currentStep === 2 && (
            <SelectPatientsStep
              key="select"
              patients={patients}
              onSelected={handlePatientsSelected}
            />
          )}
          {currentStep === 3 && (
            <CreateHL7Step
              key="create"
              patients={selectedPatients}
              onCreated={handleHL7Created}
            />
          )}
          {currentStep === 4 && (
            <PushToEMRStep
              key="push"
              messages={hl7Messages}
              onPushed={handlePushedToEMR}
            />
          )}
          {currentStep === 5 && (
            <CompleteStep
              key="complete"
              patientCount={selectedPatients.length}
              messageCount={hl7Messages.length}
              onComplete={handleComplete}
            />
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  </div>
);

}
