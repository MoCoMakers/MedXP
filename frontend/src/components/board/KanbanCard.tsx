import { SBARCard } from "@/types/handoff";
import { Patient } from "@/types/handoff";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { User, AlertTriangle, CheckSquare, Clock } from "lucide-react";

interface KanbanCardProps {
  handoff: SBARCard;
  patient: Patient | undefined;
  onClick?: () => void;
}

export function KanbanCard({ handoff, patient, onClick }: KanbanCardProps) {
  const pendingTasks = handoff.tasks.filter((t) => !t.completed).length;
  const highRisks = handoff.risks.filter((r) => r.severity === "high");

  return (
    <Card
      className={cn(
        "bg-card border-border shadow-card hover:shadow-card-hover transition-all cursor-pointer",
        "hover:border-primary/30"
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="w-4 h-4 text-primary" />
            </div>
            <div>
              <p className="font-medium text-sm">{patient?.name || "Unknown"}</p>
              <p className="text-xs text-muted-foreground">
                Room {patient?.room}
              </p>
            </div>
          </div>
          <Badge
            variant="outline"
            className={cn(
              "text-xs",
              handoff.status === "new" && "border-info text-info",
              handoff.status === "acknowledged" && "border-warning text-warning",
              handoff.status === "in_progress" && "border-primary text-primary",
              handoff.status === "completed" && "border-success text-success"
            )}
          >
            {handoff.status.replace("_", " ")}
          </Badge>
        </div>

        {/* Risks */}
        {highRisks.length > 0 && (
          <div className="mb-3 space-y-1.5">
            {highRisks.slice(0, 2).map((risk) => (
              <div
                key={risk.id}
                className="flex items-center gap-2 px-2 py-1.5 rounded bg-risk/10 text-risk"
              >
                <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="text-xs font-medium truncate">{risk.title}</span>
              </div>
            ))}
          </div>
        )}

        {/* Tasks */}
        {pendingTasks > 0 && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <CheckSquare className="w-3.5 h-3.5" />
            <span>{pendingTasks} task{pendingTasks > 1 ? "s" : ""} pending</span>
          </div>
        )}

        {/* Time */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
          <Clock className="w-3.5 h-3.5" />
          <span>
            {new Date(handoff.createdAt).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
