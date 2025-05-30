import React, { useEffect, useState } from "react";

interface Props {
  channel: string;
  setChannel: (c: string) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function Step2Channel({
  channel,
  setChannel,
  onNext,
  onPrev,
}: Props) {
  const [channels, setChannels] = useState<string[]>([]);
  const [custom, setCustom] = useState("");

  useEffect(() => {
    fetch("/api/presets/channels")
      .then((r) => r.json())
      .then(setChannels);
  }, []);

  return (
    <div>
      <h2>Step 2: Select Channel/Medium</h2>
      <div style={{ marginBottom: 16 }}>
        {channels.map((ch) =>
          ch !== "custom" ? (
            <label key={ch} style={{ display: "block", margin: 4 }}>
              <input
                type="radio"
                checked={channel === ch}
                onChange={() => setChannel(ch)}
              />{" "}
              {ch.charAt(0).toUpperCase() + ch.slice(1).replace("_", " ")}
            </label>
          ) : null
        )}
        <label style={{ display: "block", margin: 4 }}>
          <input
            type="radio"
            checked={channel === "custom"}
            onChange={() => setChannel("custom")}
          />{" "}
          Custom:{" "}
          <input
            type="text"
            value={custom}
            onChange={(e) => {
              setCustom(e.target.value);
              setChannel("custom");
            }}
            disabled={channel !== "custom"}
            placeholder="Your custom channel"
            style={{ marginLeft: 4 }}
          />
        </label>
      </div>
      <button onClick={onPrev}>Back</button>{" "}
      <button
        onClick={onNext}
        disabled={!channel || (channel === "custom" && !custom)}
      >
        Continue
      </button>
    </div>
  );
}