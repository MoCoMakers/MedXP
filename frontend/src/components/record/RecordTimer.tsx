import * as React from "react";
import { cn } from "@/lib/utils";

interface RecordTimerProps {
  isRecording: boolean;
  className?: string;
}

export function RecordTimer({ isRecording, className }: RecordTimerProps) {
  const [seconds, setSeconds] = React.useState(0);

  React.useEffect(() => {
    if (!isRecording) {
      setSeconds(0);
      return;
    }

    const interval = setInterval(() => {
      setSeconds((s) => s + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isRecording]);

  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div
      className={cn(
        "text-2xl font-mono font-semibold tabular-nums",
        isRecording ? "text-recording" : "text-muted-foreground",
        className
      )}
    >
      {formatTime(seconds)}
    </div>
  );
}
