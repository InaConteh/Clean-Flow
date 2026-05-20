import type { Tip } from "../types";

const iconMap: Record<string, string> = {
  "water-drop": "💧",
  warning: "⚠️",
  wrench: "🔧",
  sun: "☀️",
  book: "📖",
};

export default function TipsPanel({ tips }: { tips: Tip[] }) {
  return (
    <section aria-labelledby="tips-heading">
      <h2 id="tips-heading" className="text-xl font-bold text-primary">
        Educational Tips
      </h2>
      <ul className="mt-4 space-y-3">
        {tips.map((tip) => (
          <li
            key={tip.id}
            className="flex gap-3 rounded-lg border border-gray-200 bg-white p-4"
          >
            <span className="text-2xl" aria-hidden>
              {iconMap[tip.icon] || "📖"}
            </span>
            <div>
              <h3 className="font-semibold text-body">{tip.title}</h3>
              <p className="text-sm text-neutral">{tip.body}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
