import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Loader2 } from "lucide-react";

interface TranscriptPreviewProps {
  transcript: string;
  isProcessing: boolean;
}

export function TranscriptPreview({
  transcript,
  isProcessing,
}: TranscriptPreviewProps) {
  if (isProcessing) {
    return (
      <Card className="bg-card border-border">
        <CardContent className="py-12 flex flex-col items-center justify-center gap-4">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <div className="text-center">
            <p className="font-medium">Processing audio...</p>
            <p className="text-sm text-muted-foreground">
              Generating transcript and SBAR card
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!transcript) {
    return null;
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          Transcript Preview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="max-h-48 overflow-y-auto rounded-lg bg-muted/50 p-4">
          <p className="text-sm leading-relaxed text-foreground/90">
            {transcript}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
