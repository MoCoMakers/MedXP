// Common types shared across the application

export interface UUID {
  id: string;
}

export interface Timestamps {
  createdAt: string;
  updatedAt?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Nurse types
export interface Nurse {
  id: string;
  name: string;
  email: string;
  department: string;
  shiftPattern: string;
  employeeId: string;
  status: 'active' | 'inactive';
  hireDate: string;
  certifications: string[];
  profileImageUrl?: string;
}

export interface NurseStatistics {
  totalSessions: number;
  totalTranscripts: number;
  averageRiskScore: number;
  highRiskSessions: number;
  tagsBreakdown: Record<string, number>;
}

// Patient types
export interface Patient {
  id: string;
  mrn: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: string;
  allergies: string[];
  conditions: string[];
  medications: Medication[];
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
}

// Session types
export interface Session {
  id: string;
  nurseId: string;
  patientId: string;
  startTime: string;
  endTime?: string;
  status: SessionStatus;
  sessionType: SessionType;
  department: string;
  duration?: number;
  transcriptId?: string;
}

export type SessionStatus = 'recording' | 'transcribing' | 'analyzing' | 'completed' | 'failed';

export type SessionType = 
  | 'initial_assessment'
  | 'routine_followup'
  | 'emergency'
  | 'discharge'
  | 'care_planning'
  | 'medication_review';

// Transcript types
export interface Transcript {
  id: string;
  sessionId: string;
  nurseId: string;
  patientId: string;
  text: string;
  status: TranscriptStatus;
  metadata: TranscriptMetadata;
  createdAt: string;
  processedAt?: string;
}

export type TranscriptStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface TranscriptMetadata {
  recordingDurationSeconds: number;
  recordingTimestamp: string;
  sessionType: string;
  department: string;
  additionalInfo?: Record<string, unknown>;
}

// Classification types
export interface Classification {
  id: string;
  transcriptId: string;
  tags: string[];
  categories: ClassificationCategory[];
  riskLevel: RiskLevel;
  sentiment: Sentiment;
  topics: Topic[];
  entities: EntityExtraction;
  metadata: ClassificationMetadata;
  createdAt: string;
}

export interface ClassificationCategory {
  name: string;
  confidence: number;
}

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface Sentiment {
  overall: string;
  confidence: number;
  breakdown: {
    positive: number;
    neutral: number;
    negative: number;
  };
}

export interface Topic {
  name: string;
  confidence: number;
  keyPhrases: string[];
  relevantSegments?: TextSegment[];
}

export interface TextSegment {
  startChar: number;
  endChar: number;
  text: string;
}

export interface EntityExtraction {
  medications: MedicationMention[];
  symptoms: SymptomMention[];
  procedures: string[];
  timeExpressions: TimeExpression[];
  careInstructions: string[];
}

export interface MedicationMention {
  name: string;
  dosage?: string;
  frequency?: string;
  context?: string;
  instruction?: string;
  precaution?: string;
}

export interface SymptomMention {
  term: string;
  severity?: string;
  duration?: string;
  location?: string;
  context?: string;
}

export interface TimeExpression {
  expression: string;
  parsedDuration?: string;
  parsedTimestamp?: string;
  context?: string;
}

export interface ClassificationMetadata {
  modelVersion: string;
  modelName: string;
  processingTimeMs: number;
  confidenceThreshold: number;
  pipelineVersion: string;
}

// Notification types
export interface Notification {
  id: string;
  sessionId?: string;
  nurseId?: string;
  patientId?: string;
  type: NotificationType;
  severity: NotificationSeverity;
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
  metadata?: Record<string, unknown>;
}

export type NotificationType = 
  | 'alert'
  | 'warning'
  | 'info'
  | 'action_required'
  | 'risk_assessment';

export type NotificationSeverity = 'low' | 'medium' | 'high' | 'critical';

// Job types
export interface ProcessingJob {
  id: string;
  status: JobStatus;
  progress: number;
  currentStage: string;
  startedAt: string;
  estimatedCompletion?: string;
  error?: string;
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

// API Response types
export interface ApiResponse<T> {
  status: 'success' | 'error' | 'accepted';
  data?: T;
  message?: string;
  errorCode?: string;
  details?: unknown;
  _links?: Record<string, string>;
}

export interface ErrorResponse {
  status: 'error';
  errorCode: string;
  message: string;
  details?: Array<{ field: string; message: string }>;
  requestId?: string;
}

// Dashboard types
export interface DashboardStats {
  totalNurses: number;
  totalPatients: number;
  totalSessions: number;
  activeSessions: number;
  averageRiskScore: number;
  notificationsCount: number;
  recentAlerts: Notification[];
}

export interface RiskTrend {
  date: string;
  low: number;
  medium: number;
  high: number;
  critical: number;
}
