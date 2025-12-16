import JSZip from "jszip";

/**
 * Downloads Terraform files as a ZIP archive
 * @param iacCode Object containing filename: code pairs
 * @param projectName Optional name for the ZIP file (default: 'terraform-infrastructure')
 */
export async function downloadTerraformAsZip(
  iacCode: Record<string, string>,
  projectName: string = "terraform-infrastructure"
): Promise<void> {
  try {
    const zip = new JSZip();

    // Add each Terraform file to the ZIP
    Object.entries(iacCode).forEach(([filename, code]) => {
      zip.file(filename, code);
    });

    // Generate the ZIP file
    const blob = await zip.generateAsync({ type: "blob" });

    // Create a download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${projectName}.zip`;

    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error downloading Terraform files:", error);
    throw new Error("Failed to download Terraform files as ZIP");
  }
}
