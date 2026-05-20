interface Props {
  sourceId: string;
  onClose: () => void;
  onSubmit: (cause: string) => Promise<void>;
}

const CAUSES = [
  { value: "BROKEN_PUMP", label: "Broken pump" },
  { value: "DRY_WELL", label: "Dry well" },
  { value: "CONTAMINATION", label: "Contamination" },
  { value: "LOW_WATER", label: "Low water level" },
];

export default function ReportForm({ sourceId, onClose, onSubmit }: Props) {
  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const cause = form.get("cause") as string;
    await onSubmit(cause);
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-title"
    >
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl"
      >
        <h2 id="report-title" className="text-xl font-bold text-primary">
          Report Issue
        </h2>
        <p className="mt-1 text-sm text-neutral">Source: {sourceId}</p>

        <label className="mt-4 block text-sm font-semibold text-body" htmlFor="cause">
          Cause
        </label>
        <select
          id="cause"
          name="cause"
          required
          className="mt-1 w-full rounded-lg border border-gray-300 px-4 py-3 text-base focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
        >
          {CAUSES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-3 font-semibold text-body"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex-1 rounded-lg bg-primary px-4 py-3 font-semibold text-white"
          >
            Submit
          </button>
        </div>
      </form>
    </div>
  );
}
