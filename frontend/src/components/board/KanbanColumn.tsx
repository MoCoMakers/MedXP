import { SBARCard, Patient } from "@/types/handoff";
import { KanbanCard } from "./KanbanCard";
import { cn } from "@/lib/utils";

interface KanbanColumnProps {
  title: string;
  status: SBARCard["status"];
  handoffs: SBARCard[];
  patients: Patient[];
  onCardClick?: (handoffId: string) => void;
  color: string;
}

export function KanbanColumn({
  title,
  status,
  handoffs,
  patients,
  onCardClick,
  color,
}: KanbanColumnProps) {
  const columnHandoffs = handoffs.filter((h) => h.status === status);

  return (
    <div className="flex flex-col min-w-[280px] max-w-[320px]">
      {/* Column Header */}
      <div className="flex items-center gap-3 mb-4 px-1">
        <div className={cn("w-3 h-3 rounded-full", color)} />
        <h3 className="font-semibold text-sm">{title}</h3>
        <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
          {columnHandoffs.length}
        </span>
      </div>

      {/* Cards */}
      <div className="space-y-3 flex-1">
        {columnHandoffs.map((handoff) => (
          <KanbanCard
            key={handoff.id}
            handoff={handoff}
            patient={patients.find((p) => p.id === handoff.patientId)}
            onClick={() => onCardClick?.(handoff.id)}
          />
        ))}
        {columnHandoffs.length === 0 && (
          <div className="text-center py-8 text-muted-foreground text-sm border-2 border-dashed border-border rounded-lg">
            No handoffs
          </div>
        )}
      </div>
    </div>
  );
}
