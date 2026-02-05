import * as React from "react";
import { useNavigate } from "react-router-dom";
import { RecordButton } from "@/components/ui/record-button";
import { AnimatedWaveform } from "@/components/ui/waveform";
import { PatientSelector } from "@/components/record/PatientSelector";
import { RecordingControls } from "@/components/record/RecordingControls";
import { TranscriptPreview } from "@/components/record/TranscriptPreview";
import { RecordTimer } from "@/components/record/RecordTimer";
import { mockPatients } from "@/data/mockData";
import { IncomingRole, ShiftContext } from "@/types/handoff";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { useAudioRecorder } from "@/hooks/use-audio-recorder";
import { useToast } from "@/hooks/use-toast";
import { transcriptionApi } from "@/lib/api";

export default function RecordHandoff() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [selectedPatientId, setSelectedPatientId] = React.useState<string | null>(null);
  const [incomingRole, setIncomingRole] = React.useState<IncomingRole>("RN");
  const [shiftContext, setShiftContext] = React.useState<ShiftContext>("ED → Floor");
  const [isProcessing, setIsProcessing] = React.useState(false);
  const [transcript, setTranscript] = React.useState("");
  
  const { isRecording, audioBlob, startRecording, stopRecording, error } = useAudioRecorder();

  // Handle recording errors
  React.useEffect(() => {
    if (error) {
      toast({
        title: "Recording Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  // Send audio to backend when recording stops
  React.useEffect(() => {
    if (audioBlob && !isRecording) {
      console.log("Recording complete! Audio blob size:", audioBlob.size, "bytes");
      console.log("Audio blob type:", audioBlob.type);
      
      // Send to backend for saving and transcription
      transcribeAudio(audioBlob);
    }
  }, [audioBlob, isRecording]);

  const transcribeAudio = async (blob: Blob) => {
    setIsProcessing(true);
    
    try {
      const data = await transcriptionApi.transcribe({
        audio: blob,
        patientId: selectedPatientId || undefined,
        incomingRole,
        shiftContext,
      });

      if (data.success && data.transcript) {
        setTranscript(data.transcript);

        toast({
          title: "Success",
          description: `Audio saved as ${data.audio_file}. Transcription complete.`,
        });
      } else {
        const msg = data.message || data.error || "Transcription failed.";
        console.error("Transcription failed:", msg);
        toast({
          title: "Transcription Failed",
          description: msg,
          variant: "destructive",
        });
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { message?: string; error?: string } }; message?: string };
      const msg =
        axiosErr?.response?.data?.message ||
        axiosErr?.response?.data?.error ||
        (err instanceof Error ? err.message : "Transcription service error. Please try again.");
      console.error("Transcription error:", err);
      toast({
        title: "Transcription Error",
        description: msg,
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRecordStart = async () => {
    if (!selectedPatientId) return;
    setTranscript("");
    await startRecording();
  };

  const handleRecordStop = () => {
    stopRecording();
  };

  const handleContinue = () => {
    navigate("/handoff/1");
  };

  return (
    <div className="bg-background">
      <div className="container max-w-2xl py-8 px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-foreground">Record Handoff</h1>
          <p className="text-muted-foreground mt-1">
            Select a patient and hold to record your handoff
          </p>
        </div>

        {/* Controls */}
        <div className="space-y-4 mb-8">
          <PatientSelector
            patients={mockPatients}
            selectedPatientId={selectedPatientId}
            onSelectPatient={setSelectedPatientId}
          />
          <RecordingControls
            incomingRole={incomingRole}
            shiftContext={shiftContext}
            onRoleChange={setIncomingRole}
            onContextChange={setShiftContext}
          />
        </div>

        {/* Recording Area */}
        <div className="flex flex-col items-center py-8 mb-8">
          {/* Waveform */}
          <AnimatedWaveform isActive={isRecording} className="mb-4 w-full max-w-md" />
          
          {/* Timer */}
          <RecordTimer isRecording={isRecording} className="mb-8" />
          
          {/* Record Button */}
          <RecordButton
            isRecording={isRecording}
            onRecordStart={handleRecordStart}
            onRecordStop={handleRecordStop}
            disabled={!selectedPatientId || isProcessing}
          />
          
          {!selectedPatientId && (
            <p className="mt-16 text-sm text-muted-foreground">
              Select a patient to start recording
            </p>
          )}
        </div>

        {/* Transcript Preview */}
        <TranscriptPreview transcript={transcript} isProcessing={isProcessing} />

        {/* Continue Button */}
        {transcript && !isProcessing && (
          <div className="mt-6 flex justify-center animate-slide-up">
            <Button onClick={handleContinue} size="lg" className="gap-2">
              View Handoff Card
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
