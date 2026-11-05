import { LuBell, LuMenu, LuSearch } from "react-icons/lu";

export function TopBar({ onMenu, initial }: { onMenu: () => void; initial: string }) {
  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-line bg-paper/80 px-6 py-3 backdrop-blur-md lg:px-10">
      <button className="lg:hidden" onClick={onMenu} aria-label="Open menu">
        <LuMenu size={22} />
      </button>

      <label className="relative max-w-md flex-1">
        <LuSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-muted" size={16} />
        <input
          type="search"
          placeholder="Search campaigns, posts, clients…"
          className="w-full rounded-full border border-line bg-white py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-brand"
        />
      </label>

      <div className="ml-auto flex items-center gap-3">
        <button className="relative grid h-10 w-10 place-items-center rounded-full border border-line bg-white" aria-label="Notifications">
          <LuBell size={17} />
          <span className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-brand" />
        </button>
        <span className="grid h-10 w-10 place-items-center rounded-full bg-ink text-sm font-bold text-paper">{initial}</span>
      </div>
    </header>
  );
}