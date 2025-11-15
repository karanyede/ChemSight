import { ChangeEvent, useState } from "react";
import { uploadDataset } from "../services/api";

interface UploadPanelProps {
  onUploaded: (datasetId: number) => void;
}

const UploadPanel = ({ onUploaded }: UploadPanelProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isUploading, setUploading] = useState(false);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const candidate = event.target.files?.[0] ?? null;
    setFile(candidate);
    setMessage(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Select a CSV file before uploading.");
      return;
    }
    setUploading(true);
    setMessage(null);
    try {
      const response = await uploadDataset(file);
      setMessage("Upload complete.");
      onUploaded(response.dataset.id);
    } catch (error) {
      setMessage("Upload failed. Please verify the file and try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <section aria-labelledby="upload-heading" className="panel">
      <h2 id="upload-heading">Upload Dataset</h2>
      <p>Submit a CSV file to analyse new equipment data.</p>
      <input
        type="file"
        accept=".csv,text/csv"
        aria-label="Select dataset CSV"
        onChange={handleFileChange}
      />
      <button type="button" onClick={handleUpload} disabled={isUploading}>
        {isUploading ? "Uploading…" : "Upload"}
      </button>
      {message && <p role="status">{message}</p>}
    </section>
  );
};

export default UploadPanel;
