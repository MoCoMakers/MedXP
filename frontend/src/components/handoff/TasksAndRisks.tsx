import { Task, Risk, MissingInfo } from "@/types/handoff";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { CheckSquare, AlertTriangle, HelpCircle, Clock } from "lucide-react";

interface TasksAndRisksProps {
  tasks: Task[];
  risks: Risk[];
  missingInfo: MissingInfo[];
  onTaskToggle?: (taskId: string) => void;
  onMissingInfoToggle?: (id: string) => void;
}

export function TasksAndRisks({
  tasks,
  risks,
  missingInfo,
  onTaskToggle,
  onMissingInfoToggle,
}: TasksAndRisksProps) {
  return (
    <div className="space-y-4">
      {/* Tasks */}
      <Card className="bg-card border-border shadow-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-success" />
            Tasks
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {tasks.map((task) => (
            <div
              key={task.id}
              className={cn(
                "flex items-start gap-3 p-2 rounded-lg transition-colors",
                task.completed && "bg-muted/50"
              )}
            >
              <Checkbox
                checked={task.completed}
                onCheckedChange={() => onTaskToggle?.(task.id)}
                className="mt-0.5"
              />
              <div className="flex-1 min-w-0">
                <p
                  className={cn(
                    "text-sm",
                    task.completed && "line-through text-muted-foreground"
                  )}
                >
                  {task.text}
                </p>
                {task.dueTime && (
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                    <Clock className="w-3 h-3" />
                    {task.dueTime}
                  </p>
                )}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Risks */}
      <Card className="bg-card border-border shadow-card border-risk/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-risk" />
            Risks
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {risks.map((risk) => (
            <div
              key={risk.id}
              className={cn(
                "p-3 rounded-lg border",
                risk.severity === "high"
                  ? "bg-risk/5 border-risk/20"
                  : risk.severity === "medium"
                  ? "bg-warning/5 border-warning/20"
                  : "bg-muted/50 border-border"
              )}
            >
              <div className="flex items-start gap-2">
                <span
                  className={cn(
                    "px-2 py-0.5 rounded text-xs font-semibold uppercase",
                    risk.severity === "high"
                      ? "bg-risk text-risk-foreground"
                      : risk.severity === "medium"
                      ? "bg-warning text-warning-foreground"
                      : "bg-muted text-muted-foreground"
                  )}
                >
                  {risk.severity}
                </span>
                <div className="flex-1">
                  <p className="font-medium text-sm">{risk.title}</p>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    {risk.rationale}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Missing Info */}
      <Card className="bg-card border-border shadow-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-info" />
            Missing Info Checklist
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {missingInfo.map((item) => (
            <div key={item.id} className="flex items-center gap-3">
              <Checkbox
                checked={item.checked}
                onCheckedChange={() => onMissingInfoToggle?.(item.id)}
              />
              <span
                className={cn(
                  "text-sm",
                  item.checked ? "text-muted-foreground" : "text-foreground"
                )}
              >
                {item.item}
              </span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
