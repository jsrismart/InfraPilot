import React from "react";

type Props = {
  prompt: string;
  setPrompt: (s: string) => void;
  onRun: () => void;
  loading: boolean;
};

export default function PromptForm({ prompt, setPrompt, onRun, loading }: Props) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <label className="block text-sm font-medium text-gray-700 mb-2">Describe infrastructure</label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={5}
        className="w-full border rounded p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder='e.g. "Secure 3-tier app on AWS: VPC, public ALB, EKS cluster, RDS PostgreSQL"'
      />
      <div className="mt-4 flex items-center justify-end gap-3">
        <button
          onClick={() => { setPrompt(""); }}
          className="px-4 py-2 rounded bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          Clear
        </button>
        <button
          onClick={onRun}
          disabled={loading || prompt.trim().length === 0}
          className={`px-4 py-2 rounded text-white ${loading ? "bg-blue-300" : "bg-blue-600 hover:bg-blue-700"}`}
        >
          {loading ? "Running…" : "Run Pipeline"}
        </button>
      </div>
    </div>
  );
}
