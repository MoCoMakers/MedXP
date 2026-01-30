import * as React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { KanbanColumn } from "@/components/board/KanbanColumn";
import { TimelineView } from "@/components/board/TimelineView";
import { mockSBARCards, mockPatients } from "@/data/mockData";
import { SBARCard } from "@/types/handoff";
import { Plus, RefreshCw, LayoutGrid, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

const columns: {
  title: string;
  status: SBARCard["status"];
  color: string;
}[] = [
  { title: "New Handoffs", status: "new", color: "bg-info" },
  { title: "Acknowledged", status: "acknowledged", color: "bg-warning" },
  { title: "In Progress", status: "in_progress", color: "bg-primary" },
  { title: "Completed", status: "completed", color: "bg-success" },
];

type ViewMode = "kanban" | "timeline";

export default function ShiftBoard() {
  const navigate = useNavigate();
  const [handoffs, setHandoffs] = React.useState<SBARCard[]>(mockSBARCards);
  const [viewMode, setViewMode] = React.useState<ViewMode>("kanban");

  const handleCardClick = (handoffId: string) => {
    navigate(`/handoff/${handoffId}`);
  };

  const handleRefresh = () => {
    // Simulate refresh
    setHandoffs([...mockSBARCards]);
  };

  return (
    <div className="bg-background">
      {/* Header */}
      <header className="bg-background border-b border-border">
        <div className="container py-4 px-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold">Shift Board</h1>
              <p className="text-sm text-muted-foreground">
                Incoming handoffs for your shift
              </p>
            </div>
            <div className="flex items-center gap-2">
              {/* View Toggle */}
              <div className="flex items-center bg-muted rounded-lg p-1">
                <button
                  onClick={() => setViewMode("kanban")}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                    viewMode === "kanban"
                      ? "bg-background text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <LayoutGrid className="w-4 h-4" />
                  Kanban
                </button>
                <button
                  onClick={() => setViewMode("timeline")}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                    viewMode === "timeline"
                      ? "bg-background text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <Clock className="w-4 h-4" />
                  Timeline
                </button>
              </div>
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button size="sm" onClick={() => navigate("/")}>
                <Plus className="w-4 h-4 mr-2" />
                New Handoff
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="container py-6 px-4">
        {viewMode === "kanban" ? (
          <div className="flex gap-6 overflow-x-auto pb-6">
            {columns.map((column) => (
              <KanbanColumn
                key={column.status}
                title={column.title}
                status={column.status}
                handoffs={handoffs}
                patients={mockPatients}
                onCardClick={handleCardClick}
                color={column.color}
              />
            ))}
          </div>
        ) : (
          <TimelineView
            handoffs={handoffs}
            patients={mockPatients}
            onCardClick={handleCardClick}
          />
        )}
      </main>
    </div>
  );
}
