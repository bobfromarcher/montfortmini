"use client";

import { useEffect, useRef, useState } from "react";
import type { ChangeEvent, PointerEvent, ReactNode } from "react";

type Mode = "object-swap" | "motion-transfer";
type Box = [number, number, number, number];
type Connection = { configured: boolean; features: { objectSwap: boolean; motionTransfer: boolean }; limits: { maxVideoBytes: number; maxImageBytes: number; maxFrames: number; maxSide: number }; message?: string };
type Result = { source_video_b64: string; generated_video_b64: string; composite_video_b64: string; manifest: object; workflow: object };
type Phase = "idle" | "submitting" | "queued" | "running" | "succeeded" | "failed";
type JobResponse = { id?: string; status?: "queued" | "running" | "succeeded" | "failed"; error?: string; result?: Result };
const START: Box = [0.3, 0.25, 0.4, 0.5];

function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, ReactNode> = {
    upload: <><path d="M12 16V4m-4 4 4-4 4 4M4 15v5h16v-5" /></>,
    arrow: <path d="M4 12h15m-5-5 5 5-5 5" />,
    play: <path d="m9 5 11 7-11 7z" />,
    pause: <path d="M8 5v14M16 5v14" />,
    download: <path d="M12 3v12m-4-4 4 4 4-4M4 17v3h16v-3" />,
    swap: <path d="M4 7h15m-4-4 4 4-4 4M20 17H5m4-4-4 4 4 4" />,
    motion: <path d="M3 7h8m-6 5h5m-7 5h7M14 4l7 8-7 8" />,
    region: <><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5" /><rect x="7" y="7" width="10" height="10" rx="1" /></>,
    image: <><rect x="3" y="3" width="18" height="18" rx="3" /><circle cx="8" cy="8" r="1.5" /><path d="m4 18 6-6 4 4 3-3 4 4" /></>,
    video: <><rect x="3" y="5" width="13" height="14" rx="2" /><path d="m16 10 5-3v10l-5-3" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    reset: <path d="M3 11a9 9 0 1 1 3 8M3 4v7h7" />,
    code: <path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-16-2 20" />,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.arrow}</svg>;
}
function readFile(file: File): Promise<string> { return new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result).split(",")[1] || ""); reader.onerror = () => reject(new Error("This file could not be read. Select it again.")); reader.readAsDataURL(file); }); }
function mediaUrl(base64: string) { const raw = atob(base64); const bytes = new Uint8Array(raw.length); for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i); return URL.createObjectURL(new Blob([bytes], { type: "video/mp4" })); }
function saveJSON(value: object, filename: string) { const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: "application/json" })); const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
function clock(seconds: number) { return `${Math.floor(seconds / 60)}:${Math.floor(seconds % 60).toString().padStart(2, "0")}`; }

