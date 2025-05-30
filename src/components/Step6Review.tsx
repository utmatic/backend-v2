import React, { useState } from "react";

interface Props {
  files: File[];
  channel: string;
  numOutputs: number;
  charLimit: number;
  charReservedForLink: number;
  flow: string;
  flowNotes: string[];
  tone: string;
  ctaType: "preset" | "ai" | "custom";
  ctaText: string;
  destinationUrl: string;
  utm: { utm_source: string; utm_medium: string; utm_campaign: string };
  shortenLinks: boolean;
  outputs: any[];
  setOutputs: (o: any[]) => void;
  meta: any;
  setMeta: (m: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function Step6Review({
  files,
  channel,
  numOutputs,
  charLimit,
  charReservedForLink,
  flow,
  flowNotes,
  tone,
  ctaType,
  ctaText,
  destinationUrl,
  utm,
  shortenLinks,
  outputs,
  setOutputs,
  meta,
  setMeta,
  onNext,
  onPrev,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // Call backend and get outputs
  const handleGenerate = async () => {
    setLoading(true);
    setErr(null);

    const form = new FormData();
    files.forEach((file) => form.append("files", file));
    form.append("channel", channel);
    form.append("num_outputs", String(numOutputs));
    form.append("flow", flow);
    form.append("tone", tone);
    form.append("char_limit", String(charLimit));
    form.append("char_reserved_for_link", String(charReservedForLink));
    form.append("cta_type", ctaType);
    if (ctaText) form.append("cta_text", ctaText);
    if (destinationUrl) form.append("destination_url", destinationUrl);
    if (utm.utm_source) form.append("utm_source", utm.utm_source);
    if (utm.utm_medium) form.append("utm_medium", utm.utm_medium);
    if (utm.utm_campaign) form.append("utm_campaign", utm.utm_campaign);
    form.append("shorten_links", String(shortenLinks));

    try {
      const res = await fetch("/api/repurpose", {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        setErr("Failed to generate outputs.");
        setLoading(false);
        return;
      }
      const data = await res.json();
      setOutputs(data.outputs);
      setMeta(data.meta);
      setLoading(false);
    } catch (e) {
      setErr("Network error.");
      setLoading(false);
    }
  };

  // Allow re-edit of output snippets in place
  const handleEdit = (idx: number, field: string, value: string) => {
    const updated = outputs.map((o, i) =>
      i === idx ? { ...o, [field]: value } : o
    );
    setOutputs(updated);
  };

  return (
    <div>
      <h2>Step 6: Review & Edit Generated Outputs</h2>
      {!outputs.length ? (
        <div>
          <button onClick={onPrev}>Back</button>{" "}
          <button onClick={handleGenerate} disabled={loading}>
            {loading ? "Generating..." : "Generate Outputs"}
          </button>
          {err && <div style={{ color: "red", marginTop: 12 }}>{err}</div>}
        </div>
      ) : (
        <div>
          {outputs.map((o, i) => (
            <div
              key={i}
              style={{
                border: "1px solid #ccc",
                margin: "12px 0",
                padding: 10,
                borderRadius: 6,
                background: "#f9f9f9",
              }}
            >
              <div>
                <strong>#{i + 1}</strong>
              </div>
              <div>
                <label>
                  Main Text:{" "}
                  <textarea
                    value={o.main_text}
                    style={{ width: "100%", minHeight: 60 }}
                    onChange={(e) =>
                      handleEdit(i, "main_text", e.target.value)
                    }
                  />
                </label>
              </div>
              <div>
                <label>
                  CTA:{" "}
                  <input
                    type="text"
                    value={o.cta_text}
                    style={{ width: 180 }}
                    onChange={(e) =>
                      handleEdit(i, "cta_text", e.target.value)
                    }
                  />
                </label>
              </div>
              <div>
                <label>
                  Link:{" "}
                  <input
                    type="text"
                    value={o.cta_link}
                    style={{ width: 320 }}
                    onChange={(e) =>
                      handleEdit(i, "cta_link", e.target.value)
                    }
                  />
                </label>
              </div>
              <div>
                <strong>Full Preview: </strong>
                <span style={{ fontFamily: "monospace" }}>{o.full_text}</span>
              </div>
              <div>
                <small>Character Count: {o.char_count}</small>
              </div>
            </div>
          ))}
          <button onClick={onPrev}>Back</button>{" "}
          <button onClick={onNext}>Continue</button>
        </div>
      )}
    </div>
  );
}