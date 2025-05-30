import React, { useState } from "react";
import Step1Upload from "./components/Step1Upload";
import Step2Channel from "./components/Step2Channel";
import Step3Deployments from "./components/Step3Deployments";
import Step4Flow from "./components/Step4Flow";
import Step5ToneCTA from "./components/Step5ToneCTA";
import Step6Review from "./components/Step6Review";
import Step7Export from "./components/Step7Export";

type Step = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export default function App() {
  const [step, setStep] = useState<Step>(1);

  // Global state for all steps
  const [files, setFiles] = useState<File[]>([]);
  const [channel, setChannel] = useState<string>("");
  const [numOutputs, setNumOutputs] = useState<number>(1);
  const [charLimit, setCharLimit] = useState<number>(280);
  const [charReservedForLink, setCharReservedForLink] = useState<number>(40);
  const [flow, setFlow] = useState<string>("");
  const [flowNotes, setFlowNotes] = useState<string[]>([]);
  const [tone, setTone] = useState<string>("");
  const [ctaType, setCtaType] = useState<"preset" | "ai" | "custom">("preset");
  const [ctaText, setCtaText] = useState<string>("");
  const [destinationUrl, setDestinationUrl] = useState<string>("");
  const [utm, setUtm] = useState<{ utm_source: string; utm_medium: string; utm_campaign: string }>({
    utm_source: "",
    utm_medium: "",
    utm_campaign: "",
  });
  const [shortenLinks, setShortenLinks] = useState<boolean>(false);

  // For review & export
  const [outputs, setOutputs] = useState<any[]>([]);
  const [meta, setMeta] = useState<any>({});

  // Step handlers
  const next = () => setStep((s) => (s < 7 ? ((s + 1) as Step) : s));
  const prev = () => setStep((s) => (s > 1 ? ((s - 1) as Step) : s));

  // Reset for new session
  const reset = () => {
    setStep(1);
    setFiles([]);
    setChannel("");
    setNumOutputs(1);
    setCharLimit(280);
    setCharReservedForLink(40);
    setFlow("");
    setFlowNotes([]);
    setTone("");
    setCtaType("preset");
    setCtaText("");
    setDestinationUrl("");
    setUtm({ utm_source: "", utm_medium: "", utm_campaign: "" });
    setShortenLinks(false);
    setOutputs([]);
    setMeta({});
  };

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 16 }}>
      <h1>Content Repurposing Engine</h1>
      <ProgressBar step={step} />
      {step === 1 && (
        <Step1Upload
          files={files}
          setFiles={setFiles}
          onNext={next}
        />
      )}
      {step === 2 && (
        <Step2Channel
          channel={channel}
          setChannel={setChannel}
          onNext={next}
          onPrev={prev}
        />
      )}
      {step === 3 && (
        <Step3Deployments
          numOutputs={numOutputs}
          setNumOutputs={setNumOutputs}
          charLimit={charLimit}
          setCharLimit={setCharLimit}
          charReservedForLink={charReservedForLink}
          setCharReservedForLink={setCharReservedForLink}
          onNext={next}
          onPrev={prev}
        />
      )}
      {step === 4 && (
        <Step4Flow
          flow={flow}
          setFlow={setFlow}
          flowNotes={flowNotes}
          setFlowNotes={setFlowNotes}
          numOutputs={numOutputs}
          onNext={next}
          onPrev={prev}
        />
      )}
      {step === 5 && (
        <Step5ToneCTA
          tone={tone}
          setTone={setTone}
          ctaType={ctaType}
          setCtaType={setCtaType}
          ctaText={ctaText}
          setCtaText={setCtaText}
          destinationUrl={destinationUrl}
          setDestinationUrl={setDestinationUrl}
          utm={utm}
          setUtm={setUtm}
          shortenLinks={shortenLinks}
          setShortenLinks={setShortenLinks}
          onNext={next}
          onPrev={prev}
        />
      )}
      {step === 6 && (
        <Step6Review
          files={files}
          channel={channel}
          numOutputs={numOutputs}
          charLimit={charLimit}
          charReservedForLink={charReservedForLink}
          flow={flow}
          flowNotes={flowNotes}
          tone={tone}
          ctaType={ctaType}
          ctaText={ctaText}
          destinationUrl={destinationUrl}
          utm={utm}
          shortenLinks={shortenLinks}
          outputs={outputs}
          setOutputs={setOutputs}
          meta={meta}
          setMeta={setMeta}
          onNext={next}
          onPrev={prev}
        />
      )}
      {step === 7 && (
        <Step7Export
          outputs={outputs}
          meta={meta}
          onPrev={prev}
          onRestart={reset}
        />
      )}
    </div>
  );
}

function ProgressBar({ step }: { step: number }) {
  const items = [
    "Upload",
    "Channel",
    "Deployments",
    "Flow",
    "Tone/CTA",
    "Review",
    "Export",
  ];
  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
      {items.map((label, idx) => (
        <div
          key={label}
          style={{
            flex: 1,
            padding: 4,
            borderBottom: idx + 1 === step ? "3px solid #1976d2" : "1px solid #ccc",
            color: idx + 1 === step ? "#1976d2" : "#888",
            fontWeight: idx + 1 === step ? "bold" : "normal",
            textAlign: "center",
            fontSize: 14,
          }}
        >
          {idx + 1}. {label}
        </div>
      ))}
    </div>
  );
}