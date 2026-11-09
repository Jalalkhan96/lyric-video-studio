#!/usr/bin/env python3
"""Full sync: Demucs vocals (done separately) + torchaudio MMS_FA forced alignment.
Input : work/demucs/htdemucs/song/vocals.wav (fallback: assets/song.mp3), lyrics.txt
Output: assets/words.json [{line, w, s, e}] and work/timing-table.md
Low-confidence lines are flagged in the table, never silently forced.
"""
import json, os, sys
from pathlib import Path
import torch, torchaudio

# Studio adaptation: project dir via LVS_PROJECT (default: studio root).
# Run with the sync venv (torch/torchaudio/demucs/soundfile) — see docs/INSTALL.md.
ROOT = Path(os.environ.get("LVS_PROJECT", str(Path(__file__).resolve().parent.parent)))
VOC = ROOT / "work" / "demucs" / "htdemucs" / "song" / "vocals.wav"
SRC = VOC if VOC.exists() else ROOT / "assets" / "song.mp3"
LINES = [l.strip() for l in (ROOT / "lyrics.txt").read_text().splitlines() if l.strip()]
WORDS = [l.split() for l in LINES]
FLAT = [w for ws in WORDS for w in ws]
SR = 16000

def main():
    print("source:", SRC)
    import soundfile as sf  # torchaudio 2.11 load() needs torchcodec; soundfile reads wav directly
    data, sr = sf.read(str(SRC), always_2d=True)
    wav = torch.from_numpy(data.T).float().mean(0, keepdim=True)
    if sr != SR:
        wav = torchaudio.functional.resample(wav, sr, SR)
    dur = wav.shape[1] / SR
    print(f"audio {dur:.2f}s mono 16k")

    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model()
    model.eval()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()

    # --- chunked emission (30 s windows, concatenated) ---
    win = 30 * SR
    ems = []
    with torch.inference_mode():
        for i in range(0, wav.shape[1], win):
            seg = wav[:, i:i + win]
            em, _ = model(seg)
            ems.append(em[0])
    emission = torch.cat(ems, dim=0)  # [frames, vocab], 50 fps
    ratio = dur / emission.shape[0]
    print(f"emission frames={emission.shape[0]} ratio={ratio:.5f}s/frame")

    tokens = tokenizer(FLAT)  # list per word -> token id lists
    with torch.inference_mode():
        token_spans = aligner(emission, tokens)
    assert len(token_spans) == len(FLAT), (len(token_spans), len(FLAT))

    out, idx = [], 0
    table = ["| # | line start | line end | conf | lyrics |", "|---|---|---|---|---|"]
    for li, ws in enumerate(WORDS):
        line_words, scores = [], []
        for w in ws:
            spans = token_spans[idx]; idx += 1
            s = spans[0].start * ratio; e = spans[-1].end * ratio
            sc = sum(sp.score for sp in spans) / len(spans)
            scores.append(sc)
            line_words.append({"line": li, "w": w, "s": round(s, 3), "e": round(e, 3)})
        conf = sum(scores) / len(scores)
        out.extend(line_words)
        flag = " ⚠️ LOW" if conf < -1.5 else ""
        table.append(f"| {li+1} | {line_words[0]['s']:.2f} | {line_words[-1]['e']:.2f} | {conf:.2f}{flag} | {' '.join(ws)} |")

    (ROOT / "assets" / "words.json").write_text(json.dumps(out, indent=1))
    (ROOT / "work" / "timing-table.md").write_text("\n".join(table) + "\n")
    print("\n".join(table))
    print(f"\nwrote assets/words.json ({len(out)} words, {len(LINES)} lines)")

if __name__ == "__main__":
    main()
