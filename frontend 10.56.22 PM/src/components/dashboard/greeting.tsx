export function Greeting({ name }: { name: string }) {
  const h = new Date().getHours();
  const part = h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
  return (
    <h1 className="text-3xl font-bold tracking-tight">
      <span suppressHydrationWarning>{part}</span>, {name}
    </h1>
  );
}