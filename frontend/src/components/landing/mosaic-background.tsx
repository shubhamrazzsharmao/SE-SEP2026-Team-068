const COLS = 10;
const ROWS = 8;

const tiles = Array.from({ length: COLS * ROWS }, (_, n) => {
  const c = n % COLS;
  const r = Math.floor(n / COLS);
  const h = (c * 7 + r * 13 + c * r) % 11;
  if (h === 0) return "bg-brand";
  if (h === 3) return "bg-ink";
  if (h === 5) return "bg-accent/80";
  if (h <= 8) return "bg-ink/[0.04]";
  return "bg-transparent";
});

export function MosaicBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute right-6 top-10 hidden w-[480px] grid-cols-10 gap-2 lg:grid [mask-image:linear-gradient(to_bottom_left,#000_25%,transparent_80%)]"
    >
      {tiles.map((fill, i) => (
        <div key={i} className={`aspect-square rounded-md border border-ink/[0.07] ${fill}`} />
      ))}
    </div>
  );
}