export default function Home() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [connectionError, setConnectionError] = useState("");
  const [connectionAttempt, setConnectionAttempt] = useState(0);
  const [mode, setMode] = useState<Mode>("object-swap");
  const [video, setVideo] = useState<File | null>(null);
  const [reference, setReference] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [referenceUrl, setReferenceUrl] = useState("");
  const [videoInfo, setVideoInfo] = useState({ width: 16, height: 9, duration: 0 });
  const [prompt, setPrompt] = useState("");
  const [seed, setSeed] = useState(42);
  const [frames, setFrames] = useState<17 | 33>(17);
  const [box, setBox] = useState<Box>(START);
  const [endBox, setEndBox] = useState<Box>(START);
  const [moving, setMoving] = useState(false);
  const [keyframe, setKeyframe] = useState<"start" | "end">("start");
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState("");
  const [jobId, setJobId] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [urls, setUrls] = useState<{ source: string; generated: string; composite: string } | null>(null);
  const [view, setView] = useState<"composite" | "generated">("composite");
  const [playing, setPlaying] = useState(false);
  const [playhead, setPlayhead] = useState(0);
  const [duration, setDuration] = useState(0);
  const beforeRef = useRef<HTMLVideoElement>(null);
  const afterRef = useRef<HTMLVideoElement>(null);
  const editorRef = useRef<HTMLVideoElement>(null);
  const submitLock = useRef(false);
  const anchor = useRef<{ x: number; y: number } | null>(null);
  const busy = ["submitting", "queued", "running"].includes(phase);
  const activeBox = keyframe === "end" && moving ? endBox : box;
  const available = !!connection?.configured && (mode === "object-swap" ? connection.features.objectSwap : connection.features.motionTransfer);
  useEffect(() => { const duration = beforeRef.current?.duration; if (duration && Number.isFinite(duration)) setDuration(duration); }, [urls,mode]);
  useEffect(() => {
    try {
      const pending = JSON.parse(sessionStorage.getItem("montfortmini-pending-job") || "null") as { id?: string; mode?: Mode } | null;
      if (pending?.id && pending.id.length < 200 && (pending.mode === "object-swap" || pending.mode === "motion-transfer")) {
        submitLock.current = true; setMode(pending.mode); setPhase("queued"); setJobId(pending.id);
      }
    } catch { /* Storage may be disabled; the live page still works. */ }
  }, []);

  useEffect(() => {
    const abort = new AbortController(); setConnectionError("");
    fetch("/api/status", { signal: abort.signal }).then(async response => {
      if (!response.ok) throw new Error("The connection could not be checked.");
      const value = await response.json() as Connection;
      if (typeof value.configured !== "boolean" || !value.features || !value.limits) throw new Error("The connection returned an unexpected response.");
      setConnection(value); if (value.limits.maxFrames < 33) setFrames(17);
    }).catch(e => { if (e.name !== "AbortError") setConnectionError(e.message); });
    return () => abort.abort();
  }, [connectionAttempt]);
  useEffect(() => { if (!video) { setVideoUrl(""); return; } const url = URL.createObjectURL(video); setVideoUrl(url); return () => URL.revokeObjectURL(url); }, [video]);
  useEffect(() => { if (!reference) { setReferenceUrl(""); return; } const url = URL.createObjectURL(reference); setReferenceUrl(url); return () => URL.revokeObjectURL(url); }, [reference]);
  useEffect(() => {
    if (!result) return;
    const next = { source: "", generated: "", composite: "" };
    try { next.source = mediaUrl(result.source_video_b64); next.generated = mediaUrl(result.generated_video_b64); next.composite = mediaUrl(result.composite_video_b64 || result.generated_video_b64); setUrls(next); setPlaying(false); setPlayhead(0); }
    catch { setError("The result arrived, but its preview could not be opened."); }
    return () => Object.values(next).forEach(url => { if (url) URL.revokeObjectURL(url); });
  }, [result]);
  useEffect(() => {
    if (!jobId) return;
    const abort = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const response = await fetch(`/api/jobs?id=${encodeURIComponent(jobId)}`, { signal: abort.signal });
        const value = await response.json() as JobResponse;
        if (!response.ok) throw new Error(value.error || "The generation could not be checked.");
        if (value.status === "failed") { try { sessionStorage.removeItem("montfortmini-pending-job"); } catch {} setError(value.error || "Generation did not finish. Adjust the clip and try again."); setPhase("failed"); submitLock.current = false; return; }
        if (value.status === "succeeded") {
          if (!value.result?.generated_video_b64 || !value.result?.source_video_b64) { setError("Generation finished without a playable result."); setPhase("failed"); submitLock.current = false; return; }
          try { sessionStorage.removeItem("montfortmini-pending-job"); } catch {}
          setResult(value.result); setPhase("succeeded"); setError(""); submitLock.current = false; return;
        }
        if (value.status !== "queued" && value.status !== "running") throw new Error("The generation returned an unexpected status.");
        setPhase(value.status);
      } catch (e) {
        if (abort.signal.aborted) return;
        setError(`${e instanceof Error ? e.message : "Connection interrupted."} Still checking your existing job; no new generation has been submitted.`);
      }
      timer = setTimeout(poll, 4000);
    }
    poll(); return () => { abort.abort(); clearTimeout(timer); };
  }, [jobId]);
  useEffect(() => { const el = editorRef.current; if (el && videoUrl && Number.isFinite(el.duration)) el.currentTime = keyframe === "end" && moving ? Math.max(0, Math.min(el.duration - 0.05, (frames - 1) / 8)) : 0; }, [keyframe, moving, frames, videoUrl]);

  function chooseFile(event: ChangeEvent<HTMLInputElement>, kind: "video" | "reference") {
    const file = event.target.files?.[0]; event.target.value = ""; if (!file) return;
    const max = kind === "video" ? Math.min(connection?.limits.maxVideoBytes || 20971520, 20971520) : Math.min(connection?.limits.maxImageBytes || 10485760, 10485760);
    if (file.size > max) { setError(`Choose ${kind === "video" ? "a video" : "an image"} under ${Math.round(max / 1048576)} MB.`); return; }
    const valid = kind === "video" ? /\.(mp4|mov|webm)$/i.test(file.name) || file.type.startsWith("video/") : /\.(png|jpe?g|webp)$/i.test(file.name);
    if (!valid) { setError(kind === "video" ? "Choose an MP4, MOV, or WebM clip." : "Choose a PNG, JPG, or WebP image."); return; }
    setError(""); if (kind === "video") { setVideo(file); setBox(START); setEndBox(START); setKeyframe("start"); } else setReference(file);
  }
  function updateBox(index: number, value: number) { const next = [...activeBox] as Box; next[index] = value; next[0] = Math.min(next[0], 1 - next[2]); next[1] = Math.min(next[1], 1 - next[3]); if (keyframe === "end" && moving) setEndBox(next); else setBox(next); }
  function point(event: PointerEvent<HTMLDivElement>) { const r = event.currentTarget.getBoundingClientRect(); return { x: Math.max(0, Math.min(1, (event.clientX - r.left) / r.width)), y: Math.max(0, Math.min(1, (event.clientY - r.top) / r.height)) }; }
  function draw(event: PointerEvent<HTMLDivElement>) { if (!anchor.current) return; const end = point(event); const start = anchor.current; const next: Box = [Math.min(.97, start.x, end.x), Math.min(.97, start.y, end.y), Math.max(.03, Math.abs(end.x - start.x)), Math.max(.03, Math.abs(end.y - start.y))]; next[2] = Math.min(next[2], 1 - next[0]); next[3] = Math.min(next[3], 1 - next[1]); if (keyframe === "end" && moving) setEndBox(next); else setBox(next); }
  async function generate() {
    if (submitLock.current || busy) return;
    if (!video || !reference) { setError("Add a source clip and a reference image to begin."); return; }
    if (!available) { setError(connection?.message || "Connect a GPU before generating."); return; }
    submitLock.current = true; setPhase("submitting"); setError(""); setJobId("");
    try {
      const [video_b64, reference_b64] = await Promise.all([readFile(video), readFile(reference)]);
      const response = await fetch("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mode, video_b64, reference_b64, prompt: prompt.trim(), seed, frames, bbox: box, end_bbox: moving ? endBox : box }) });
      const value = await response.json() as JobResponse; if (!response.ok || !value.id) throw new Error(value.error || "Generation could not be started.");
      try { sessionStorage.setItem("montfortmini-pending-job",JSON.stringify({id:value.id,mode})); } catch {}
      setPhase("queued"); setJobId(value.id);
    } catch (e) { setError(e instanceof Error ? e.message : "Generation could not be started."); setPhase("failed"); submitLock.current = false; }
  }
  async function togglePlayback() {
    const before = beforeRef.current; const after = afterRef.current; if (!before || !after) return;
    if (Number.isFinite(before.duration)) setDuration(before.duration);
    if (playing) { before.pause(); after.pause(); setPlaying(false); return; }
    if (before.ended || before.currentTime >= duration - .03) before.currentTime = 0;
    after.currentTime = before.currentTime;
    try { await Promise.all([before.play(), after.play()]); setPlaying(true); } catch { before.pause(); after.pause(); setPlaying(false); setError("Wait for both previews to load, then try playback again."); }
  }
  function seek(value: number) { if (beforeRef.current && afterRef.current) { beforeRef.current.currentTime = value; afterRef.current.currentTime = value; setPlayhead(value); } }
  function synchronize() { const before = beforeRef.current; const after = afterRef.current; if (before && after) { setPlayhead(before.currentTime); if (Math.abs(before.currentTime - after.currentTime) > .15) after.currentTime = before.currentTime; } }
  function stopPlayback() { beforeRef.current?.pause(); afterRef.current?.pause(); setPlaying(false); }
  const phaseText = { idle: "Ready when you are", submitting: "Preparing your inputs", queued: "Your generation is queued", running: "Creating your new take", succeeded: "Your new take is ready", failed: "Generation needs attention" }[phase];

  return <main className="studio-shell">
    <header className="app-header"><a className="brand" href="#workspace" aria-label="montfortmini workspace"><span className="brand-symbol"><i /><i /><i /></span><span>montfort<span className="brand-light">mini</span><sup>β</sup></span></a><div className="header-note"><span>✦</span> YOUR SHOT. YOUR RULES.</div><div className="open-badge"><Icon name="code" size={14} /> Open by design</div></header>
    <div className="workspace" id="workspace">
      <div className="workspace-heading"><div><p className="eyebrow">THE OPEN CREATIVE WORKBENCH</p><h1>A new take on the same moment<span>.</span></h1><p className="intro">Transform a subject. Transfer a performance. Make it yours.</p></div><div className={`connection-pill ${connection?.configured ? "connected" : ""}`}><span />{connection?.configured ? "GPU connected" : connectionError ? "Connection unavailable" : connection ? "GPU not connected" : "Checking connection"}</div></div>
      <div className="mode-tabs" role="tablist" aria-label="Creation mode"><button role="tab" aria-selected={mode === "object-swap"} disabled={busy} className={mode === "object-swap" ? "active" : ""} onClick={() => setMode("object-swap")}><Icon name="swap" /> Object swap <span>01</span></button><button role="tab" aria-selected={mode === "motion-transfer"} disabled={busy} className={mode === "motion-transfer" ? "active" : ""} onClick={() => setMode("motion-transfer")}><Icon name="motion" /> Motion transfer <span>02</span></button><p>SMALL CLIPS. BIG POSSIBILITIES.</p></div>
      <div className="workbench">
        <aside className="input-panel" aria-label="Generation inputs"><div className="panel-title"><span className="section-index">01</span><h2>Build your take</h2><span className="panel-kicker">INPUTS</span></div><fieldset disabled={busy} className="inputs-fieldset">
          <div className="input-block"><div className="label-row"><label htmlFor="source-video">Source clip</label><span>UP TO {Math.round(Math.min(connection?.limits.maxVideoBytes || 20971520, 20971520) / 1048576)} MB</span></div><label className={`file-drop ${video ? "has-file" : ""}`} htmlFor="source-video"><span className="file-icon"><Icon name={video ? "check" : "video"} size={22} /></span><span className="file-label"><strong>{video?.name || "Choose your original"}</strong><small>{video ? `${(video.size / 1048576).toFixed(1)} MB · Click to replace` : "MP4, MOV, or WebM"}</small></span><Icon name="upload" size={17} /><input id="source-video" type="file" accept="video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm" onChange={e => chooseFile(e, "video")} /></label></div>
          <div className="input-block"><div className="label-row"><label htmlFor="reference-image">{mode === "object-swap" ? "Replacement reference" : "Character reference"}</label><span>UP TO {Math.round(Math.min(connection?.limits.maxImageBytes || 10485760, 10485760) / 1048576)} MB</span></div><label className={`reference-drop ${reference ? "has-file" : ""}`} htmlFor="reference-image">{referenceUrl ? <img src={referenceUrl} alt="Your selected reference" /> : <div className="reference-illustration"><span /><Icon name="image" size={27} /></div>}<span className="reference-name"><strong>{reference?.name || "Bring a new subject"}</strong><small>{reference ? "Click to change reference" : "PNG, JPG, or WebP"}</small></span><span className="add-file">+</span><input id="reference-image" type="file" accept="image/png,image/jpeg,image/webp" onChange={e => chooseFile(e, "reference")} /></label></div>
          <div className="input-block prompt-block"><div className="label-row"><label htmlFor="prompt">Describe the result</label><span>OPTIONAL</span></div><textarea id="prompt" rows={3} maxLength={1500} placeholder={mode === "object-swap" ? "A glossy blue sphere, resting naturally in the scene…" : "The reference character performs the movement from the clip…"} value={prompt} onChange={e => setPrompt(e.target.value)} /><p className="field-hint">Describe what you want to see in the finished shot.</p></div>
          <div className="settings-grid"><div><label htmlFor="frames">Clip length</label><select id="frames" value={frames} onChange={e => setFrames(Number(e.target.value) as 17 | 33)}><option value={17}>2.1 seconds · quick take</option><option value={33} disabled={(connection?.limits.maxFrames || 33) < 33}>4.1 seconds · longer take</option></select></div><div><label htmlFor="seed">Seed</label><div className="seed-input"><input id="seed" type="number" min={0} max={2147483647} value={seed} onChange={e => setSeed(Math.max(0, Math.min(2147483647, Math.floor(Number(e.target.value) || 0))))} /><button type="button" title="Choose a random seed" aria-label="Choose a random seed" onClick={() => setSeed(Math.floor(Math.random() * 2147483647))}><Icon name="reset" size={14} /></button></div></div></div><p className="preview-limits">Preview mode <span /> First {frames} frames · up to {connection?.limits.maxSide || 480}px</p>
        </fieldset><div className="generation-controls"><button className="generate-button" disabled={busy || !available || !video || !reference} onClick={generate}>{busy ? <span className="spinner" /> : <span className="button-spark">✦</span>}<span>{busy ? "Creating your take…" : "Generate new take"}</span>{!busy && <Icon name="arrow" size={18} />}</button><p className="cost-note">{connection?.configured ? "Uses your connected GPU credits. Experimental results may vary." : connectionError || connection?.message || "Connect a GPU to generate your own result."}</p>{connectionError && <button className="text-button retry-button" onClick={() => setConnectionAttempt(value => value + 1)}>Check connection again <Icon name="reset" size={12} /></button>}{connection?.configured && !available && <p className="availability-note">{mode === "motion-transfer" ? "Motion transfer" : "Object swap"} is not available on this connection yet.</p>}</div></aside>
        <div className="stage-workspace">
          {error && <div role="alert" className="error-message"><span>!</span><p>{error}</p><button onClick={() => setError("")} aria-label="Dismiss error">×</button></div>}
          <section className="comparison-panel" aria-label="Before and after comparison"><div className="viewer-heading"><div className="viewer-title"><span className={`status-dot ${busy ? "working" : ""}`} /><h2>{urls ? "Your new take" : "See the transformation"}</h2></div><span className={`proof-badge ${urls ? "fresh" : ""}`}>{urls ? "YOUR GENERATION" : "RECORDED PROOF"}</span></div><div className="comparison-grid"><div className="video-cell"><div className="video-label"><span>BEFORE</span><small>Original clip</small></div><video ref={beforeRef} src={urls?.source || (mode === "object-swap" ? "/examples/source.mp4" : "/examples/motion-source.mp4")} muted playsInline preload="metadata" onLoadedMetadata={e => setDuration(e.currentTarget.duration || 0)} onTimeUpdate={synchronize} onEnded={stopPlayback} /><div className="cell-corner">01 / SOURCE</div></div><div className="video-cell after-cell"><div className="video-label"><span>AFTER</span><small>{urls && view === "composite" ? "Finished take" : "Generated result"}</small></div><video ref={afterRef} src={urls ? urls[view] : (mode === "object-swap" ? "/examples/generated.mp4" : "/examples/motion-generated.mp4")} muted playsInline preload="metadata" onEnded={stopPlayback} /><div className="cell-corner">02 / REIMAGINED</div></div><span className="comparison-divider"><Icon name="swap" size={15} /></span></div><div className="transport"><button className="play-button" onClick={togglePlayback} aria-label={playing ? "Pause both videos" : "Play both videos"}><Icon name={playing ? "pause" : "play"} size={16} /></button><span className="timecode">{clock(playhead)}</span><input className="timeline" type="range" aria-label="Scrub both videos" min={0} max={duration || 1} step={.01} value={Math.min(playhead, duration || 1)} onChange={e => seek(Number(e.target.value))} /><span className="timecode">{clock(duration)}</span><span className="sync-label"><span /> LINKED PLAYBACK</span></div><div className="viewer-caption"><p>{urls ? "Created from your inputs. Compare, download, and keep experimenting." : "An actual recorded open-model edit. Your own result will appear here."}</p>{urls ? <div className="result-actions"><button className={view === "composite" ? "selected" : ""} onClick={() => { stopPlayback(); setView("composite"); }}>Finished</button><button className={view === "generated" ? "selected" : ""} onClick={() => { stopPlayback(); setView("generated"); }}>Raw result</button></div> : <span className="sample-note">Example, not a live generation</span>}</div></section>
          <section className="region-panel" aria-label={mode === "object-swap" ? "Replacement region" : "Motion reference"}><div className="region-heading"><div><span className="section-index">02</span><h2>{mode === "object-swap" ? "Choose what changes" : "A performance, reimagined"}</h2></div>{mode === "object-swap" && <span className="region-tag"><Icon name="region" size={13} /> REGION EDITOR</span>}</div>{mode === "object-swap" ? <div className="region-content"><div><div className={`region-stage ${videoUrl ? "has-video" : ""}`} style={{ aspectRatio: `${videoInfo.width} / ${videoInfo.height}` }} onPointerDown={e => { if (!videoUrl || busy) return; e.currentTarget.setPointerCapture(e.pointerId); anchor.current = point(e); }} onPointerMove={draw} onPointerUp={() => { anchor.current = null; }} onPointerCancel={() => { anchor.current = null; }} aria-label="Draw a replacement rectangle on your clip">{videoUrl ? <><video ref={editorRef} src={videoUrl} muted playsInline preload="auto" onLoadedMetadata={e => { const el = e.currentTarget; setVideoInfo({ width: el.videoWidth || 16, height: el.videoHeight || 9, duration: el.duration }); el.currentTime = 0; }} /><div className="selection-box" style={{ left: `${activeBox[0] * 100}%`, top: `${activeBox[1] * 100}%`, width: `${activeBox[2] * 100}%`, height: `${activeBox[3] * 100}%` }}><i /><i /><i /><i /><span>{keyframe === "end" && moving ? "END REGION" : "EDIT REGION"}</span></div></> : <div className="region-empty"><Icon name="region" size={30} /><strong>Your clip goes here</strong><span>Upload a clip, then draw the area to replace.</span></div>}</div><p className="region-instruction">{videoUrl ? `${videoInfo.width} × ${videoInfo.height} · ${videoInfo.duration.toFixed(1)}s · Drag to draw a region` : "The region preview uses your source clip."}</p></div><fieldset disabled={busy} className="region-settings"><div className="keyframe-tabs"><button className={keyframe === "start" ? "active" : ""} onClick={() => setKeyframe("start")}>Start position</button><button disabled={!moving} className={keyframe === "end" ? "active" : ""} onClick={() => setKeyframe("end")}>End position</button></div><div className="box-sliders">{["Left", "Top", "Width", "Height"].map((label, index) => <label key={label}><span>{label}<output>{Math.round(activeBox[index] * 100)}%</output></span><input type="range" min={index < 2 ? 0 : .03} max={index === 0 ? 1 - activeBox[2] : index === 1 ? 1 - activeBox[3] : index === 2 ? 1 - activeBox[0] : 1 - activeBox[1]} step={.01} value={activeBox[index]} onChange={e => updateBox(index, Number(e.target.value))} /></label>)}</div><label className="tracking-toggle"><input type="checkbox" checked={moving} onChange={e => { setMoving(e.target.checked); if (e.target.checked) setEndBox([...box] as Box); else setKeyframe("start"); }} /><span className="toggle-track" /><span>Move the region through the clip</span></label><p className="tracking-note">Follows a straight path between two positions. Linear keyframes, not AI tracking.</p></fieldset></div> : <div className="motion-explainer"><span className="motion-glyph"><Icon name="motion" size={38} /></span><div><h3>One clip. A new performer.</h3><p>Add the movement you want to borrow and an image of the character you want to animate.</p><small>{connection?.features.motionTransfer ? "Use a clear, single-subject performance for your first take." : "Motion transfer is in development. Prepare your inputs; generation becomes available when connected."}</small></div></div>}</section>
          <div className="bottom-strip"><div aria-live="polite" className={`job-status ${busy ? "busy" : ""}`}>{busy ? <span className="spinner" /> : <span className="status-orbit" />}<div><strong>{phaseText}</strong><p>{busy ? "Keep this page open. The preview updates when the take is complete." : urls ? "Your files are ready to save." : "Start with a short clip and a clear reference."}</p></div></div>{urls && result && <div className="download-actions"><a href={urls.composite} download="montfortmini-take.mp4"><Icon name="download" size={15} /> MP4</a><button onClick={() => saveJSON(result.workflow, "montfortmini-workflow.json")}><Icon name="code" size={15} /> Workflow</button><button className="manifest-download" onClick={() => saveJSON(result.manifest, "montfortmini-run.json")}>Run details</button></div>}</div>
        </div>
      </div><footer className="app-footer"><span><span className="footer-mark">✦</span> Open tools. Independent possibilities.</span><span>Open-source repository forthcoming <span className="footer-dot">·</span> Early preview</span></footer>
    </div>
  </main>;
}

