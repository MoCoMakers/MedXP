import { Patient, SBARCard, Task, Risk, MissingInfo, TranscriptEntity } from '@/types/handoff';

export const mockPatients: Patient[] = [
  {
    id: '1',
    name: 'Johnson, Mary',
    room: '412A',
    mrn: 'MRN-78432',
    age: 67,
    gender: 'F',
  },
  {
    id: '2',
    name: 'Chen, Robert',
    room: '418B',
    mrn: 'MRN-91205',
    age: 52,
    gender: 'M',
  },
  {
    id: '3',
    name: 'Williams, Sarah',
    room: '421',
    mrn: 'MRN-65891',
    age: 34,
    gender: 'F',
  },
];

export const mockTranscript = `Patient Mary Johnson, 67-year-old female admitted from ED with community-acquired pneumonia. She's been on Levaquin 750mg IV daily since admission yesterday. Vitals have been stable with temp trending down from 39.2 to 37.8 this morning. BP 128/78, heart rate 92, O2 sat 94% on 2L nasal cannula. 

Labs from this morning show WBC 14.2, down from 18.5 yesterday. BMP was unremarkable, creatinine stable at 1.1. Lactate pending from 8am draw. 

She has a history of COPD, hypertension, and type 2 diabetes. Home meds include metformin, lisinopril, and albuterol inhaler PRN. She's allergic to penicillin - causes rash.

Current assessment is improving pneumonia, responding to antibiotics. Continue current antibiotic course. Watch for any signs of sepsis - she did have elevated lactate initially at 2.8. Repeat lactate should be back soon. 

Tasks for next shift: check lactate result, continue q4h vitals, reassess oxygen requirements, and confirm she can transition to oral antibiotics if continues to improve. She's DNR/DNI per discussion with family yesterday.`;

export const mockEntities: TranscriptEntity[] = [
  { text: 'Levaquin 750mg', type: 'medication', start: 142, end: 156 },
  { text: '39.2', type: 'vital', start: 215, end: 219 },
  { text: '37.8', type: 'vital', start: 223, end: 227 },
  { text: 'BP 128/78', type: 'vital', start: 242, end: 251 },
  { text: 'heart rate 92', type: 'vital', start: 253, end: 266 },
  { text: 'O2 sat 94%', type: 'vital', start: 268, end: 278 },
  { text: 'WBC 14.2', type: 'lab', start: 325, end: 333 },
  { text: '18.5', type: 'lab', start: 348, end: 352 },
  { text: 'creatinine stable at 1.1', type: 'lab', start: 382, end: 406 },
  { text: '8am', type: 'time', start: 429, end: 432 },
  { text: 'metformin', type: 'medication', start: 530, end: 539 },
  { text: 'lisinopril', type: 'medication', start: 541, end: 551 },
  { text: 'albuterol', type: 'medication', start: 557, end: 566 },
  { text: 'lactate initially at 2.8', type: 'lab', start: 751, end: 775 },
  { text: 'q4h', type: 'time', start: 856, end: 859 },
];

export const mockTasks: Task[] = [
  { id: '1', text: 'Check lactate result', dueTime: '10:00 AM', completed: false },
  { id: '2', text: 'Continue q4h vitals', completed: false },
  { id: '3', text: 'Reassess oxygen requirements', dueTime: '2:00 PM', completed: false },
  { id: '4', text: 'Evaluate for PO antibiotics transition', dueTime: 'If improving', completed: false },
];

export const mockRisks: Risk[] = [
  {
    id: '1',
    title: 'Sepsis risk',
    rationale: 'Lactate pending, initial lactate 2.8, temp 39.2°C on admission, HR elevated',
    severity: 'high',
  },
  {
    id: '2',
    title: 'Respiratory decompensation',
    rationale: 'On supplemental O2, history of COPD, active pneumonia',
    severity: 'medium',
  },
];

export const mockMissingInfo: MissingInfo[] = [
  { id: '1', item: 'Allergies documented', checked: true },
  { id: '2', item: 'Code status confirmed', checked: true },
  { id: '3', item: 'Lines/drains/wounds', checked: false },
  { id: '4', item: 'Isolation precautions', checked: false },
  { id: '5', item: 'Fall risk assessment', checked: false },
];

export const mockSBARCards: SBARCard[] = [
  {
    id: '1',
    patientId: '1',
    situation: '67F with community-acquired pneumonia admitted from ED yesterday, currently improving on IV antibiotics with downtrending fever and WBC.',
    background: 'PMH: COPD, HTN, T2DM. Home meds: metformin, lisinopril, albuterol PRN. Allergic to penicillin (rash). DNR/DNI.',
    assessment: 'Improving pneumonia. Vitals stable: T 37.8°C, BP 128/78, HR 92, O2 sat 94% on 2L NC. Labs: WBC 14.2 (↓ from 18.5), Cr 1.1, lactate pending.',
    recommendation: 'Continue Levaquin, q4h vitals, reassess O2 needs, check pending lactate, evaluate for PO transition if continues improving.',
    transcript: mockTranscript,
    entities: mockEntities,
    tasks: mockTasks,
    risks: mockRisks,
    missingInfo: mockMissingInfo,
    status: 'new',
    createdAt: new Date(),
  },
  {
    id: '2',
    patientId: '2',
    situation: '52M post-CABG day 2, hemodynamically stable, pain controlled, ready for step-down.',
    background: 'PMH: CAD, hyperlipidemia. 3-vessel CABG performed 2 days ago. No allergies.',
    assessment: 'Stable post-op course. Vitals: T 37.2°C, BP 118/72, HR 78, O2 sat 98% RA. Labs: Hgb 9.8, Cr 0.9.',
    recommendation: 'Continue current plan, advance diet, PT evaluation, monitor for arrhythmias.',
    transcript: 'Post-CABG day 2 patient...',
    entities: [],
    tasks: [
      { id: '1', text: 'PT evaluation', dueTime: '11:00 AM', completed: false },
      { id: '2', text: 'Advance diet as tolerated', completed: false },
    ],
    risks: [
      { id: '1', title: 'Post-op bleeding', rationale: 'Day 2 post-CABG, on anticoagulation', severity: 'medium' },
    ],
    missingInfo: [],
    status: 'acknowledged',
    createdAt: new Date(Date.now() - 3600000),
  },
  {
    id: '3',
    patientId: '3',
    situation: '34F with acute appendicitis, post-laparoscopic appendectomy, ready for discharge.',
    background: 'No significant PMH. No allergies. Lives alone, has ride home arranged.',
    assessment: 'Uncomplicated post-op course. Tolerating PO, ambulating, pain controlled with PO meds.',
    recommendation: 'Discharge with prescriptions, follow-up in 1 week, return precautions given.',
    transcript: 'Post-appendectomy patient...',
    entities: [],
    tasks: [
      { id: '1', text: 'Complete discharge paperwork', completed: true },
      { id: '2', text: 'Pharmacy to deliver meds', completed: false },
    ],
    risks: [],
    missingInfo: [],
    status: 'in_progress',
    createdAt: new Date(Date.now() - 7200000),
  },
];
