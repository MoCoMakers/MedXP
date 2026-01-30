import { SBARCard, Patient } from "@/types/handoff";
import { TimelineCard } from "./TimelineCard";
import { User } from "lucide-react";

interface TimelineViewProps {
  handoffs: SBARCard[];
  patients: Patient[];
  onCardClick?: (handoffId: string) => void;
}

export function TimelineView({ handoffs, patients, onCardClick }: TimelineViewProps) {
  // Group handoffs by patient
  const handoffsByPatient = patients.map((patient) => ({
    patient,
    handoffs: handoffs
      .filter((h) => h.patientId === patient.id)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()),
  })).filter((group) => group.handoffs.length > 0);

  if (handoffsByPatient.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No handoffs to display</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {handoffsByPatient.map(({ patient, handoffs: patientHandoffs }) => (
        <div key={patient.id} className="bg-card border border-border rounded-xl p-6">
          {/* Patient header */}
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-border">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold">{patient.name}</h3>
              <p className="text-sm text-muted-foreground">
                Room {patient.room} • MRN: {patient.mrn} • {patient.age}{patient.gender}
              </p>
            </div>
            <div className="ml-auto">
              <span className="text-xs bg-muted px-2.5 py-1 rounded-full">
                {patientHandoffs.length} handoff{patientHandoffs.length > 1 ? "s" : ""}
              </span>
            </div>
          </div>

          {/* Timeline */}
          <div className="pl-2">
            {patientHandoffs.map((handoff) => (
              <TimelineCard
                key={handoff.id}
                handoff={handoff}
                patient={patient}
                onClick={() => onCardClick?.(handoff.id)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
