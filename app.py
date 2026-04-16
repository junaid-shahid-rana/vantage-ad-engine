import streamlit as st
import os
import json
import time
import tempfile
import re
import requests
import textwrap
from pathlib import Path

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vantage Ad Engine | Vibe Studio",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Dark-Mode CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0a0a0f !important;
    color: #e0e0e0;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background-color: #0d0d14 !important; }

/* Main container */
.main .block-container {
    max-width: 780px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Title gradient */
.vantage-title {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00c6ff, #0072ff, #7b2ff7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin-bottom: 0.1rem;
}
.vantage-sub {
    color: #555a6e;
    font-size: 0.95rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Input */
.stTextInput > div > div > input {
    background-color: #13131f !important;
    border: 1px solid #1e2040 !important;
    border-radius: 10px !important;
    color: #e0e0e0 !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0072ff !important;
    box-shadow: 0 0 0 2px rgba(0,114,255,0.25) !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #0072ff, #7b2ff7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

/* Progress card */
.progress-card {
    background: #13131f;
    border: 1px solid #1e2040;
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    margin: 1.2rem 0;
}
.stage-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0;
    font-size: 0.95rem;
}
.stage-icon { font-size: 1.1rem; width: 24px; text-align: center; }
.stage-done { color: #00e5a0; font-weight: 600; }
.stage-active { color: #00c6ff; font-weight: 700; animation: pulse 1.2s infinite; }
.stage-pending { color: #333550; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* DNA card */
.dna-card {
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    margin: 1rem 0;
}
.dna-label {
    color: #0072ff;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
    font-weight: 700;
}
.dna-value { color: #c8d0e8; font-size: 0.95rem; margin-bottom: 0.8rem; }

/* Script box */
.script-box {
    background: #0a0a10;
    border-left: 3px solid #0072ff;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.4rem;
    font-style: italic;
    color: #d0d8f0;
    font-size: 1rem;
    line-height: 1.7;
    margin: 0.8rem 0;
}

/* Keyword chips */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.5rem; }
.chip {
    background: #1a1a2e;
    border: 1px solid #0072ff44;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #80aaff;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* Video container */
.video-wrapper {
    background: #0d0d14;
    border: 1px solid #1e2040;
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    margin-top: 1rem;
}

/* Download button override */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #00e5a0, #0072ff) !important;
    color: #000 !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    width: 100%;
    font-size: 1rem !important;
    padding: 0.75rem !important;
}

/* Divider */
hr { border-color: #1a1a2e !important; margin: 1.5rem 0 !important; }

/* Metric row */
.metric-row {
    display: flex; gap: 16px; margin: 1rem 0;
}
.metric-box {
    flex: 1;
    background: #0e0e1a;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-val { font-size: 1.4rem; font-weight: 800; color: #0072ff; }
.metric-lbl { font-size: 0.7rem; color: #555a6e; letter-spacing: 1px; text-transform: uppercase; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="vantage-title">⚡ Vantage Ad Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="vantage-sub">Vibe Studio &nbsp;·&nbsp; URL-to-Video Pipeline</div>', unsafe_allow_html=True)

st.markdown("""
<div class="metric-row">
  <div class="metric-box"><div class="metric-val">15s</div><div class="metric-lbl">Cinematic Ad</div></div>
  <div class="metric-box"><div class="metric-val">9:16</div><div class="metric-lbl">Vertical Format</div></div>
  <div class="metric-box"><div class="metric-val">1080p</div><div class="metric-lbl">Resolution</div></div>
  <div class="metric-box"><div class="metric-val">AI</div><div class="metric-lbl">Powered</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Input ─────────────────────────────────────────────────────────────────────
url_input = st.text_input(
    "🌐  Target Website URL",
    placeholder="https://example.com",
    label_visibility="visible",
)

run_btn = st.button("🚀  Generate Ad", use_container_width=True)

# ─── Helper Functions ───────────────────────────────────────────────────────────

def analyze_url_with_gemini(url: str) -> dict:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""You are an expert ad copywriter and brand strategist. Analyze this website URL and return ONLY valid JSON (no markdown, no code fences).

URL: {url}

Return exactly this JSON structure:
{{
  "brand_dna": {{
    "tone": "2-4 word tone descriptor",
    "industry": "industry name",
    "value_proposition": "one punchy sentence"
  }},
  "script": "A high-converting 15-second voiceover script. Max 45 words. Present tense. Powerful opening. Strong CTA.",
  "keywords": [
    "cinematic vertical stock footage keyword 1",
    "cinematic vertical stock footage keyword 2",
    "cinematic vertical stock footage keyword 3"
  ]
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def generate_voice(script: str, output_path: str) -> str:
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    voice_names = ["Brian", "Marcus", "Charlie", "Daniel", "George"]
    voice_id = None

    try:
        voices_resp = client.voices.get_all()
        available = {v.name: v.voice_id for v in voices_resp.voices}
        for name in voice_names:
            if name in available:
                voice_id = available[name]
                break
        if not voice_id and available:
            voice_id = list(available.values())[0]
    except Exception:
        voice_id = "onwK4e9ZLuTAKqWW03F9"  # fallback: Daniel

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=script,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    with open(output_path, "wb") as f:
        for chunk in audio:
            if isinstance(chunk, bytes):
                f.write(chunk)
    return output_path


def fetch_pexels_videos(keywords: list, output_dir: str) -> list:
    api_key = os.environ["PEXELS_API_KEY"]
    headers = {"Authorization": api_key}
    downloaded = []

    for i, keyword in enumerate(keywords[:3]):
        try:
            resp = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params={"query": keyword, "orientation": "portrait", "per_page": 5, "size": "medium"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            videos = data.get("videos", [])
            if not videos:
                resp2 = requests.get(
                    "https://api.pexels.com/videos/search",
                    headers=headers,
                    params={"query": keyword.split()[0], "orientation": "portrait", "per_page": 5},
                    timeout=15,
                )
                videos = resp2.json().get("videos", [])

            for vid in videos:
                files = vid.get("video_files", [])
                # prefer HD portrait files
                portrait_files = [f for f in files if f.get("width", 0) < f.get("height", 1)]
                if not portrait_files:
                    portrait_files = files
                portrait_files.sort(key=lambda f: f.get("width", 0) * f.get("height", 0), reverse=True)
                if portrait_files:
                    dl_url = portrait_files[0]["link"]
                    out_path = os.path.join(output_dir, f"clip_{i}.mp4")
                    r = requests.get(dl_url, stream=True, timeout=60)
                    r.raise_for_status()
                    with open(out_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=65536):
                            f.write(chunk)
                    downloaded.append(out_path)
                    break
        except Exception as e:
            st.warning(f"⚠️ Clip {i+1} fetch issue: {e}")
            continue

    return downloaded


def render_video(clips_paths: list, audio_path: str, script: str, output_path: str) -> str:
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, TextClip, ColorClip
    )

    W, H = 1080, 1920
    CLIP_DURATION = 5
    processed = []

    for path in clips_paths:
        try:
            clip = VideoFileClip(path)
            # Crop/resize to fill 9:16
            clip_ratio = clip.w / clip.h
            target_ratio = W / H
            if clip_ratio > target_ratio:
                new_w = int(clip.h * target_ratio)
                x_center = clip.w // 2
                clip = clip.cropped(x1=x_center - new_w // 2, x2=x_center + new_w // 2)
            else:
                new_h = int(clip.w / target_ratio)
                y_center = clip.h // 2
                clip = clip.cropped(y1=y_center - new_h // 2, y2=y_center + new_h // 2)

            clip = clip.resized((W, H))
            if clip.duration > CLIP_DURATION:
                clip = clip.subclipped(0, CLIP_DURATION)
            elif clip.duration < CLIP_DURATION:
                loops = int(CLIP_DURATION / clip.duration) + 1
                clip = concatenate_videoclips([clip] * loops).subclipped(0, CLIP_DURATION)
            processed.append(clip)
        except Exception as e:
            st.warning(f"⚠️ Could not process clip {path}: {e}")

    if not processed:
        # fallback: black clip
        processed = [ColorClip(size=(W, H), color=(10, 10, 15), duration=CLIP_DURATION)]

    # Pad to 3 clips
    while len(processed) < 3:
        processed.append(processed[-1].copy())

    final_clip = concatenate_videoclips(processed[:3], method="compose")

    # Captions
    words = script.split()
    chunk_size = max(1, len(words) // 3)
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    text_clips = []
    seg_duration = 5.0
    for idx, chunk in enumerate(chunks[:3]):
        wrapped = textwrap.fill(chunk, width=22)
        try:
            txt = TextClip(
                text=wrapped,
                font_size=68,
                color="white",
                font="DejaVu-Sans-Bold",
                stroke_color="black",
                stroke_width=3,
                method="caption",
                size=(W - 120, None),
            ).with_position("center").with_start(idx * seg_duration).with_duration(seg_duration)
            text_clips.append(txt)
        except Exception:
            try:
                txt = TextClip(
                    text=wrapped,
                    font_size=64,
                    color="white",
                    stroke_color="black",
                    stroke_width=3,
                    method="label",
                ).with_position("center").with_start(idx * seg_duration).with_duration(seg_duration)
                text_clips.append(txt)
            except Exception as e:
                st.warning(f"Caption render issue: {e}")

    if text_clips:
        final_clip = CompositeVideoClip([final_clip] + text_clips)

    # Audio
    try:
        audio = AudioFileClip(audio_path)
        if audio.duration > final_clip.duration:
            audio = audio.subclipped(0, final_clip.duration)
        final_clip = final_clip.with_audio(audio)
    except Exception as e:
        st.warning(f"⚠️ Audio overlay issue: {e}")

    final_clip.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        logger=None,
    )
    return output_path


# ─── Pipeline ──────────────────────────────────────────────────────────────────

STAGES = [
    ("🧬", "Scanning URL DNA..."),
    ("🎙️", "Generating AI Voice..."),
    ("🎬", "Harvesting Cinematic Assets..."),
    ("🎞️", "Rendering Final MP4..."),
]

def render_progress(current: int, statuses: list):
    rows = ""
    for i, (icon, label) in enumerate(STAGES):
        if i < current:
            css = "stage-done"
            marker = "✓"
        elif i == current:
            css = "stage-active"
            marker = "◉"
        else:
            css = "stage-pending"
            marker = "○"
        rows += f'<div class="stage-row"><span class="stage-icon">{icon}</span><span class="{css}">{marker} {label}</span>'
        if statuses[i]:
            rows += f'<span style="color:#666;font-size:0.8rem;margin-left:auto">{statuses[i]}</span>'
        rows += "</div>"
    st.markdown(f'<div class="progress-card">{rows}</div>', unsafe_allow_html=True)


if run_btn:
    if not url_input.strip():
        st.error("Please enter a valid URL.")
        st.stop()

    url = url_input.strip()
    statuses = ["", "", "", ""]
    progress_placeholder = st.empty()

    # ── Stage 0: Gemini analysis ──────────────────────────────────────────────
    with progress_placeholder.container():
        render_progress(0, statuses)

    t0 = time.time()
    try:
        data = analyze_url_with_gemini(url)
    except Exception as e:
        st.error(f"Gemini analysis failed: {e}")
        st.stop()

    statuses[0] = f"{time.time()-t0:.1f}s"
    brand_dna = data["brand_dna"]
    script = data["script"]
    keywords = data["keywords"]

    with progress_placeholder.container():
        render_progress(1, statuses)

    # Show DNA card
    chips = "".join(f'<span class="chip">🔍 {k}</span>' for k in keywords)
    st.markdown(f"""
<div class="dna-card">
  <div class="dna-label">Brand DNA</div>
  <div class="dna-value">
    <b style="color:#80aaff">Tone:</b> {brand_dna.get('tone','')} &nbsp;·&nbsp;
    <b style="color:#80aaff">Industry:</b> {brand_dna.get('industry','')} &nbsp;·&nbsp;
    <b style="color:#80aaff">Value:</b> {brand_dna.get('value_proposition','')}
  </div>
  <div class="dna-label">Ad Script</div>
  <div class="script-box">{script}</div>
  <div class="dna-label" style="margin-top:0.8rem">Footage Keywords</div>
  <div class="chip-row">{chips}</div>
</div>
""", unsafe_allow_html=True)

    # ── Stage 1: ElevenLabs voice ─────────────────────────────────────────────
    tmpdir = tempfile.mkdtemp()
    audio_path = os.path.join(tmpdir, "voice.mp3")

    t1 = time.time()
    try:
        generate_voice(script, audio_path)
    except Exception as e:
        st.error(f"Voice generation failed: {e}")
        st.stop()

    statuses[1] = f"{time.time()-t1:.1f}s"
    with progress_placeholder.container():
        render_progress(2, statuses)

    st.markdown("**🎙️ Voice Preview**")
    with open(audio_path, "rb") as af:
        st.audio(af.read(), format="audio/mp3")

    # ── Stage 2: Pexels footage ───────────────────────────────────────────────
    t2 = time.time()
    clips_dir = os.path.join(tmpdir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    clips = fetch_pexels_videos(keywords, clips_dir)

    statuses[2] = f"{len(clips)} clips · {time.time()-t2:.1f}s"
    with progress_placeholder.container():
        render_progress(3, statuses)

    # ── Stage 3: MoviePy render ───────────────────────────────────────────────
    output_path = os.path.join(tmpdir, "vantage_ad.mp4")
    t3 = time.time()
    try:
        render_video(clips, audio_path, script, output_path)
    except Exception as e:
        st.error(f"Render failed: {e}")
        st.stop()

    statuses[3] = f"{time.time()-t3:.1f}s"
    with progress_placeholder.container():
        render_progress(4, statuses)

    # ── Output ────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🎬 Your 15-Second Cinematic Ad")
    st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
    with open(output_path, "rb") as vf:
        video_bytes = vf.read()
    st.video(video_bytes, format="video/mp4")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️  Download for Client",
        data=video_bytes,
        file_name="vantage_ad_15s.mp4",
        mime="video/mp4",
        use_container_width=True,
    )

    total = time.time() - t0
    st.markdown(f"""
<div style="text-align:center;margin-top:1.5rem;color:#333550;font-size:0.82rem">
  Pipeline completed in <b style="color:#0072ff">{total:.1f}s</b> &nbsp;·&nbsp;
  1080×1920 · 30fps · H.264 · AAC Audio
</div>
""", unsafe_allow_html=True)
