interface DatasetRow {
  id: number;
  original_filename: string;
  uploaded_at: string;
  total_records: number;
}

interface HistoryTableProps {
  datasets: DatasetRow[];
  onSelect: (id: number) => void;
}

const HistoryTable = ({ datasets, onSelect }: HistoryTableProps) => {
  if (!datasets.length) {
    return <p>No datasets uploaded yet.</p>;
  }
  return (
    <section aria-labelledby="history-heading" className="panel">
      <h2 id="history-heading">History</h2>
      <div className="table-container" role="region" aria-live="polite">
        <table>
          <caption className="sr-only">Uploaded dataset history</caption>
          <thead>
            <tr>
              <th scope="col">Filename</th>
              <th scope="col">Uploaded</th>
              <th scope="col">Records</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.id}>
                <td>{dataset.original_filename}</td>
                <td>{new Date(dataset.uploaded_at).toLocaleString()}</td>
                <td>{dataset.total_records}</td>
                <td>
                  <button type="button" onClick={() => onSelect(dataset.id)}>
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default HistoryTable;
