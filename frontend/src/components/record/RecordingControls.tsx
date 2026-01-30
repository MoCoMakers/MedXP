import { IncomingRole, ShiftContext } from "@/types/handoff";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { UserCog, ArrowRight } from "lucide-react";

interface RecordingControlsProps {
  incomingRole: IncomingRole;
  shiftContext: ShiftContext;
  onRoleChange: (role: IncomingRole) => void;
  onContextChange: (context: ShiftContext) => void;
}

const roles: IncomingRole[] = ["RN", "Intern", "Resident", "Attending"];
const contexts: ShiftContext[] = [
  "ED → Floor",
  "ICU → Floor",
  "OR → PACU",
  "Floor → Floor",
];

export function RecordingControls({
  incomingRole,
  shiftContext,
  onRoleChange,
  onContextChange,
}: RecordingControlsProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <UserCog className="w-4 h-4" />
          Incoming Role
        </label>
        <Select value={incomingRole} onValueChange={onRoleChange}>
          <SelectTrigger className="w-full bg-card border-border">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {roles.map((role) => (
              <SelectItem key={role} value={role}>
                {role}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <ArrowRight className="w-4 h-4" />
          Shift Context
        </label>
        <Select value={shiftContext} onValueChange={onContextChange}>
          <SelectTrigger className="w-full bg-card border-border">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {contexts.map((context) => (
              <SelectItem key={context} value={context}>
                {context}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
