const demoSite = {
  name: "North Terrace mixed-use parcel",
  priority: "High",
  detectionConfidence: "86%",
  businessConfidence: "78%",
  datasetVersion: "mock-dataset-v0",
  modelVersion: "rfdetr-nano-mock-v0",
  trace: [
    "Classified request as site discovery",
    "Retrieved mocked visual detection evidence",
    "Combined evidence with commercial proximity metadata",
    "Routed to human review"
  ]
};

export default function Home() {
  return (
    <main className="shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">GeoSite Agent</p>
          <h1>Real estate development analysis</h1>
        </div>
        <button className="primaryButton">Run demo query</button>
      </section>

      <section className="dashboardGrid">
        <div className="mapPanel">
          <div className="mapHeader">
            <span>Demo region</span>
            <span>Construction-site layer</span>
          </div>
          <div className="mapCanvas">
            <div className="tile tileA" />
            <div className="tile tileB" />
            <div className="tile tileC" />
            <div className="detectionBox" />
            <div className="siteMarker">1</div>
          </div>
        </div>

        <aside className="sidePanel">
          <h2>Priority site</h2>
          <div className="siteCard">
            <div>
              <p className="label">Site</p>
              <strong>{demoSite.name}</strong>
            </div>
            <div className="statusRow">
              <span className="badge high">{demoSite.priority}</span>
              <span>{demoSite.detectionConfidence} detection confidence</span>
            </div>
          </div>

          <h2>Evidence</h2>
          <div className="evidenceList">
            <p>Likely active construction footprint in the selected tile.</p>
            <p>Commercial proximity signal from mocked metadata.</p>
          </div>
        </aside>

        <section className="reportPanel">
          <h2>Agent report</h2>
          <p>
            One high-priority site is ready for analyst review. The current milestone uses mocked
            evidence shaped like the future LangGraph output.
          </p>
          <div className="metricRow">
            <span>Business confidence</span>
            <strong>{demoSite.businessConfidence}</strong>
          </div>
          <ol>
            {demoSite.trace.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </section>

        <section className="opsPanel">
          <h2>MLOps status</h2>
          <div className="metricRow">
            <span>Dataset</span>
            <strong>{demoSite.datasetVersion}</strong>
          </div>
          <div className="metricRow">
            <span>Model</span>
            <strong>{demoSite.modelVersion}</strong>
          </div>
          <div className="metricRow">
            <span>Promotion</span>
            <strong>Mocked</strong>
          </div>
        </section>
      </section>
    </main>
  );
}
