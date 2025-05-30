import React, { useEffect, useState } from "react";

interface Props {
  tone: string;
  setTone: (t: string) => void;
  ctaType: "preset" | "ai" | "custom";
  setCtaType: (t: "preset" | "ai" | "custom") => void;
  ctaText: string;
  setCtaText: (t: string) => void;
  destinationUrl: string;
  setDestinationUrl: (t: string) => void;
  utm: { utm_source: string; utm_medium: string; utm_campaign: string };
  setUtm: (u: { utm_source: string; utm_medium: string; utm_campaign: string }) => void;
  shortenLinks: boolean;
  setShortenLinks: (b: boolean) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function Step5ToneCTA({
  tone,
  setTone,
  ctaType,
  setCtaType,
  ctaText,
  setCtaText,
  destinationUrl,
  setDestinationUrl,
  utm,
  setUtm,
  shortenLinks,
  setShortenLinks,
  onNext,
  onPrev,
}: Props) {
  const [tones, setTones] = useState<string[]>([]);
  const [ctas, setCtas] = useState<string[]>([]);
  useEffect(() => {
    fetch("/api/presets/tones")
      .then((r) => r.json())
      .then(setTones);
    fetch("/api/presets/ctas")
      .then((r) => r.json())
      .then(setCtas);
  }, []);

  return (
    <div>
      <h2>Step 5: Tone & CTA Options</h2>
      <div style={{ marginBottom: 16 }}>
        <strong>Choose a tone:</strong>
        <div>
          {tones.map((t) => (
            <label key={t} style={{ marginRight: 12 }}>
              <input
                type="radio"
                checked={tone === t}
                onChange={() => setTone(t)}
              />{" "}
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </label>
          ))}
          <label style={{ marginLeft: 12 }}>
            <input
              type="radio"
              checked={tone && !tones.includes(tone)}
              onChange={() => setTone("")}
            />{" "}
            Custom:{" "}
            <input
              type="text"
              value={!tones.includes(tone) ? tone : ""}
              disabled={tones.includes(tone)}
              onChange={(e) => setTone(e.target.value)}
              placeholder="Enter tone"
              style={{ width: 120 }}
            />
          </label>
        </div>
      </div>
      <div>
        <strong>CTA Options:</strong>
        <div>
          <label>
            <input
              type="radio"
              checked={ctaType === "preset"}
              onChange={() => setCtaType("preset")}
            />{" "}
            Preset
          </label>{" "}
          <label>
            <input
              type="radio"
              checked={ctaType === "ai"}
              onChange={() => setCtaType("ai")}
            />{" "}
            AI-generated
          </label>{" "}
          <label>
            <input
              type="radio"
              checked={ctaType === "custom"}
              onChange={() => setCtaType("custom")}
            />{" "}
            Custom
          </label>
        </div>
        {ctaType === "preset" && (
          <select
            value={ctaText}
            onChange={(e) => setCtaText(e.target.value)}
            style={{ marginTop: 8 }}
          >
            <option value="">Select preset</option>
            {ctas.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        )}
        {ctaType === "custom" && (
          <input
            type="text"
            value={ctaText}
            onChange={(e) => setCtaText(e.target.value)}
            placeholder="Custom CTA"
            style={{ marginLeft: 8, width: 180 }}
          />
        )}
      </div>
      <div style={{ marginTop: 16 }}>
        <strong>Destination URL:</strong>
        <input
          type="text"
          value={destinationUrl}
          onChange={(e) => setDestinationUrl(e.target.value)}
          placeholder="https://yourlandingpage.com"
          style={{ marginLeft: 8, width: 260 }}
        />
      </div>
      <div style={{ marginTop: 8 }}>
        <strong>UTM Parameters:</strong>
        <div>
          <label>
            utm_source:{" "}
            <input
              type="text"
              value={utm.utm_source}
              onChange={(e) =>
                setUtm({ ...utm, utm_source: e.target.value })
              }
              style={{ width: 110 }}
              placeholder="e.g. twitter"
            />
          </label>
          <label style={{ marginLeft: 8 }}>
            utm_medium:{" "}
            <input
              type="text"
              value={utm.utm_medium}
              onChange={(e) =>
                setUtm({ ...utm, utm_medium: e.target.value })
              }
              style={{ width: 110 }}
              placeholder="e.g. social"
            />
          </label>
          <label style={{ marginLeft: 8 }}>
            utm_campaign:{" "}
            <input
              type="text"
              value={utm.utm_campaign}
              onChange={(e) =>
                setUtm({ ...utm, utm_campaign: e.target.value })
              }
              style={{ width: 110 }}
              placeholder="e.g. launch"
            />
          </label>
        </div>
      </div>
      <div style={{ marginTop: 8 }}>
        <label>
          <input
            type="checkbox"
            checked={shortenLinks}
            onChange={(e) => setShortenLinks(e.target.checked)}
          />{" "}
          Automatically shorten links and insert into CTA
        </label>
      </div>
      <button onClick={onPrev} style={{ marginTop: 20 }}>
        Back
      </button>{" "}
      <button
        onClick={onNext}
        disabled={!tone || (ctaType === "preset" && !ctaText)}
        style={{ marginTop: 20 }}
      >
        Continue
      </button>
    </div>
  );
}