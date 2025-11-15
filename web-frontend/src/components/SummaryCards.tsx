interface SummaryCardsProps {
  summary: {
    total_records: number;
    average_flowrate: number;
    average_pressure: number;
    average_temperature: number;
  } | null;
}

const SummaryCards = ({ summary }: SummaryCardsProps) => {
  if (!summary) {
    return null;
  }

  const items = [
    { label: "Total Records", value: summary.total_records.toLocaleString() },
    { label: "Avg Flowrate", value: summary.average_flowrate.toFixed(2) },
    { label: "Avg Pressure", value: summary.average_pressure.toFixed(2) },
    { label: "Avg Temperature", value: summary.average_temperature.toFixed(2) },
  ];

  return (
    <section aria-labelledby="summary-heading" className="panel">
      <h2 id="summary-heading">Summary</h2>
      <div className="summary-cards">
        {items.map((item) => (
          <article key={item.label} className="card" aria-label={item.label}>
            <h3>{item.label}</h3>
            <p>{item.value}</p>
          </article>
        ))}
      </div>
    </section>
  );
};

export default SummaryCards;
