export default function Loading() {
  return (
    <div className="mx-auto max-w-6xl animate-pulse space-y-6">
      <div className="h-10 w-72 rounded-xl bg-line" />
      <div className="h-40 rounded-3xl bg-line" />
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-32 rounded-2xl bg-line" />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="h-96 rounded-3xl bg-line lg:col-span-2" />
        <div className="h-96 rounded-3xl bg-line" />
      </div>
    </div>
  );
}