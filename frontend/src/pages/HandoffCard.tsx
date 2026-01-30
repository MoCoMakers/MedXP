import * as React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { HighlightedTranscript, EntityLegend } from "@/components/handoff/HighlightedTranscript";
import { SBARCardDisplay } from "@/components/handoff/SBARCardDisplay";
import { TasksAndRisks } from "@/components/handoff/TasksAndRisks";
import { mockSBARCards, mockPatients } from "@/data/mockData";
import { Task, MissingInfo } from "@/types/handoff";
import { FileText, Download, Share2, Lock, ArrowLeft, ChevronRight } from "lucide-react";
import { toast } from "@/hooks/use-toast";

export default function HandoffCard() {
  const navigate = useNavigate();
  const [card, setCard] = React.useState(mockSBARCards[0]);
  const patient = mockPatients.find((p) => p.id === card.patientId);

  const handleTaskToggle = (taskId: string) => {
    setCard((prev) => ({
      ...prev,
      tasks: prev.tasks.map((task) =>
        task.id === taskId ? { ...task, completed: !task.completed } : task
      ),
    }));
  };

  const handleMissingInfoToggle = (id: string) => {
    setCard((prev) => ({
      ...prev,
      missingInfo: prev.missingInfo.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item
      ),
    }));
  };

  const handleExport = () => {
    toast({
      title: "Exported",
      description: "Handoff card exported as PDF",
    });
  };

  const handleShare = () => {
    toast({
      title: "Link Generated",
      description: "Share link copied to clipboard",
    });
  };

  const handleLock = () => {
    setCard((prev) => ({
      ...prev,
      status: "completed",
      lockedAt: new Date(),
    }));
    toast({
      title: "Handoff Locked",
      description: "This handoff is now an immutable record",
    });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur border-b border-border">
        <div className="container py-4 px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate("/")}
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-lg font-semibold">{patient?.name}</h1>
                <p className="text-sm text-muted-foreground">
                  Room {patient?.room} · {patient?.mrn}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={handleExport}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" onClick={handleShare}>
                <Share2 className="w-4 h-4 mr-2" />
                Send
              </Button>
              <Button
                size="sm"
                onClick={handleLock}
                disabled={card.lockedAt !== undefined}
              >
                <Lock className="w-4 h-4 mr-2" />
                {card.lockedAt ? "Locked" : "Approve & Lock"}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="container py-6 px-4">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left: Transcript */}
          <Card className="bg-card border-border shadow-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary" />
                Transcript
              </CardTitle>
              <EntityLegend />
            </CardHeader>
            <CardContent>
              <div className="max-h-[60vh] overflow-y-auto pr-2">
                <HighlightedTranscript
                  transcript={card.transcript}
                  entities={card.entities}
                />
              </div>
            </CardContent>
          </Card>

          {/* Center: SBAR Card */}
          <div className="lg:col-span-1">
            <SBARCardDisplay
              situation={card.situation}
              background={card.background}
              assessment={card.assessment}
              recommendation={card.recommendation}
            />
          </div>

          {/* Right: Tasks & Risks */}
          <TasksAndRisks
            tasks={card.tasks}
            risks={card.risks}
            missingInfo={card.missingInfo}
            onTaskToggle={handleTaskToggle}
            onMissingInfoToggle={handleMissingInfoToggle}
          />
        </div>

        {/* Continue to Board */}
        <div className="mt-8 flex justify-center">
          <Button
            variant="outline"
            size="lg"
            onClick={() => navigate("/board")}
            className="gap-2"
          >
            View Shift Board
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
