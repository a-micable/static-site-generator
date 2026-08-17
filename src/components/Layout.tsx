import type { AppView } from "../types";

interface LayoutProps {
  activeView: AppView;
  onNavigate: (view: AppView) => void;
  children: React.ReactNode;
}

const NAV: { view: AppView; label: string }[] = [
  { view: "editor", label: "Markdown Editor" },
  { view: "config", label: "Site Config" },
  { view: "collections", label: "Collections" },
  { view: "build", label: "Build" },
  { view: "search", label: "Search Index" },
];

export function Layout({ activeView, onNavigate, children }: LayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1 className="brand">SSG Dashboard</h1>
        <nav className="nav">
          {NAV.map((item) => (
            <button
              key={item.view}
              type="button"
              className={activeView === item.view ? "nav-link active" : "nav-link"}
              onClick={() => onNavigate(item.view)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
