import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface SBARCardProps {
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
}

const sections = [
  { key: "situation", label: "S", title: "Situation", color: "bg-info" },
  { key: "background", label: "B", title: "Background", color: "bg-primary" },
  { key: "assessment", label: "A", title: "Assessment", color: "bg-warning" },
  { key: "recommendation", label: "R", title: "Recommendation", color: "bg-success" },
] as const;

export function SBARCardDisplay({
  situation,
  background,
  assessment,
  recommendation,
}: SBARCardProps) {
  const content: Record<string, string> = {
    situation,
    background,
    assessment,
    recommendation,
  };

  return (
    <Card className="bg-card border-border shadow-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <span className="text-primary">SBAR</span>
          <span className="text-muted-foreground font-normal text-sm">Handoff Card</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sections.map((section, index) => (
          <div key={section.key}>
            <div className="flex gap-3">
              <div
                className={`w-8 h-8 rounded-lg ${section.color} flex items-center justify-center flex-shrink-0`}
              >
                <span className="text-sm font-bold text-white">
                  {section.label}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-foreground mb-1">
                  {section.title}
                </h4>
                <p className="text-sm text-foreground/80 leading-relaxed">
                  {content[section.key]}
                </p>
              </div>
            </div>
            {index < sections.length - 1 && (
              <Separator className="mt-4 bg-border/50" />
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
