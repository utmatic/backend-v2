import React from "react";

interface Props {
  flow: string;
  setFlow: (v: string) => void;
  flowNotes: string[];
  setFlowNotes: (notes: string[]) => void;
  numOutputs: number;
  onNext: () => void;
  onPrev: () => void;
}

const FLOWS = [
  { key: "nurture", label: "Nurture/Education (info builds over time)" },
  { key: "urgency", label: "Urgency Escalation" },
  { key: "teaser_to_reveal", label: "Teaser-to-Reveal" },
  { key: "custom", label: "Custom" },
];

export default function Step4Flow({
  flow,
  setFlow,
  flowNotes,
  setFlowNotes,
  numOutputs,
  onNext,
  onPrev,
}: Props) {
  return (
    <div>
      <h2>Step 4: Set Communication Flow/Progression</h2>
      <div style={{ marginBottom: 16 }}>
        {FLOWS.map((f) => (
          <label key={f.key} style={{ display: "block", margin: 4 }}>
            <input
              type="radio"
              checked={flow === f.key}
              onChange={() => setFlow(f.key)}
            />{" "}
            {f.label}
          </label>
        ))}
      </div>
      <div>
        <strong>Optional: Add a note/goal for each piece</strong>
        <div>
          {Array.from({ length: numOutputs }).map((_, i) => (
            <div key={i} style={{ margin: "4px 0" }}>
              {i + 1}.{" "}
              <input
                style={{ width: 320 }}
                type="text"
                value={flowNotes[i] || ""}
                onChange={(e) => {
                  const updated = [...flowNotes];
                  updated[i] = e.target.value;
                  setFlowNotes(updated);
                }}
                placeholder={`e.g. "Introduce topic"`}
              />
            </div>
          ))}
        </div>
      </div>
      <button onClick={onPrev}>Back</button>{" "}
      <button onClick={onNext} disabled={!flow}>
        Continue
      </button>
    </div>
  );
}