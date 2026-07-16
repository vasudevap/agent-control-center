const agents = [
  { name: "Communications", state: "Healthy", meta: "12m ago", tone: "good" },
  { name: "Document filing", state: "Running", meta: "Step 3 of 5", tone: "active" },
  { name: "Travel intelligence", state: "Review", meta: "1 approval", tone: "warn" },
];

const pillars = [
  {
    number: "01",
    title: "Control",
    copy: "Inspect, pause, stop, or authorize autonomous behavior without surrendering human authority.",
    proof: "Lifecycle controls · approvals · policies",
  },
  {
    number: "02",
    title: "Trust",
    copy: "Follow the evidence behind every material action, outcome, failure, and decision.",
    proof: "Runs · events · artifacts · audit",
  },
  {
    number: "03",
    title: "Clarity",
    copy: "See current state, operational risk, and required action before configuration complexity.",
    proof: "Fleet health · alerts · schedules",
  },
];

const maturity = [
  {
    label: "Built",
    tone: "built",
    summary: "Interactive product evidence",
    items: ["Operational dashboard", "Agent inventory and detail", "Human approvals prototype"],
  },
  {
    label: "Designed",
    tone: "designed",
    summary: "Documented platform architecture",
    items: ["Control and execution planes", "Connector and runtime contracts", "Approval decision integrity"],
  },
  {
    label: "Planned",
    tone: "planned",
    summary: "Production delivery roadmap",
    items: ["Backend, scheduler, and workers", "Production connectors", "Gmail reference agent"],
  },
];

function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <span className={`brand ${compact ? "brand-compact" : ""}`}>
      <span className="brand-mark" aria-hidden="true">
        <span>A</span>
      </span>
      <span className="brand-copy">
        <strong>Atlas</strong>
        {!compact && <small>Enterprise Agent Control Center</small>}
      </span>
    </span>
  );
}

function Arrow() {
  return <span aria-hidden="true">↗</span>;
}

function SectionIntro({
  eyebrow,
  title,
  copy,
}: {
  eyebrow: string;
  title: string;
  copy: string;
}) {
  return (
    <div className="section-intro">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p className="section-lede">{copy}</p>
    </div>
  );
}

