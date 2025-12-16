import { useState, useEffect } from "react";
import type { GenerateResponse } from "../lib/api";

interface PricingData {
  success: boolean;
  total_costs: {
    aws: number;
    azure: number;
    gcp: number;
  };
  breakdown: {
    aws: Array<{ name: string; type: string; cost: number; description: string }>;
    azure: Array<{ name: string; type: string; cost: number; description: string }>;
    gcp: Array<{ name: string; type: string; cost: number; description: string }>;
  };
  comparison: {
    cheapest_provider: string;
    monthly_costs: { aws: number; azure: number; gcp: number };
    annual_costs: { aws: number; azure: number; gcp: number };
    savings_potential: Record<string, any>;
  };
}

interface FinOpsPricingCalculatorProps {
  result: GenerateResponse | null;
}

export default function FinOpsPricingCalculator({ result }: FinOpsPricingCalculatorProps) {
  const [pricingData, setPricingData] = useState<PricingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<"aws" | "azure" | "gcp" | "all">("all");
  const [customTerraform, setCustomTerraform] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Auto-calculate pricing when result changes (FORCE FRESH CALCULATION EVERY TIME)
  useEffect(() => {
    if (result?.iac && Object.keys(result.iac).length > 0) {
      const code = Object.values(result.iac).join("\n\n");
      if (code && code.trim()) {
        // Force fresh calculation - don't cache, always recalculate
        calculatePricing(code);
      }
    }
  }, [result]);

  const calculatePricing = async (terraformCode?: string) => {
    const code = terraformCode || customTerraform || Object.values(result?.iac || {}).join("\n\n");

    if (!code || !code.trim()) {
      setError("Please provide Terraform code or generate IaC first");
      return;
    }

    // FORCE FRESH CALCULATION - Reset state first
    setPricingData(null);
    setLoading(true);
    setError(null);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE || "http://localhost:8001/api/v1";

      const response = await fetch(`${baseUrl}/pricing/calculate-pricing`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Cache-Control": "no-cache, no-store, must-revalidate",
          "Pragma": "no-cache",
          "Expires": "0"
        },
        body: JSON.stringify({
          terraform_code: code,
          include_breakdown: true,
          include_comparison: true,
        }),
        cache: "no-store"
      });

      if (!response.ok) {
        throw new Error("Failed to calculate pricing");
      }

      const data = await response.json();
      setPricingData(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to calculate pricing";
      setError(errorMsg);
      console.error("Pricing calculation error:", err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const getProviderColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "aws":
        return "from-orange-500 to-orange-600";
      case "azure":
        return "from-blue-500 to-blue-600";
      case "gcp":
        return "from-red-500 to-red-600";
      default:
        return "from-gray-500 to-gray-600";
    }
  };

  const getProviderBgColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "aws":
        return "bg-orange-50";
      case "azure":
        return "bg-blue-50";
      case "gcp":
        return "bg-red-50";
      default:
        return "bg-gray-50";
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "aws":
        return "☁️";
      case "azure":
        return "🔵";
      case "gcp":
        return "🔴";
      default:
        return "💾";
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            💻 Terraform Code Input
          </label>
          <textarea
            className="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-xs font-mono h-40 text-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-600"
            placeholder='Paste or modify Terraform code here...
Example:
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
}

