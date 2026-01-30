import { Patient } from "@/types/handoff";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { User } from "lucide-react";

interface PatientSelectorProps {
  patients: Patient[];
  selectedPatientId: string | null;
  onSelectPatient: (patientId: string) => void;
}

export function PatientSelector({
  patients,
  selectedPatientId,
  onSelectPatient,
}: PatientSelectorProps) {
  const selectedPatient = patients.find((p) => p.id === selectedPatientId);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-muted-foreground">
        Patient
      </label>
      <Select value={selectedPatientId || ""} onValueChange={onSelectPatient}>
        <SelectTrigger className="w-full bg-card border-border">
          <SelectValue placeholder="Select patient...">
            {selectedPatient && (
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-primary" />
                <span className="font-medium">{selectedPatient.name}</span>
                <span className="text-muted-foreground">
                  · Room {selectedPatient.room}
                </span>
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="bg-card border-border">
          {patients.map((patient) => (
            <SelectItem key={patient.id} value={patient.id}>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <div className="font-medium">{patient.name}</div>
                  <div className="text-xs text-muted-foreground">
                    Room {patient.room} · {patient.mrn} · {patient.age}
                    {patient.gender}
                  </div>
                </div>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
