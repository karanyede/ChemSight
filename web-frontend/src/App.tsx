import { ChangeEvent, ReactNode, useEffect, useRef, useState } from "react";
import {
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import NavBar from "./components/NavBar";
import LoginForm from "./components/LoginForm";
import UploadPanel from "./components/UploadPanel";
import SummaryCards from "./components/SummaryCards";
import HistoryTable from "./components/HistoryTable";
import TypeDistributionChart from "./components/TypeDistributionChart";
import {
  DatasetSummary,
  downloadReport,
  getDatasetRecords,
  getDatasetSummary,
  getDatasets,
  getMetrics,
  subscribeToUnauthorized,
} from "./services/api";
import { clearToken, isAuthenticated } from "./utils/auth";

interface DatasetListItem {
  id: number;
  original_filename: string;
  uploaded_at: string;
  total_records: number;
}

interface DatasetListResponse {
  count: number;
  results: DatasetListItem[];
}

interface RecordRow {
  id: number;
  equipment_name: string;
  equipment_type: string;
  flowrate: string;
  pressure: string;
  temperature: string;
}

interface PaginatedRecords {
  count: number;
  results: RecordRow[];
}

const ProtectedLayout = () => {
  return (
    <div className="layout">
      <a className="sr-only" href="#main-content">
        Skip to main content
      </a>
      <NavBar />
      <main id="main-content" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
};

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const DashboardPage = () => {
  const [metrics, setMetrics] = useState<{
    dataset_count: number;
    latest_upload: string | null;
  } | null>(null);
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [distribution, setDistribution] = useState<Record<string, number>>({});

  useEffect(() => {
    getMetrics()
      .then((data) => setMetrics(data))
      .catch(() => setMetrics(null));

    getDatasets({ page_size: 1 })
      .then((response: DatasetListResponse) => {
        if (response.results.length) {
          const latest = response.results[0];
          getDatasetSummary(latest.id).then((datasetSummary) => {
            setSummary(datasetSummary);
            setDistribution(datasetSummary.type_distribution);
          });
        }
      })
      .catch(() => {
        setSummary(null);
        setDistribution({});
      });
  }, []);

  return (
    <div className="grid">
      <section className="panel" aria-labelledby="metrics-heading">
        <h2 id="metrics-heading">Metrics</h2>
        {metrics ? (
          <ul>
            <li>Total datasets: {metrics.dataset_count}</li>
            <li>
              Last upload:{" "}
              {metrics.latest_upload
                ? new Date(metrics.latest_upload).toLocaleString()
                : "—"}
            </li>
          </ul>
        ) : (
          <p>No metrics available yet.</p>
        )}
      </section>
      <SummaryCards summary={summary} />
      {distribution && Object.keys(distribution).length > 0 && (
        <section className="panel" aria-labelledby="distribution-heading">
          <h2 id="distribution-heading">Distribution</h2>
          <TypeDistributionChart data={distribution} />
        </section>
      )}
    </div>
  );
};

const UploadPage = () => {
  const navigate = useNavigate();
  return <UploadPanel onUploaded={(id) => navigate(`/dataset/${id}`)} />;
};

const HistoryPage = () => {
  const [datasets, setDatasets] = useState<DatasetListResponse | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    getDatasets()
      .then((response: DatasetListResponse) => setDatasets(response))
      .catch(() => setDatasets({ count: 0, results: [] }));
  }, []);

  return (
    <HistoryTable
      datasets={datasets?.results ?? []}
      onSelect={(id) => navigate(`/dataset/${id}`)}
    />
  );
};

const DatasetDetailPage = () => {
  const { id } = useParams();
  const datasetId = Number(id);
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [distribution, setDistribution] = useState<Record<string, number>>({});
  const [records, setRecords] = useState<PaginatedRecords>({
    count: 0,
    results: [],
  });
  const [typeFilter, setTypeFilter] = useState("");
  const [sort, setSort] = useState("equipment_name");

  useEffect(() => {
    if (!datasetId) return;
    getDatasetSummary(datasetId).then((data) => {
      setSummary(data);
      setDistribution(data.type_distribution);
    });
  }, [datasetId]);

  useEffect(() => {
    if (!datasetId) return;
    const params = {
      ...(typeFilter ? { type: typeFilter } : {}),
      ...(sort ? { sort } : {}),
    };
    getDatasetRecords(datasetId, params).then((data) =>
      setRecords(data as PaginatedRecords)
    );
  }, [datasetId, typeFilter, sort]);

  const handleDownload = async () => {
    const blob = await downloadReport(datasetId);
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `dataset-${datasetId}.pdf`;
    anchor.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="grid">
      <SummaryCards summary={summary} />
      {distribution && Object.keys(distribution).length > 0 && (
        <section className="panel" aria-labelledby="detail-distribution">
          <h2 id="detail-distribution">Type distribution</h2>
          <TypeDistributionChart data={distribution} />
        </section>
      )}
      <section className="panel" aria-labelledby="records-heading">
        <div className="grid" style={{ gap: "0.75rem" }}>
          <div>
            <h2 id="records-heading">Records</h2>
            <div
              className="grid"
              style={{
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
              }}
            >
              <label>
                Type filter
                <input
                  value={typeFilter}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    setTypeFilter(event.target.value)
                  }
                  aria-label="Filter by equipment type"
                />
              </label>
              <label>
                Sort
                <select
                  value={sort}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                    setSort(event.target.value)
                  }
                  aria-label="Sort records"
                >
                  <option value="equipment_name">Name</option>
                  <option value="flowrate">Flowrate</option>
                  <option value="pressure">Pressure</option>
                  <option value="temperature">Temperature</option>
                  <option value="-flowrate">Flowrate (desc)</option>
                  <option value="-pressure">Pressure (desc)</option>
                  <option value="-temperature">Temperature (desc)</option>
                </select>
              </label>
              <button type="button" onClick={handleDownload}>
                Download PDF report
              </button>
            </div>
          </div>
          <div className="table-container" role="region" aria-live="polite">
            <table>
              <caption className="sr-only">Equipment records</caption>
              <thead>
                <tr>
                  <th scope="col">Name</th>
                  <th scope="col">Type</th>
                  <th scope="col">Flowrate</th>
                  <th scope="col">Pressure</th>
                  <th scope="col">Temperature</th>
                </tr>
              </thead>
              <tbody>
                {records.results.map((row: RecordRow) => (
                  <tr key={row.id}>
                    <td>{row.equipment_name}</td>
                    <td>{row.equipment_type}</td>
                    <td>{row.flowrate}</td>
                    <td>{row.pressure}</td>
                    <td>{row.temperature}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
};

const App = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const mainRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const unsubscribe = subscribeToUnauthorized(() => {
      clearToken();
      navigate("/login", { replace: true, state: { from: location.pathname } });
    });
    return () => unsubscribe();
  }, [navigate, location.pathname]);

  useEffect(() => {
    if (location.pathname !== "/login") {
      const main = document.getElementById("main-content");
      if (main) {
        main.focus();
      }
    }
  }, [location.pathname]);

  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route
        element={
          <ProtectedRoute>
            <ProtectedLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/dataset/:id" element={<DatasetDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;
