import { useEffect, useState } from 'react'

const STAGES = [
    "Searching for sources...",
    "Extracting facts...",
    "Synthesizing snapshot...",
];

function LoadingSequence() {
    const [stageIndex, setStageIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setStageIndex((prev) => Math.min(prev + 1, STAGES.length - 1));
        }, 1500);
        return () => clearInterval(interval);
    }, []);
    return (
        <div className="flex flex-col gap-2 font-mono text-sm">
            {STAGES.map((stage, i) => (
                <div
                    key={stage}
                    className={`transition-opacity duration-300 ${i <= stageIndex ? "text-signal opacity-100" : "text-slate/40 opacity-60"
                        }`}
                >
                    {stage}
                </div>
            ))}
        </div>
    );
}

export default LoadingSequence