import { useState, useEffect } from "react";
import Prism from "prismjs";
import "prismjs/components/prism-hcl";
import "prismjs/themes/prism-tomorrow.css";
import type { GenerateResponse } from "../lib/api";
import DiagramView from "./DiagramView";
import FinOpsPricingCalculator from "./FinOpsPricingCalculator";
import { downloadTerraformAsZip } from "../lib/downloadUtils";

interface ResultTabsProps {
  result: GenerateResponse | null;
  loading?: boolean;
}

export default function ResultTabs({ result, loading }: ResultTabsProps) {
  const [active, setActive] = useState("iac");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    Prism.highlightAll();
  }, [result, active]);

  const handleDownloadTerraform = async () => {
    if (!result?.iac) return;
    
    setDownloading(true);
    try {
      await downloadTerraformAsZip(result.iac, "terraform-infrastructure");
    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to download Terraform files");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-blue-600 border-gray-700 mx-auto mb-3"></div>
          <p className="text-gray-400">Generating infrastructure...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center h-[600px]">
        <p className="text-gray-400">Run a prompt to see results.</p>
      </div>
    );
  }

  const tabs = [
    { id: "iac", label: "IaC", available: !!result.iac },
    { id: "diagram", label: "Diagram", available: !!result.iac },
    { id: "plan", label: "Plan", available: !!result.plan },
    { id: "security", label: "Security", available: !!result.security },
    { id: "finops", label: "FinOps", available: !!result.finops },
  ];

  // Ensure active tab is available
  const hasActive = tabs.some(t => t.id === active && t.available);
  if (!hasActive) {
    const firstAvailable = tabs.find(t => t.available);
    if (firstAvailable) setActive(firstAvailable.id);
  }

  const renderContent = () => {
    if (active === "iac" && result.iac) {
      return (
        <div>
          {/* Download Button */}
          <div className="mb-4 flex justify-end">
            <button
              onClick={handleDownloadTerraform}
              disabled={downloading}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium text-sm transition flex items-center gap-2"
            >
              {downloading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-white"></div>
                  Downloading...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download as ZIP
                </>
              )}
            </button>
          </div>

          {/* Terraform Files */}
          {Object.entries(result.iac).map(([file, code]) => (
            <div key={file} className="mb-6">
              <h3 className="font-semibold text-blue-400 mb-2 text-sm">{file}</h3>
              <pre className="language-hcl rounded-lg overflow-auto text-sm bg-black/30 p-3">
                <code className="language-hcl">{code as string}</code>
              </pre>
            </div>
          ))}
        </div>
      );
    }

    if (active === "diagram") {
      return <DiagramView result={result} />;
    }

    if (active === "finops") {
      return <FinOpsPricingCalculator result={result} />;
    }

    const data = result[active as keyof GenerateResponse];

    if (!data) {
      return <p className="text-gray-400">No data available.</p>;
    }

    if (typeof data === "object" && "error" in data) {
      return (
        <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
          {(data as any).error}
        </div>
      );
    }

    return (
      <pre className="bg-black/30 p-4 rounded-lg overflow-auto text-sm max-h-[500px] text-gray-100">
        {typeof data === "string" ? data : JSON.stringify(data, null, 2)}
      </pre>
    );
  };

  return (
    <>
      {/* Tabs */}
      <div className="flex space-x-2 border-b border-gray-700 pb-2 mb-4 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.id}
            disabled={!t.available}
            className={`px-3 py-2 font-medium whitespace-nowrap transition ${
              active === t.id
                ? "text-blue-400 border-b-2 border-blue-400"
                : t.available
                ? "text-gray-400 hover:text-gray-200"
                : "text-gray-600 cursor-not-allowed"
            }`}
            onClick={() => t.available && setActive(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="max-h-[600px] overflow-auto">
        {renderContent()}
      </div>
    </>
  );
}
