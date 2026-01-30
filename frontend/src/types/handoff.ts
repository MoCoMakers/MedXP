export interface Patient {
  id: string;
  name: string;
  room: string;
  mrn: string;
  age: number;
  gender: string;
}

export interface HandoffRecording {
  id: string;
  patientId: string;
  audioBlob?: Blob;
  transcript: string;
  duration: number;
  createdAt: Date;
  status: 'recording' | 'processing' | 'complete';
}

export interface SBARCard {
  id: string;
  patientId: string;
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
  transcript: string;
  entities: TranscriptEntity[];
  tasks: Task[];
  risks: Risk[];
  missingInfo: MissingInfo[];
  status: 'new' | 'acknowledged' | 'in_progress' | 'completed';
  createdAt: Date;
  lockedAt?: Date;
}

export interface TranscriptEntity {
  text: string;
  type: 'medication' | 'vital' | 'lab' | 'time';
  start: number;
  end: number;
}

export interface Task {
  id: string;
  text: string;
  dueTime?: string;
  completed: boolean;
}

export interface Risk {
  id: string;
  title: string;
  rationale: string;
  severity: 'high' | 'medium' | 'low';
}

export interface MissingInfo {
  id: string;
  item: string;
  checked: boolean;
}

export type IncomingRole = 'RN' | 'Intern' | 'Resident' | 'Attending';
export type ShiftContext = 'ED → Floor' | 'ICU → Floor' | 'OR → PACU' | 'Floor → Floor';
