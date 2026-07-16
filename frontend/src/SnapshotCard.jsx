export default function SnapshotCard({ snapshot }) {
  return (
    <div className="w-full max-w-xl rounded-lg border-l-4 border-signal bg-paper p-8 text-ink shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="font-body text-3xl font-semibold tracking-tight">
            {snapshot.company_name}
          </h2>
          <p className="mt-1 font-mono text-xs text-slate">
            sifted just now
          </p>
        </div>
        {snapshot.funding_stage && (
          <span className="whitespace-nowrap rounded-full bg-signal/15 px-3 py-1 font-mono text-xs text-signal">
            {snapshot.funding_stage}
          </span>
        )}
      </div>

      <Section label="Summary">
        <p className="font-body text-ink/90">{snapshot.summary}</p>
      </Section>

      <Section label="Market Signal" accent>
        <p className="font-body text-ink/90">{snapshot.market_signal}</p>
      </Section>

      <Section label="Funding Stage">
        <p className="font-body text-ink/90">
          {snapshot.funding_stage ?? "Not disclosed"}
        </p>
      </Section>

      <Section label="Founders">
        <p className="font-body text-ink/90">{snapshot.founder_background}</p>
      </Section>

      <Section label="Risk Flags">
        <ul className="flex flex-col gap-2">
          {snapshot.risk_flags.map((flag, i) => (
            <li
              key={i}
              className="rounded-md border-l-2 border-brick bg-brick/5 px-3 py-2 font-body text-sm text-ink/90"
            >
              {flag}
            </li>
          ))}
        </ul>
      </Section>
    </div>
  );
}

function Section({ label, accent, children }) {
  return (
    <div className="mt-6 border-t border-ink/10 pt-6 first:mt-6 first:border-t-0 first:pt-0">
      <div className="mb-2 flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-slate">
        {accent && <span className="h-1.5 w-1.5 rounded-full bg-signal" />}
        {label}
      </div>
      {children}
    </div>
  );
}