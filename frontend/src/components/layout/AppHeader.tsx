import { NavLink } from "@/components/NavLink";
import { Mic, LayoutGrid } from "lucide-react";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b border-border">
      <div className="container flex items-center justify-between h-14 px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">M</span>
          </div>
          <span className="font-semibold text-lg">MedXP</span>
        </div>

        <nav className="flex items-center gap-1">
          <NavLink
            to="/"
            className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            activeClassName="bg-muted text-foreground"
          >
            <Mic className="w-4 h-4" />
            Record
          </NavLink>
          <NavLink
            to="/board"
            className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            activeClassName="bg-muted text-foreground"
          >
            <LayoutGrid className="w-4 h-4" />
            Shift Board
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
