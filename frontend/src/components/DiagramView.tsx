import { useState } from "react";
import { GenerateResponse } from "../lib/api";

interface DiagramViewProps {
  result: GenerateResponse | null;
  loading?: boolean;
}

export default function DiagramView({ result, loading }: DiagramViewProps) {
  const [diagramType, setDiagramType] = useState<"ascii" | "mermaid" | "lucidchart" | "json" | "svg" | "png" | "html">("svg");
  const [diagramContent, setDiagramContent] = useState<string | null>(null);
  const [diagramLoading, setDiagramLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const generateDiagram = async () => {
    if (!result?.iac) return;

    setDiagramLoading(true);
    try {
      // Combine all IaC files into one
      const terraformCode = Object.values(result.iac).join("\n\n");

      const baseUrl = import.meta.env.VITE_API_BASE || "http://localhost:8001/api/v1";
      const response = await fetch(`${baseUrl}/diagram/generate-diagram`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          terraform_code: terraformCode,
          diagram_type: diagramType,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate diagram");
      }

      const data = await response.json();
      setDiagramContent(data.content);
      
      // Auto-show preview for HTML diagrams
      if (diagramType === "html") {
        setShowPreview(true);
      }
    } catch (error) {
      console.error("Diagram generation error:", error);
      setDiagramContent("Failed to generate diagram. Please try again.");
    } finally {
      setDiagramLoading(false);
    }
  };

  const downloadDiagram = () => {
    if (!diagramContent) return;

    let filename = `infrastructure-diagram.${getFileExtension()}`;
    let content = diagramContent;
    let mimeType = "text/plain";

    if (diagramType === "png") {
      // Download PNG as base64
      const link = document.createElement("a");
      link.href = `data:image/png;base64,${diagramContent}`;
      link.download = filename;
      link.click();
      return;
    } else if (diagramType === "svg") {
      mimeType = "image/svg+xml";
    } else if (diagramType === "html") {
      mimeType = "text/html";
    } else if (diagramType === "json") {
      mimeType = "application/json";
    }

    const element = document.createElement("a");
    element.setAttribute("href", `data:${mimeType};charset=utf-8,${encodeURIComponent(content)}`);
    element.setAttribute("download", filename);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getFileExtension = () => {
    switch (diagramType) {
      case "png":
        return "png";
      case "svg":
        return "svg";
      case "html":
        return "html";
      case "json":
        return "json";
      case "mermaid":
        return "md";
      case "lucidchart":
        return "md";
      default:
        return "txt";
    }
  };

  const copyToClipboard = () => {
    if (!diagramContent) return;
    navigator.clipboard.writeText(diagramContent);
    alert("Diagram copied to clipboard!");
  };

  if (!result?.iac) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <p className="text-gray-400">Generate IaC first to create diagrams</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Diagram Type Selector */}
      <div className="flex gap-2 flex-wrap">
        <label className="text-sm text-gray-400">Diagram Type:</label>
        {(["svg", "html", "png", "ascii", "mermaid", "lucidchart", "json"] as const).map((type) => (
          <button
            key={type}
            onClick={() => setDiagramType(type)}
            disabled={diagramLoading}
            className={`px-3 py-1 rounded text-sm font-medium transition ${
              diagramType === type
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            } disabled:opacity-50`}
            title={
              type === "svg"
                ? "Scalable vector graphics"
                : type === "html"
                ? "Interactive diagram with canvas"
                : type === "png"
                ? "Raster image format"
                : ""
            }
          >
            {type.toUpperCase()}
            {type === "svg" && " 📊"}
            {type === "html" && " 🎨"}
            {type === "png" && " 🖼️"}
          </button>
        ))}
      </div>

      {/* Generate and Download Buttons */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={generateDiagram}
          disabled={diagramLoading || !result?.iac}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          {diagramLoading ? "Generating..." : `Generate ${diagramType.toUpperCase()}`}
        </button>

        {diagramContent && (
          <>
            <button
              onClick={downloadDiagram}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
              title="Download diagram file"
            >
              📥 Download
            </button>
            <button
              onClick={copyToClipboard}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition"
              title="Copy to clipboard"
            >
              📋 Copy
            </button>
          </>
        )}
      </div>

      {/* Diagram Display */}
      {diagramContent && (
        <div className="bg-black/30 rounded-lg border border-gray-700 overflow-hidden">
          {diagramType === "ascii" ? (
            <pre className="text-xs text-gray-100 overflow-auto max-h-[600px] font-mono p-4">
              {diagramContent}
            </pre>
          ) : diagramType === "mermaid" ? (
            <div className="bg-white p-4">
              <pre className="text-xs overflow-auto max-h-[600px] font-mono text-gray-800">
                {diagramContent}
              </pre>
              <p className="text-xs text-gray-600 mt-2">
                💡 Copy the above code and paste in: <a href="https://mermaid.live" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">mermaid.live</a>, GitHub, or GitLab
              </p>
            </div>
          ) : diagramType === "lucidchart" ? (
            <div className="bg-white p-4">
              <pre className="text-xs overflow-auto max-h-[600px] font-mono text-gray-800">
                {diagramContent}
              </pre>
              <p className="text-xs text-gray-600 mt-2">
                💡 Copy the above code and paste in: <a href="https://lucidchart.com" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">Lucidchart</a> (Use Mermaid import feature) or <a href="https://mermaid.live" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">mermaid.live</a>
              </p>
            </div>
          ) : diagramType === "svg" ? (
            <div className="bg-white overflow-auto max-h-[600px] flex items-center justify-center p-4">
              <div
                dangerouslySetInnerHTML={{ __html: diagramContent }}
                className="inline-block"
              />
            </div>
          ) : diagramType === "png" ? (
            <div className="bg-white overflow-auto max-h-[600px] flex items-center justify-center p-4">
              <img
                src={`data:image/png;base64,${diagramContent}`}
                alt="Infrastructure Diagram"
                className="max-w-full max-h-full"
              />
            </div>
          ) : diagramType === "html" ? (
            <div className="space-y-2 p-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
                >
                  {showPreview ? "Hide Preview" : "Show Preview"}
                </button>
                <span className="text-gray-400 text-sm">Interactive HTML Diagram</span>
              </div>
              {showPreview ? (
                <iframe
                  srcDoc={diagramContent}
                  className="w-full border border-gray-600 rounded"
                  style={{ height: "600px" }}
                  title="Diagram Preview"
                />
              ) : (
                <pre className="text-xs text-gray-100 overflow-auto max-h-[500px] font-mono bg-black/50 p-2 rounded">
                  {diagramContent.substring(0, 500)}...
                </pre>
              )}
            </div>
          ) : (
            <pre className="text-xs text-gray-100 overflow-auto max-h-[600px] font-mono p-4">
              {typeof diagramContent === "string" 
                ? JSON.stringify(JSON.parse(diagramContent), null, 2)
                : diagramContent}
            </pre>
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3 text-sm text-gray-300">
        <p className="font-semibold mb-1">💡 Diagram Tips:</p>
        <ul className="list-disc list-inside space-y-1 text-xs">
          {diagramType === "svg" && <li>Vector-based diagram - perfect for scaling and printing</li>}
          {diagramType === "html" && <li>Interactive diagram - hover and click for resource details</li>}
          {diagramType === "png" && <li>Raster image - best for sharing and presentations</li>}
          {(diagramType === "mermaid" || diagramType === "lucidchart") && <li>Paste in Lucidchart, GitHub/GitLab markdown, or mermaid.live</li>}
          <li>Use Download button to save the diagram</li>
          <li>Use Copy button to copy and paste elsewhere</li>
        </ul>
      </div>
    </div>
  );
}
