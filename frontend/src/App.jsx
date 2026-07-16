import { useState } from 'react'
import SnapshotForm from './SnapshotForm'
import LoadingSequence from './LoadingSequence'
import SnapshotCard from './SnapshotCard'

const API_URL = import.meta.env.VITE_API_URL

function App() {
  const [query, setQuery] = useState("");
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setSnapshot(null);

    try {
      const res = await fetch(`${API_URL}/api/snapshot`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail || "Something went wrong. Please try again.")
      }

      const data = await res.json();
      setSnapshot(data);
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="flex min-h-screen flex-col items-center gap-10 bg-ink px-4 py-20">
      <div className="text-center">
        <h1 className="font-display text-5xl font-semibold text-paper">Sift</h1>
        <p className="mt-2 font-body text-slate">
          Sift through the noise. Get the signal on any startup.
        </p>
      </div>

      <SnapshotForm
        query={query}
        setQuery={setQuery}
        onSubmit={handleSubmit}
        disabled={loading}
      />

      {loading && <LoadingSequence />}

      {error && (
        <p className="max-w-xl text-center font-body text-brick">{error}</p>
      )}

      {snapshot && <SnapshotCard snapshot={snapshot} />}
    </div>
  );
}

export default App
