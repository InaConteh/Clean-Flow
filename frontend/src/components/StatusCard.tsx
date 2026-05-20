import type { GeoJSONFeature } from "../types";
import StatusBadge from "./StatusBadge";

interface Props {
  feature: GeoJSONFeature;
  onReport: (id: string) => void;
}

export default function StatusCard({ feature, onReport }: Props) {
  const { id, name, status, last_tested } = feature.properties;
  const tested = last_tested
    ? new Date(last_tested).toLocaleDateString()
    : "Unknown";

  return (
    <article
      className="group rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
      aria-labelledby={`source-${id}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 id={`source-${id}`} className="text-lg font-bold text-primary">
            {name}
          </h3>
          <p className="text-sm text-neutral">ID: {id}</p>
        </div>
        <StatusBadge status={status} />
      </div>
      <p className="mt-2 text-sm text-body">Last tested: {tested}</p>
      <button
        type="button"
        onClick={() => onReport(id)}
        className="mt-3 w-full rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white opacity-0 transition group-hover:opacity-100 focus:opacity-100"
        aria-label={`Report issue at ${name}`}
      >
        Report Issue
      </button>
    </article>
  );
}
