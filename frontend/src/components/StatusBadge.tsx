import type { WaterStatus } from "../types";

const styles: Record<WaterStatus, string> = {
  green: "bg-safe/15 text-safe border-safe/30",
  yellow: "bg-caution/20 text-yellow-800 border-caution/40",
  red: "bg-danger/15 text-danger border-danger/30",
};

const labels: Record<WaterStatus, string> = {
  green: "Safe",
  yellow: "Weather Risk",
  red: "Unsafe",
};

const icons: Record<WaterStatus, string> = {
  green: "🟢",
  yellow: "🌤️",
  red: "🔴",
};

export default function StatusBadge({ status }: { status: WaterStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${styles[status]}`}
      aria-label={`Status: ${labels[status]}`}
    >
      <span aria-hidden="true">{icons[status]}</span>
      {labels[status]}
    </span>
  );
}
