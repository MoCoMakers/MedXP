import * as React from "react";
import { cn } from "@/lib/utils";
import { Mic } from "lucide-react";

interface RecordButtonProps {
  isRecording: boolean;
  onRecordStart: () => void;
  onRecordStop: () => void;
  disabled?: boolean;
}

export function RecordButton({
  isRecording,
  onRecordStart,
  onRecordStop,
  disabled = false,
}: RecordButtonProps) {
  const handleMouseDown = () => {
    if (!disabled && !isRecording) {
      onRecordStart();
    }
  };

  const handleMouseUp = () => {
    if (isRecording) {
      onRecordStop();
    }
  };

  return (
    <button
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleMouseDown}
      onTouchEnd={handleMouseUp}
      disabled={disabled}
      className={cn(
        "relative w-32 h-32 rounded-full transition-all duration-300 focus:outline-none focus-visible:ring-4 focus-visible:ring-ring",
        "flex items-center justify-center",
        "select-none cursor-pointer",
        isRecording
          ? "bg-recording shadow-recording animate-pulse-recording"
          : "bg-primary hover:bg-primary/90 shadow-lg hover:shadow-xl hover:scale-105",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      aria-label={isRecording ? "Release to stop recording" : "Hold to record"}
    >
      {/* Outer ring for recording state */}
      {isRecording && (
        <div className="absolute inset-0 rounded-full border-4 border-recording/30 animate-ping" />
      )}
      
      {/* Icon */}
      <Mic
        className={cn(
          "w-12 h-12 transition-colors",
          isRecording ? "text-recording-foreground" : "text-primary-foreground"
        )}
      />
      
      {/* Label */}
      <span
        className={cn(
          "absolute -bottom-10 left-1/2 -translate-x-1/2 text-sm font-medium whitespace-nowrap",
          isRecording ? "text-recording" : "text-muted-foreground"
        )}
      >
        {isRecording ? "Release to stop" : "Hold to record"}
      </span>
    </button>
  );
}
