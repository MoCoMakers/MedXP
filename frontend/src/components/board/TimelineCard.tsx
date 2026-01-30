import { SBARCard, Patient } from "@/types/handoff";
import { cn } from "@/lib/utils";
import { AlertTriangle, CheckSquare, Clock, ChevronRight } from "lucide-react";

interface TimelineCardProps {
  handoff: SBARCard;
  patient: Patient;
  onClick?: () => void;
}

export function TimelineCard({ handoff, patient, onClick }: TimelineCardProps) {
  const pendingTasks = handoff.tasks.filter((t) => !t.completed).length;
  const highRisks = handoff.risks.filter((r) => r.severity === "high");

  const statusColors = {
    new: "border-info bg-info/5",
    acknowledged: "border-warning bg-warning/5",
    in_progress: "border-primary bg-primary/5",
    completed: "border-success bg-success/5",
  };

  const statusDotColors = {
    new: "bg-info",
    acknowledged: "bg-warning",
    in_progress: "bg-primary",
    completed: "bg-success",
  };

  return (
    <div
      className={cn(
        "relative pl-8 pb-8 last:pb-0 cursor-pointer group"
      )}
      onClick={onClick}
    >
      {/* Timeline line */}
      <div className="absolute left-[11px] top-3 bottom-0 w-0.5 bg-border group-last:hidden" />
      
      {/* Timeline dot */}
      <div
        className={cn(
          "absolute left-1.5 top-1.5 w-4 h-4 rounded-full border-2 border-background",
          statusDotColors[handoff.status]
        )}
      />

      {/* Card content */}
      <div
        className={cn(
          "border-l-4 rounded-lg p-4 transition-all hover:shadow-md",
          statusColors[handoff.status]
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm">{patient.name}</span>
            <span className="text-xs text-muted-foreground">
              Room {patient.room}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="w-3.5 h-3.5" />
            {new Date(handoff.createdAt).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        {/* Situation preview */}
        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
          {handoff.situation}
        </p>

        {/* Footer with risks and tasks */}
        <div className="flex items-center gap-4 flex-wrap">
          {highRisks.length > 0 && (
            <div className="flex items-center gap-1.5 text-risk">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span className="text-xs font-medium">
                {highRisks.length} high risk{highRisks.length > 1 ? "s" : ""}
              </span>
            </div>
          )}
          {pendingTasks > 0 && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <CheckSquare className="w-3.5 h-3.5" />
              <span className="text-xs">
                {pendingTasks} task{pendingTasks > 1 ? "s" : ""} pending
              </span>
            </div>
          )}
          <span
            className={cn(
              "text-xs px-2 py-0.5 rounded-full capitalize",
              handoff.status === "new" && "bg-info/20 text-info",
              handoff.status === "acknowledged" && "bg-warning/20 text-warning",
              handoff.status === "in_progress" && "bg-primary/20 text-primary",
              handoff.status === "completed" && "bg-success/20 text-success"
            )}
          >
            {handoff.status.replace("_", " ")}
          </span>
        </div>
      </div>
    </div>
  );
}
