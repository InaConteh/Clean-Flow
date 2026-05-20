import { useCallback, useEffect, useState } from "react";
import { fetchSources, fetchTips, submitReport } from "./api";
import StatusCard from "./components/StatusCard";
import WaterMap from "./components/WaterMap";
import ReportForm from "./components/ReportForm";
import TipsPanel from "./components/TipsPanel";
import type { GeoJSONFeature, Tip } from "./types";

export default function App() {
  const [features, setFeatures] = useState<GeoJSONFeature[]>([]);
  const [tips, setTips] = useState<Tip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportSourceId, setReportSourceId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [geo, tipList] = await Promise.all([fetchSources(), fetchTips()]);
      setFeatures(geo.features);
      setTips(tipList);
    } catch {
      setError("Could not load data. Is the API running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleReportSubmit(cause: string) {
    if (!reportSourceId) return;
    const result = await submitReport(reportSourceId, cause);
    setReportSourceId(null);
    setToast(result.message);
    await load();
    setTimeout(() => setToast(null), 5000);
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-primary">CleanFlow SL</h1>
            <p className="text-sm text-neutral">Water security for Sierra Leone</p>
          </div>
          <nav aria-label="Main">
            <a href="#map" className="text-sm font-semibold text-primary">
              Map
            </a>
            <span className="mx-2 text-neutral">|</span>
            <a href="#sources" className="text-sm font-semibold text-primary">
              Sources
            </a>
            <span className="mx-2 text-neutral">|</span>
            <a href="#tips" className="text-sm font-semibold text-primary">
              Tips
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-10 px-4 py-8">
        {toast && (
          <div
            role="status"
            className="rounded-lg border border-safe/40 bg-safe/10 px-4 py-3 text-safe"
          >
            {toast}
          </div>
        )}

        {error && (
          <div role="alert" className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-danger">
            {error}
          </div>
        )}

        <section id="map">
          <h2 className="mb-4 text-xl font-bold text-primary">Water Sources Map</h2>
          {loading ? (
            <p className="text-neutral">Loading map…</p>
          ) : (
            <WaterMap features={features} />
          )}
        </section>

        <section id="sources">
          <h2 className="mb-4 text-xl font-bold text-primary">Status Overview</h2>
          {loading ? (
            <p className="text-neutral">Loading sources…</p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((f) => (
                <StatusCard
                  key={f.properties.id}
                  feature={f}
                  onReport={setReportSourceId}
                />
              ))}
            </div>
          )}
        </section>

        <section id="tips">
          <TipsPanel tips={tips} />
        </section>
      </main>

      <footer className="border-t border-gray-200 py-6 text-center text-sm text-neutral">
        SMS: STATUS &lt;ID&gt; · CAUSE &lt;ID&gt; &lt;CODE&gt; · TIPS
      </footer>

      {reportSourceId && (
        <ReportForm
          sourceId={reportSourceId}
          onClose={() => setReportSourceId(null)}
          onSubmit={handleReportSubmit}
        />
      )}
    </div>
  );
}
