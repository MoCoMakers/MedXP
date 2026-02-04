import axios from "axios";

const TRANSCRIBE_BASE = import.meta.env.VITE_TRANSCRIBE_URL || "http://localhost:8000";

export interface TranscribeParams {
  audio: Blob;
  patientId?: string;
  incomingRole?: string;
  shiftContext?: string;
}

export interface TranscribeResponse {
  success: boolean;
  transcript?: string;
  audio_file?: string;
  message?: string;
  error?: string;
}

export const transcriptionApi = {
  async transcribe(params: TranscribeParams): Promise<TranscribeResponse> {
    const formData = new FormData();
    formData.append("audio", params.audio);
    if (params.patientId) formData.append("patient_id", params.patientId);
    if (params.incomingRole) formData.append("incoming_role", params.incomingRole);
    if (params.shiftContext) formData.append("shift_context", params.shiftContext);

    const { data } = await axios.post<TranscribeResponse>(
      `${TRANSCRIBE_BASE}/api/transcribe`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
      }
    );
    return data;
  },
};
