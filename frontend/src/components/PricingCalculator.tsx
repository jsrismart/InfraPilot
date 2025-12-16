import { useState } from "react";
import { GenerateResponse } from "../lib/api";

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

interface PricingCalculatorProps {
  result: GenerateResponse | null;
}

export default function PricingCalculator({ result }: PricingCalculatorProps) {
  const [pricingData, setPricingData] = useState<PricingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<"aws" | "azure" | "gcp" | "all">("all");

  const calculatePricing = async () => {
    if (!result?.iac) return;

    setLoading(true);
    try {
      const terraformCode = Object.values(result.iac).join("\n\n");
      const baseUrl = import.meta.env.VITE_API_BASE || "http://localhost:8001/api/v1";

      const response = await fetch(`${baseUrl}/pricing/calculate-pricing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          terraform_code: terraformCode,
          include_breakdown: true,
          include_comparison: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to calculate pricing");
      }

      const data = await response.json();
      setPricingData(data);
    } catch (error) {
      console.error("Pricing calculation error:", error);
      alert("Failed to calculate pricing. Please try again.");
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

  if (!result?.iac) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <p className="text-gray-400">Generate IaC first to calculate pricing</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Calculate Button */}
      <div className="flex gap-2">
        <button
          onClick={calculatePricing}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          {loading ? "Calculating..." : "💰 Calculate Multi-Cloud Pricing"}
        </button>
      </div>

      {/* Provider Filter */}
      {pricingData && (
        <div className="flex gap-2 flex-wrap">
          <label className="text-sm text-gray-400">View:</label>
          {(["all", "aws", "azure", "gcp"] as const).map((provider) => (
            <button
              key={provider}
              onClick={() => setSelectedProvider(provider)}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                selectedProvider === provider
                  ? "bg-purple-600 text-white"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
            >
              {provider === "all" ? "All Providers" : provider.toUpperCase()}
            </button>
          ))}
        </div>
      )}

      {/* Pricing Results */}
      {pricingData && (
        <div className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {["aws", "azure", "gcp"].map((provider) => (
              (selectedProvider === "all" || selectedProvider === provider) && (
                <div
                  key={provider}
                  className={`p-4 rounded-lg border border-gray-700 ${getProviderBgColor(provider)}`}
                >
                  <div className={`bg-gradient-to-r ${getProviderColor(provider)} p-3 rounded mb-3`}>
                    <h3 className="text-white font-bold text-lg">{provider.toUpperCase()}</h3>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Monthly Cost</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {formatCurrency(pricingData.total_costs[provider as keyof typeof pricingData.total_costs])}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Annual Cost</p>
                      <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
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
            <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
              <p className="text-green-400 font-semibold mb-2">
                ✅ Recommended: {pricingData.comparison.cheapest_provider.toUpperCase()}
              </p>
              <p className="text-sm text-gray-300">
                Monthly: {formatCurrency(pricingData.comparison.monthly_costs[pricingData.comparison.cheapest_provider as keyof typeof pricingData.comparison.monthly_costs])} | 
                Annual: {formatCurrency(pricingData.comparison.annual_costs[pricingData.comparison.cheapest_provider as keyof typeof pricingData.comparison.annual_costs])}
              </p>
            </div>
          )}

          {/* Savings Potential */}
          {pricingData.comparison.savings_potential &&
            Object.entries(pricingData.comparison.savings_potential).length > 0 && (
              <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                <h4 className="text-blue-400 font-semibold mb-3">💡 Savings Potential</h4>
                <div className="space-y-2">
                  {Object.entries(pricingData.comparison.savings_potential).map(
                    ([provider, savings]: [string, any]) => (
                      <div key={provider} className="text-sm">
                        <p className="text-gray-300">
                          <span className="font-semibold uppercase">{provider}:</span> Save{" "}
                          <span className="text-yellow-400 font-bold">
                            {formatCurrency(savings.monthly_savings)}/month
                          </span>{" "}
                          (
                          <span className="text-yellow-400 font-bold">
                            {savings.percent_difference.toFixed(1)}%
                          </span>
                          )
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

          {/* Detailed Breakdown */}
          <div className="space-y-3">
            <h4 className="text-lg font-semibold text-gray-200">📊 Cost Breakdown by Resource</h4>
            {["aws", "azure", "gcp"].map((provider) => (
              (selectedProvider === "all" || selectedProvider === provider) && 
              pricingData.breakdown[provider as keyof typeof pricingData.breakdown].length > 0 && (
                <div key={provider} className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
                  <h5 className="font-semibold text-gray-200 mb-2 uppercase text-sm">{provider}</h5>
                  <div className="space-y-1">
                    {pricingData.breakdown[provider as keyof typeof pricingData.breakdown].map((res, idx) => (
                      <div key={idx} className="flex justify-between text-xs py-1 border-b border-gray-800 last:border-b-0">
                        <div>
                          <p className="font-medium text-gray-300">{res.name}</p>
                          <p className="text-gray-500">{res.description}</p>
                        </div>
                        <p className="font-bold text-green-400">{formatCurrency(res.cost)}</p>
                      </div>
                    ))}
                    <div className="flex justify-between font-bold text-sm pt-2 border-t border-gray-700 text-gray-200">
                      <span>Total {provider.toUpperCase()}</span>
                      <span className="text-green-400">
                        {formatCurrency(pricingData.total_costs[provider as keyof typeof pricingData.total_costs])}
                      </span>
                    </div>
                  </div>
                </div>
              )
            ))}
          </div>

          {/* Info Box */}
          <div className="bg-amber-900/30 border border-amber-700 rounded-lg p-3 text-xs text-gray-300">
            <p className="font-semibold mb-1">ℹ️ Pricing Notes:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-400">
              <li>Estimates based on standard US regions</li>
              <li>Does not include data transfer costs between regions</li>
              <li>Reserved instances and spot pricing not included</li>
              <li>Prices are approximate - verify with provider pricing pages</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