resource "aws_db_instance" "postgres" {
  allocated_storage = 20
  instance_class    = "db.t2.small"
}'
            value={customTerraform}
            onChange={(e) => setCustomTerraform(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => {
              setCustomTerraform("");
              setPricingData(null);
            }}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg text-sm font-medium transition"
          >
            Clear
          </button>
          {result?.iac && (
            <button
              onClick={() => {
                const terraformCode = Object.values(result.iac).join("\n\n");
                setCustomTerraform(terraformCode);
              }}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition"
            >
              Load Generated IaC
            </button>
          )}
          <button
            onClick={() => calculatePricing()}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition disabled:bg-gray-600 disabled:cursor-not-allowed ml-auto"
          >
            {loading ? "Calculating..." : "💰 Calculate Pricing"}
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Provider Filter */}
      {pricingData && (
        <div className="flex gap-2 flex-wrap items-center">
          <span className="text-sm text-gray-400 font-medium">Filter:</span>
          {(["all", "aws", "azure", "gcp"] as const).map((provider) => (
            <button
              key={provider}
              onClick={() => setSelectedProvider(provider)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                selectedProvider === provider
                  ? "bg-purple-600 text-white"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
            >
              {provider === "all" ? "📊 All" : `${getProviderIcon(provider)} ${provider.toUpperCase()}`}
            </button>
          ))}
        </div>
      )}

      {/* Pricing Results */}
      {pricingData && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {["aws", "azure", "gcp"].map((provider) => (
              (selectedProvider === "all" || selectedProvider === provider) && (
                <div
                  key={provider}
                  className={`p-5 rounded-lg border border-gray-700 ${getProviderBgColor(provider)} bg-gray-800/50`}
                >
                  <div className={`bg-gradient-to-r ${getProviderColor(provider)} p-3 rounded mb-4`}>
                    <h3 className="text-white font-bold text-lg">
                      {getProviderIcon(provider)} {provider.toUpperCase()}
                    </h3>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Monthly Cost</p>
                      <p className="text-3xl font-bold text-gray-100 mt-1">
                        {formatCurrency(pricingData.total_costs[provider as keyof typeof pricingData.total_costs])}
                      </p>
                    </div>
                    <div className="pt-2 border-t border-gray-700">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Annual Cost</p>
                      <p className="text-lg font-semibold text-gray-300 mt-1">
                        {formatCurrency(
                          pricingData.total_costs[provider as keyof typeof pricingData.total_costs] * 12
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              )
            ))}
          </div>

          {/* Cheapest Provider Recommendation */}
          {pricingData.comparison && (
            <div className="bg-gradient-to-r from-green-900/40 to-emerald-900/40 border border-green-700/50 rounded-lg p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-green-400 font-bold mb-2 text-lg">
                    ✅ Recommended Provider: {pricingData.comparison.cheapest_provider.toUpperCase()}
                  </p>
                  <p className="text-sm text-gray-300">
                    Best cost-efficiency for your infrastructure
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-400">
                    {formatCurrency(pricingData.comparison.monthly_costs[pricingData.comparison.cheapest_provider as keyof typeof pricingData.comparison.monthly_costs])}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatCurrency(pricingData.comparison.annual_costs[pricingData.comparison.cheapest_provider as keyof typeof pricingData.comparison.annual_costs])}/year
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Savings Potential */}
          {pricingData.comparison.savings_potential &&
            Object.entries(pricingData.comparison.savings_potential).length > 0 && (
              <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-700/50 rounded-lg p-5">
                <h4 className="text-blue-300 font-bold mb-4 text-lg">💡 Potential Savings</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(pricingData.comparison.savings_potential).map(
                    ([provider, savings]: [string, any]) => (
                      <div key={provider} className="bg-gray-900/50 rounded p-3 border border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-gray-200 uppercase">{provider}</span>
                          <span className="text-yellow-400 font-bold text-lg">
                            {savings.percent_difference.toFixed(1)}%
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">
                          Save{" "}
                          <span className="text-yellow-400 font-bold">
                            {formatCurrency(savings.monthly_savings)}/month
                          </span>
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatCurrency(savings.annual_savings)}/year by switching
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

          {/* Detailed Cost Breakdown */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-gray-100">📊 Detailed Cost Breakdown</h3>
            {["aws", "azure", "gcp"].map((provider) => (
              (selectedProvider === "all" || selectedProvider === provider) &&
              pricingData.breakdown[provider as keyof typeof pricingData.breakdown].length > 0 && (
                <div key={provider} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <h4 className="font-bold text-gray-200 mb-3 uppercase text-sm flex items-center gap-2">
                    {getProviderIcon(provider)} {provider} Resources
                  </h4>
                  <div className="space-y-2">
                    {pricingData.breakdown[provider as keyof typeof pricingData.breakdown].map((res, idx) => (
                      <div
                        key={idx}
                        className="flex justify-between items-start py-2 px-3 bg-gray-900/50 rounded border border-gray-700/50 hover:border-gray-600 transition"
                      >
                        <div className="flex-1">
                          <p className="font-semibold text-gray-200 text-sm">{res.name}</p>
                          <p className="text-xs text-gray-400 mt-1">{res.description}</p>
                          <p className="text-xs text-gray-500 mt-1">Type: {res.type}</p>
                        </div>
                        <div className="text-right ml-4">
                          <p className="font-bold text-green-400 text-sm">{formatCurrency(res.cost)}</p>
                          <p className="text-xs text-gray-500">monthly</p>
                        </div>
                      </div>
                    ))}
                    <div className="flex justify-between font-bold text-sm pt-3 mt-3 border-t border-gray-700 text-gray-100">
                      <span>Subtotal ({provider.toUpperCase()})</span>
                      <span className="text-green-400 text-lg">
                        {formatCurrency(pricingData.total_costs[provider as keyof typeof pricingData.total_costs])}
                      </span>
                    </div>
                  </div>
                </div>
              )
            ))}
          </div>

          {/* Cost Comparison Summary */}
          {selectedProvider === "all" && (
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <h4 className="font-bold text-gray-200 mb-4">📈 Cost Comparison Summary</h4>
              <div className="space-y-2">
                {["aws", "azure", "gcp"]
                  .sort(
                    (a, b) =>
                      pricingData.total_costs[a as keyof typeof pricingData.total_costs] -
                      pricingData.total_costs[b as keyof typeof pricingData.total_costs]
                  )
                  .map((provider, index) => {
                    const cost = pricingData.total_costs[provider as keyof typeof pricingData.total_costs];
                    const total = Object.values(pricingData.total_costs).reduce((a, b) => a + b, 0);
                    const percentage = (cost / total) * 100;
                    return (
                      <div key={provider} className="flex items-center gap-3">
                        <div className="flex items-center gap-2 min-w-[80px]">
                          <span>{index + 1}.</span>
                          <span className="text-sm font-semibold text-gray-300 uppercase">{provider}</span>
                        </div>
                        <div className="flex-1">
                          <div className="bg-gray-700 rounded-full h-6 overflow-hidden">
                            <div
                              className={`h-full bg-gradient-to-r ${getProviderColor(provider)} flex items-center justify-end pr-2`}
                              style={{ width: `${percentage}%` }}
                            >
                              {percentage > 15 && (
                                <span className="text-xs font-bold text-white">{percentage.toFixed(1)}%</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="text-right min-w-[120px]">
                          <p className="font-bold text-gray-100">{formatCurrency(cost)}</p>
                          <p className="text-xs text-gray-500">{formatCurrency(cost * 12)}/yr</p>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 text-sm text-gray-300">
            <p className="font-semibold text-amber-400 mb-2">ℹ️ Important Notes</p>
            <ul className="list-disc list-inside space-y-1 text-gray-400 text-xs">
              <li>Prices are estimates based on standard US regions</li>
              <li>Does not include data transfer, reserved instances, or spot pricing</li>
              <li>Network costs between regions not included</li>
              <li>Actual costs may vary based on usage patterns and discounts</li>
              <li>Verify with official provider pricing pages before decisions</li>
            </ul>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!pricingData && !loading && (
        <div className="flex items-center justify-center py-12 bg-gray-800/30 rounded-lg border border-gray-700 border-dashed">
          <div className="text-center">
            <p className="text-5xl mb-2">💰</p>
            <p className="text-gray-400">Enter Terraform code or load generated IaC</p>
            <p className="text-xs text-gray-500 mt-2">Then click "Calculate Pricing" to see multi-cloud cost analysis</p>
          </div>
        </div>
      )}
    </div>
  );
}
