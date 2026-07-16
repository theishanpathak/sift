import React from 'react'

function SnapshotForm({ query, setQuery, onSubmit, disabled }) {
    return (
        <form onSubmit={e => {
            e.preventDefault();
            onSubmit();
        }}
            className="flex w-full max-w-xl gap-3"
        >
            <input
                type='text'
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Enter a startup name to get started"
                disabled={disabled}
                className="flex-1 rounded-md border border-slate/30 bg-transparent px-4 py-3
                   font-body text-paper placeholder:text-slate/60
                   focus:outline-none focus:ring-2 focus:ring-signal
                   disabled:opacity-50"
            />
            <button
                type='submit'
                disabled={disabled || !query.trim()}
                className="rounded-md bg-signal px-6 py-3 font-body font-medium text-ink
                   transition hover:opacity-90 disabled:opacity-40"
            >
                Sift
            </button>
        </form>
    )
}

export default SnapshotForm