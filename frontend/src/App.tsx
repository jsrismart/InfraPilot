import { useState } from "react";
import { generateFull, GenerateResponse } from "./lib/api";
import ResultTabs from "./components/ResultView";
import PricingCalculator from "./components/PricingCalculator";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fastMode, setFastMode] = useState(false);

  async function runPipeline() {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const out = await generateFull(prompt, fastMode);
      setResult(out);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">

      {/* Navbar */}
      <nav className="border-b border-gray-800 bg-gray-900 text-white p-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight">InfraPilot</h1>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="fastMode"
              checked={fastMode}
              onChange={(e) => setFastMode(e.target.checked)}
              disabled={loading}
              className="w-4 h-4 cursor-pointer"
            />
            <label htmlFor="fastMode" className="text-sm text-gray-300 cursor-pointer">
              Fast Mode (IaC only)
            </label>
          </div>
        </div>
      </nav>

      {/* Main Layout */}
      <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 gap-6">

        {/* Top Section: IaC Generation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Card */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-md">
            <h2 className="text-xl font-semibold mb-4">Describe Your Infrastructure</h2>

            <textarea
              className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm h-56 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder='Example: "AWS VPC with 2 subnets, EC2 instance, SG rules"'
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={loading}
            />

            <button
              onClick={runPipeline}
              disabled={loading || !prompt.trim()}
              className="mt-4 w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 transition font-semibold disabled:bg-gray-600 disabled:cursor-not-allowed"
            >
              {loading ? (fastMode ? "Generating IaC..." : "Running Full Pipeline...") : "Generate Infrastructure"}
            </button>

            {error && (
              <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
                {error}
              </div>
            )}

            <p className="mt-4 text-xs text-gray-400">
              {fastMode 
                ? "⚡ Fast Mode: Only generating IaC (faster)"
                : "Full Mode: Generating IaC + Plan + Security + Cost analysis"}
            </p>
          </div>

          {/* Right Card */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-md">
            <ResultTabs result={result} loading={loading} />
          </div>
        </div>

        {/* Bottom Section: Pricing Calculator */}
        {result && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-md">
            <h2 className="text-xl font-semibold mb-4">☁️ Multi-Cloud Cost Comparison</h2>
            <PricingCalculator result={result} />
          </div>
        )}
      </div>
    </div>
  );
}
