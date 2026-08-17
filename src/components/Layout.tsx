import type { AppView } from "../types";

interface LayoutProps {
  activeView: AppView;
  onNavigate: (view: AppView) => void;
  children: React.ReactNode;
}

const NAV: { view: AppView; label: string; description: string }[] = [
  { view: "editor", label: "Editor", description: "Live Markdown preview" },
  { view: "posts", label: "Posts", description: "Create and manage posts" },
  { view: "collections", label: "Tags", description: "Browse taxonomies" },
  { view: "settings", label: "Settings", description: "Edit ssg.yaml" },
  { view: "build", label: "Build", description: "Generate static site" },
  { view: "search", label: "Search", description: "Search all content" },
];

export function Layout({ activeView, onNavigate, children }: LayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">SSG</div>
          <div>
            <h1 className="brand">SSG Studio</h1>
            <p className="brand-sub">Static Site Generator</p>
          </div>
        </div>
        <nav className="nav">
          {NAV.map((item) => (
            <button
              key={item.view}
              type="button"
              className={activeView === item.view ? "nav-link active" : "nav-link"}
              onClick={() => onNavigate(item.view)}
            >
              <span className="nav-label">{item.label}</span>
              <span className="nav-desc">{item.description}</span>
            </button>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <h2>{NAV.find((item) => item.view === activeView)?.label}</h2>
        </header>
        {children}
      </main>
    </div>
  );
}
