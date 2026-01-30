import { TranscriptEntity } from "@/types/handoff";
import { cn } from "@/lib/utils";

interface HighlightedTranscriptProps {
  transcript: string;
  entities: TranscriptEntity[];
}

const entityColors: Record<TranscriptEntity["type"], string> = {
  medication: "bg-entity-med/20 text-entity-med border-entity-med/30",
  vital: "bg-entity-vital/20 text-entity-vital border-entity-vital/30",
  lab: "bg-entity-lab/20 text-entity-lab border-entity-lab/30",
  time: "bg-entity-time/20 text-entity-time border-entity-time/30",
};

const entityLabels: Record<TranscriptEntity["type"], string> = {
  medication: "Med",
  vital: "Vital",
  lab: "Lab",
  time: "Time",
};

export function HighlightedTranscript({
  transcript,
  entities,
}: HighlightedTranscriptProps) {
  // Sort entities by start position
  const sortedEntities = [...entities].sort((a, b) => a.start - b.start);

  const renderTranscript = () => {
    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedEntities.forEach((entity, i) => {
      // Add text before this entity
      if (entity.start > lastIndex) {
        elements.push(
          <span key={`text-${i}`}>
            {transcript.slice(lastIndex, entity.start)}
          </span>
        );
      }

      // Add highlighted entity
      elements.push(
        <span
          key={`entity-${i}`}
          className={cn(
            "inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-sm font-medium",
            entityColors[entity.type]
          )}
          title={entityLabels[entity.type]}
        >
          {entity.text}
        </span>
      );

      lastIndex = entity.end;
    });

    // Add remaining text
    if (lastIndex < transcript.length) {
      elements.push(
        <span key="text-end">{transcript.slice(lastIndex)}</span>
      );
    }

    return elements;
  };

  return (
    <div className="text-sm leading-relaxed text-foreground/90 space-y-1">
      {renderTranscript()}
    </div>
  );
}

// Legend component
export function EntityLegend() {
  return (
    <div className="flex flex-wrap gap-3 text-xs">
      {Object.entries(entityLabels).map(([type, label]) => (
        <div key={type} className="flex items-center gap-1.5">
          <span
            className={cn(
              "w-3 h-3 rounded border",
              entityColors[type as TranscriptEntity["type"]]
            )}
          />
          <span className="text-muted-foreground">{label}</span>
        </div>
      ))}
    </div>
  );
}