function FleetPreview() {
  return (
    <div className="console" aria-label="Fictional Atlas operational dashboard preview">
      <div className="console-topbar">
        <div className="console-brand">
          <span className="mini-mark">A</span>
          <span>Atlas</span>
        </div>
        <div className="console-context">
          <span className="console-environment">Production</span>
          <span className="operator-avatar">OP</span>
        </div>
      </div>

      <div className="console-body">
        <aside className="console-rail" aria-label="Preview navigation">
          <span className="rail-item rail-active">Overview</span>
          <span className="rail-item">Agents</span>
          <span className="rail-item">Runs</span>
          <span className="rail-item">Approvals</span>
          <span className="rail-item">Connectors</span>
        </aside>

        <div className="console-main">
          <div className="console-heading">
            <div>
              <span className="console-kicker">Operational overview</span>
              <strong>Good morning, Operator</strong>
            </div>
            <span className="system-state"><i /> Systems nominal</span>
          </div>

          <div className="metric-grid">
            <div className="metric metric-primary">
              <span>Fleet health</span>
              <strong>8 / 9</strong>
              <small>Agents operating normally</small>
            </div>
            <div className="metric">
              <span>Active runs</span>
              <strong>3</strong>
              <small>1 requires review</small>
            </div>
            <div className="metric">
              <span>Pending approvals</span>
              <strong>2</strong>
              <small>Oldest · 14 minutes</small>
            </div>
          </div>

          <div className="console-lower">
            <div className="fleet-panel">
              <div className="panel-heading">
                <strong>Agent fleet</strong>
                <span>View all</span>
              </div>
              {agents.map((agent) => (
                <div className="agent-row" key={agent.name}>
                  <span className="agent-glyph">{agent.name.slice(0, 2).toUpperCase()}</span>
                  <span className="agent-name">{agent.name}</span>
                  <span className={`state state-${agent.tone}`}><i />{agent.state}</span>
                  <small>{agent.meta}</small>
                </div>
              ))}
            </div>

            <div className="attention-panel">
              <span className="panel-label">Needs attention</span>
              <strong>Draft reply requires approval</strong>
              <p>Communications agent · High risk</p>
              <div className="attention-meta">
                <span>Expires in 46m</span>
                <span className="review-link">Review</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <>
      <a className="skip-link" href="#main-content">Skip to content</a>

      <header className="site-header">
        <div className="shell header-inner">
          <a className="brand-link" href="#top" aria-label="Atlas home">
            <Brand />
          </a>
          <nav className="primary-nav" aria-label="Primary">
            <a href="#product">Product</a>
            <a href="#control">Control</a>
            <a href="#architecture">Architecture</a>
            <a href="#status">Status</a>
          </nav>
          <a className="button button-small button-dark" href="#product">
            Explore Atlas <Arrow />
          </a>
        </div>
      </header>

      <main id="main-content">
        <section className="hero" id="top">
          <div className="hero-grid" aria-hidden="true" />
          <div className="shell hero-layout">
            <div className="hero-copy">
              <p className="eyebrow"><span /> Enterprise Agent Control Center</p>
              <h1>Keep autonomous work <em>under control.</em></h1>
              <p className="hero-lede">
                Atlas brings agents, runs, approvals, connectors, and operational evidence into one governed workspace.
              </p>
              <div className="hero-actions">
                <a className="button button-primary" href="#product">Explore Atlas <Arrow /></a>
                <a className="text-link" href="#architecture">View the architecture <span aria-hidden="true">↓</span></a>
              </div>
              <p className="development-note">
                <span className="pulse" aria-hidden="true" />
                <strong>In active development</strong>
                <span>Product prototype and architecture reference</span>
              </p>
            </div>

            <div className="hero-product">
              <div className="product-caption">
                <span>Atlas control center</span>
                <span>Frontend prototype · Fictional data</span>
              </div>
              <FleetPreview />
            </div>
          </div>
        </section>

        <section className="problem section" aria-labelledby="problem-title">
          <div className="shell problem-layout">
            <div className="problem-copy">
              <p className="eyebrow">The operational gap</p>
              <h2 id="problem-title">More agents should not mean less control.</h2>
            </div>
            <p className="problem-lede">
              Agents are moving from isolated experiments into persistent operating systems. Their schedules, credentials, decisions, and failures cannot remain scattered across disconnected tools.
            </p>
          </div>

          <div className="shell control-map" aria-label="Disconnected agent operations unified through Atlas">
            <div className="fragmented-side">
              <span className="map-label">Fragmented operations</span>
              <div className="fragment-grid">
                {[
                  ["AG", "Agents"], ["SC", "Schedules"], ["CR", "Credentials"],
                  ["AP", "Approvals"], ["LG", "Logs"], ["OU", "Outputs"],
                ].map(([code, label]) => (
                  <div className="fragment" key={code}><span>{code}</span><small>{label}</small></div>
                ))}
              </div>
            </div>
            <div className="map-flow" aria-hidden="true"><span /><i>→</i><span /></div>
            <div className="unified-side">
              <span className="map-label">Governed operations</span>
              <div className="atlas-node">
                <span className="node-orbit orbit-one" />
                <span className="node-orbit orbit-two" />
                <span className="node-core">A</span>
                <strong>Atlas</strong>
                <small>Control plane</small>
              </div>
            </div>
          </div>
        </section>

        <section className="pillars section" id="control" aria-labelledby="pillars-title">
          <div className="shell">
            <SectionIntro
              eyebrow="Operating principles"
              title="Autonomy with structure."
              copy="Atlas is shaped around three principles that keep agent operations understandable and accountable."
            />
            <div className="pillar-grid" id="pillars-title">
              {pillars.map((pillar) => (
                <article className="pillar" key={pillar.title}>
                  <span className="pillar-number">{pillar.number}</span>
                  <h3>{pillar.title}</h3>
                  <p>{pillar.copy}</p>
                  <small>{pillar.proof}</small>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="product section" id="product" aria-labelledby="product-title">
          <div className="shell">
            <SectionIntro
              eyebrow="One operating environment"
              title="Know what is running. Know what requires you."
              copy="Atlas organizes agent operations around stable objects and the questions an operator needs answered first."
            />

            <div className="feature-grid" id="product-title">
              <article className="feature-card feature-fleet">
                <div className="feature-copy">
                  <span className="feature-index">01 · Fleet awareness</span>
                  <h3>See every agent and its operating state.</h3>
                  <p>Health, status, ownership, last run, next run, and current issues stay visible in one inventory.</p>
                </div>
                <div className="mini-table" aria-label="Fictional agent fleet status">
                  <div className="mini-table-head"><span>Agent</span><span>Health</span><span>Next run</span></div>
                  <div><strong>Communications</strong><span className="good-text">● Healthy</span><small>08:30</small></div>
                  <div><strong>Document filing</strong><span className="active-text">◉ Running</span><small>Manual</small></div>
                  <div><strong>Travel intelligence</strong><span className="warn-text">◆ Review</span><small>Tomorrow</small></div>
                </div>
              </article>

              <article className="feature-card feature-run">
                <div className="feature-copy">
                  <span className="feature-index">02 · Run evidence</span>
                  <h3>Follow what happened, step by step.</h3>
                  <p>Inspect triggers, events, tools, decisions, outputs, failures, and retry history without reconstructing a run from raw logs.</p>
                </div>
                <ol className="run-timeline" aria-label="Fictional agent run timeline">
                  <li className="complete"><span>08:30:02</span><strong>Run started</strong><small>Scheduled trigger</small></li>
                  <li className="complete"><span>08:30:05</span><strong>Messages classified</strong><small>24 records</small></li>
                  <li className="current"><span>08:30:08</span><strong>Approval requested</strong><small>Draft external reply</small></li>
                </ol>
              </article>

              <article className="feature-card feature-approval">
                <div className="feature-copy">
                  <span className="feature-index">03 · Human approvals</span>
                  <h3>Review the exact action before it proceeds.</h3>
                  <p>Action, target, consequence, evidence, policy, risk, and timing belong in the decision context.</p>
                </div>
                <div className="approval-preview">
                  <div className="approval-head"><span>Approval AP-1042</span><strong>High risk</strong></div>
                  <p>Send an external draft reply to a new recipient.</p>
                  <dl>
                    <div><dt>Agent</dt><dd>Communications</dd></div>
                    <div><dt>Policy</dt><dd>External communication</dd></div>
                  </dl>
                  <div className="approval-actions"><span>Reject</span><span className="approve">Review evidence</span></div>
                </div>
              </article>

              <article className="feature-card feature-connector">
                <div className="feature-copy">
                  <span className="feature-index">04 · Governed connections</span>
                  <h3>Control how agents reach external systems.</h3>
                  <p>Standard connector contracts isolate credentials, normalize errors, expose health, and apply policy before action.</p>
                </div>
                <div className="connector-list" aria-label="Fictional connector health">
                  <div><span className="connector-icon">GM</span><strong>Gmail</strong><small>3 dependent agents</small><i className="connector-good">Healthy</i></div>
                  <div><span className="connector-icon">GD</span><strong>Google Drive</strong><small>2 dependent agents</small><i className="connector-good">Healthy</i></div>
                  <div><span className="connector-icon">NT</span><strong>Notion</strong><small>Reconnect in 3 days</small><i className="connector-warn">Attention</i></div>
                </div>
              </article>
            </div>
          </div>
        </section>

        <section className="authority section" aria-labelledby="authority-title">
          <div className="shell authority-layout">
            <div className="authority-copy">
              <p className="eyebrow eyebrow-light">Human-in-the-loop</p>
              <h2 id="authority-title">Human authority is part of the architecture.</h2>
              <p>
                Approval is more than a confirmation button. Atlas is designed to bind one exact action to its evidence, risk, policy context, reviewer decision, and recoverable continuation state.
              </p>
              <div className="prototype-note"><span>Frontend prototype</span> Displayed decisions are local simulations and do not execute real actions.</div>
            </div>

            <div className="decision-manifest" aria-label="Example approval decision manifest">
              <div className="manifest-top"><span>Decision context manifest</span><span className="manifest-id">AP-1042 · rev 3</span></div>
              <div className="manifest-action">
                <span>Proposed action</span>
                <strong>Send external draft reply</strong>
                <p>To: new recipient · Account renewal inquiry</p>
              </div>
              <div className="manifest-grid">
                <div><span>Risk</span><strong className="high-risk">High</strong></div>
                <div><span>Policy</span><strong>COMM-04</strong></div>
                <div><span>Evidence</span><strong>4 items</strong></div>
                <div><span>Expires</span><strong>46 minutes</strong></div>
              </div>
              <div className="manifest-lock"><span aria-hidden="true">◇</span><p><strong>Decision integrity</strong><small>Context identity · reviewer provenance · continuation intent</small></p></div>
            </div>
          </div>
        </section>

        <section className="architecture section" id="architecture" aria-labelledby="architecture-title">
          <div className="shell">
            <SectionIntro
              eyebrow="Architecture by design"
              title="Built as a control plane, not a collection of scripts."
              copy="Atlas separates management and governance from agent execution so the operating model can evolve without coupling every agent to the dashboard."
            />

            <div className="architecture-map" id="architecture-title">
              <div className="plane plane-control">
                <div className="plane-heading"><span>01</span><div><strong>Control plane</strong><small>Defines intent and authority</small></div></div>
                <div className="plane-items"><span>Registry</span><span>Schedules</span><span>Policies</span><span>Approvals</span><span>Health</span><span>Audit</span></div>
              </div>
              <div className="governed-boundary">
                <span>Governed boundary</span>
                <div><i /> Validated contracts <i /></div>
              </div>
              <div className="plane plane-execution">
                <div className="plane-heading"><span>02</span><div><strong>Execution plane</strong><small>Performs bounded work</small></div></div>
                <div className="plane-items"><span>Agent runtime</span><span>Tool calls</span><span>Connectors</span><span>LLM requests</span><span>Workers</span><span>Outputs</span></div>
              </div>
            </div>

            <div className="architecture-principles">
              <span>Framework-independent contracts</span>
              <span>Least privilege</span>
              <span>Structured outputs</span>
              <span>Observable by default</span>
            </div>
          </div>
        </section>

        <section className="status section" id="status" aria-labelledby="status-title">
          <div className="shell">
            <SectionIntro
              eyebrow="Delivery status"
              title="Clear about what exists today."
              copy="Atlas treats implementation evidence and architecture intent as different things. The website does the same."
            />

            <div className="maturity-grid" id="status-title">
              {maturity.map((group) => (
                <article className={`maturity-card maturity-${group.tone}`} key={group.label}>
                  <div className="maturity-head"><span className="maturity-dot" /><strong>{group.label}</strong></div>
                  <p>{group.summary}</p>
                  <ul>{group.items.map((item) => <li key={item}>{item}</li>)}</ul>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="reference section" aria-labelledby="reference-title">
          <div className="shell reference-layout">
            <div className="reference-copy">
              <p className="eyebrow">First reference implementation</p>
              <h2 id="reference-title">One real workflow to exercise the whole platform.</h2>
              <p>
                The planned Gmail Triage Agent will validate connectors, scheduling, structured model output, human approval, audit evidence, and operational recovery through one understandable workflow.
              </p>
              <span className="planned-label">Planned capability</span>
            </div>

            <div className="mail-flow" aria-label="Planned Gmail triage agent workflow">
              <div className="mail-source"><span>GM</span><strong>Gmail</strong><small>Eligible messages</small></div>
              <div className="flow-line"><i /><i /><i /></div>
              <div className="flow-steps">
                <span>Classify</span><span>Apply labels</span><span>Prepare drafts</span><span>Route approvals</span><span>Record evidence</span>
              </div>
            </div>
          </div>
        </section>

        <section className="closing" aria-labelledby="closing-title">
          <div className="closing-grid" aria-hidden="true" />
          <div className="shell closing-layout">
            <div>
              <p className="eyebrow eyebrow-light">Control before automation</p>
              <h2 id="closing-title">Autonomous systems should remain understandable.</h2>
            </div>
            <div className="closing-actions">
              <a className="button button-light" href="#product">Explore the Atlas product <Arrow /></a>
              <a className="text-link text-link-light" href="#status">Review delivery status <span aria-hidden="true">↑</span></a>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="shell footer-main">
          <Brand />
          <p>A governed operating environment for autonomous work.</p>
          <nav aria-label="Footer">
            <a href="#product">Product</a>
            <a href="#architecture">Architecture</a>
            <a href="#status">Status</a>
          </nav>
        </div>
        <div className="shell footer-meta">
          <span>© 2026 Atlas</span>
          <span>In active development · Product prototype and architecture reference</span>
        </div>
      </footer>
    </>
  );
}
