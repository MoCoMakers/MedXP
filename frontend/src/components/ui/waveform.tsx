import * as React from "react";
import { cn } from "@/lib/utils";

interface WaveformProps {
  isActive: boolean;
  className?: string;
}

export function Waveform({ isActive, className }: WaveformProps) {
  const bars = 24;

  return (
    <div
      className={cn(
        "flex items-center justify-center gap-1 h-16",
        className
      )}
      aria-hidden="true"
    >
      {Array.from({ length: bars }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "w-1 rounded-full transition-all duration-150",
            isActive
              ? "bg-recording"
              : "bg-muted-foreground/30"
          )}
          style={{
            height: isActive
              ? `${20 + Math.random() * 60}%`
              : "20%",
            animationDelay: `${i * 50}ms`,
            transition: isActive ? "height 150ms ease-out" : "height 300ms ease-out",
          }}
        />
      ))}
    </div>
  );
}

// Animated version with continuous updates
export function AnimatedWaveform({ isActive, className }: WaveformProps) {
  const bars = 24;
  const [heights, setHeights] = React.useState<number[]>(
    Array(bars).fill(20)
  );

  React.useEffect(() => {
    if (!isActive) {
      setHeights(Array(bars).fill(20));
      return;
    }

    const interval = setInterval(() => {
      setHeights(
        Array(bars)
          .fill(0)
          .map(() => 15 + Math.random() * 70)
      );
    }, 100);

    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div
      className={cn(
        "flex items-center justify-center gap-1 h-16",
        className
      )}
      aria-hidden="true"
    >
      {heights.map((height, i) => (
        <div
          key={i}
          className={cn(
            "w-1 rounded-full transition-all duration-100",
            isActive ? "bg-recording" : "bg-muted-foreground/30"
          )}
          style={{
            height: `${height}%`,
          }}
        />
      ))}
    </div>
  );
}
