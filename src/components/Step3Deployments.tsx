import React from "react";

interface Props {
  numOutputs: number;
  setNumOutputs: (n: number) => void;
  charLimit: number;
  setCharLimit: (n: number) => void;
  charReservedForLink: number;
  setCharReservedForLink: (n: number) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function Step3Deployments({
  numOutputs,
  setNumOutputs,
  charLimit,
  setCharLimit,
  charReservedForLink,
  setCharReservedForLink,
  onNext,
  onPrev,
}: Props) {
  return (
    <div>
      <h2>Step 3: Number of Deployments & Character Limit</h2>
      <div style={{ marginBottom: 16 }}>
        <label>
          Number of snippets/posts/emails:{" "}
          <input
            type="number"
            min={1}
            max={10}
            value={numOutputs}
            onChange={(e) => setNumOutputs(Number(e.target.value))}
            style={{ width: 60 }}
          />
        </label>
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>
          Max character limit per output:{" "}
          <input
            type="number"
            min={60}
            max={3000}
            value={charLimit}
            onChange={(e) => setCharLimit(Number(e.target.value))}
            style={{ width: 80 }}
          />
        </label>
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>
          Reserve characters for CTA & link:{" "}
          <input
            type="number"
            min={0}
            max={charLimit - 20}
            value={charReservedForLink}
            onChange={(e) => setCharReservedForLink(Number(e.target.value))}
            style={{ width: 60 }}
          />
        </label>
      </div>
      <button onClick={onPrev}>Back</button>{" "}
      <button onClick={onNext}>Continue</button>
    </div>
  );
}