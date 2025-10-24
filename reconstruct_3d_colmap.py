import argparse, os, shutil, subprocess, sys
from pathlib import Path

def check_bin(name_or_path: str) -> str:
    p = Path(name_or_path)
    if p.exists():
        return str(p)
    full = shutil.which(name_or_path)
    if full:
        return full
    sys.exit(f"❌ Eseguibile non trovato: {name_or_path}. Aggiungilo al PATH o usa --colmap_bin/--ffmpeg_bin.")

def run(cmd, cwd=None):
    print("➜", " ".join(map(str, cmd)))
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(f"❌ Comando fallito ({e.returncode}): {' '.join(map(str, cmd))}")

def extract_frames(ffmpeg_bin: str, video: Path, out_dir: Path, fps: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    run([ffmpeg_bin, "-i", str(video), "-vf", f"fps={fps}", "-q:v", "2", str(out_dir / "frame_%06d.jpg")])

def colmap_pipeline(colmap_bin: str, images_dir: Path, workspace: Path,
                    threads: int, gpu_index: int, pm_max_size: int):
    workspace.mkdir(parents=True, exist_ok=True)
    database_path = workspace / "database.db"
    sparse_dir    = workspace / "sparse"
    model_dir     = sparse_dir / "0"
    dense_root    = workspace / "dense"
    dense_dir     = dense_root / "0"
    dense_dir.mkdir(parents=True, exist_ok=True)

    # 1) Feature extraction (SIFT)
    run([
        colmap_bin, "feature_extractor",
        "--database_path", str(database_path),
        "--image_path", str(images_dir),
        "--SiftExtraction.num_threads", str(threads),
        "--SiftExtraction.use_gpu", "1" if gpu_index >= 0 else "0",
    ])

    # 2) Matching (exhaustive)
    run([
        colmap_bin, "exhaustive_matcher",
        "--database_path", str(database_path),
        "--SiftMatching.num_threads", str(threads),
        "--SiftMatching.use_gpu", "1" if gpu_index >= 0 else "0",
    ])

    # 3) Sparse reconstruction (Mapper)
    sparse_dir.mkdir(parents=True, exist_ok=True)
    run([
        colmap_bin, "mapper",
        "--database_path", str(database_path),
        "--image_path", str(images_dir),
        "--output_path", str(sparse_dir),
        "--Mapper.num_threads", str(threads),
    ])

    # 4) Undistort per la fase densa (scrive in .../dense/0)
    run([
        colmap_bin, "image_undistorter",
        "--image_path", str(images_dir),
        "--input_path", str(model_dir),
        "--output_path", str(dense_dir),
        "--output_type", "COLMAP",
    ])

    # 5) PatchMatch Stereo (GPU) – ***ATTENZIONE: workspace_path = .../dense/0***
    run([
        colmap_bin, "patch_match_stereo",
        "--workspace_path", str(dense_dir),
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.gpu_index", str(gpu_index if gpu_index >= 0 else 0),
        "--PatchMatchStereo.max_image_size", str(pm_max_size),
    ])

    # 6) Fusion (nuvola densa) – workspace_path = .../dense/0
    fused_ply = dense_dir / "fused.ply"
    run([
        colmap_bin, "stereo_fusion",
        "--workspace_path", str(dense_dir),
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", str(fused_ply),
    ])

    # 7) Meshing (Delaunay)
    meshed_delaunay = dense_dir / "meshed-delaunay.ply"
    run([
        colmap_bin, "delaunay_mesher",
        "--input_path", str(dense_dir),
        "--output_path", str(meshed_delaunay),
    ])

def main():
    ap = argparse.ArgumentParser("Ricostruzione 3D con COLMAP (SfM+MVS)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--images", type=Path, help="Cartella immagini")
    src.add_argument("--video", type=Path, help="Video da cui estrarre frame")

    ap.add_argument("--output", type=Path, default=Path("reconstruction_workspace"))
    ap.add_argument("--reset", action="store_true", help="⚠️ Cancella la cartella di output prima di iniziare")
    ap.add_argument("--colmap_bin", type=str, default="colmap")
    ap.add_argument("--ffmpeg_bin", type=str, default="ffmpeg")
    ap.add_argument("--fps", type=int, default=3, help="FPS per estrarre frame dal video")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 8, help="Thread CPU per SIFT/Matching/Mapper")
    ap.add_argument("--gpu", type=int, default=0, help="Indice GPU per PatchMatch (0 = prima GPU, -1 = disattiva)")
    ap.add_argument("--pm_max_size", type=int, default=2000, help="Max image size per PatchMatch (qualità/tempo)")

    args = ap.parse_args()

    # Reset pulito se richiesto
    if args.reset and args.output.exists():
        print(f"🗑️  --reset: cancello '{args.output}' ...")
        shutil.rmtree(args.output, ignore_errors=True)

    colmap = check_bin(args.colmap_bin)

    # Sorgente immagini: cartella o video
    if args.images:
        images_dir = args.images.resolve()
        if not images_dir.exists():
            sys.exit(f"❌ Cartella non trovata: {images_dir}")
    else:
        ffmpeg = check_bin(args.ffmpeg_bin)
        if not args.video.exists():
            sys.exit(f"❌ Video non trovato: {args.video}")
        if args.video.is_dir():
            sys.exit("❌ Hai passato una CARTELLA a --video. Usa --images <cartella> oppure un FILE video (es. .mp4).")
        images_dir = (args.output / "frames").resolve()
        print(f"🎞️  Estraggo frame: {args.video} → {images_dir} (fps={args.fps})")
        extract_frames(ffmpeg, args.video.resolve(), images_dir, args.fps)

    print(f"🧱 Avvio pipeline COLMAP su {images_dir}")
    colmap_pipeline(
        colmap_bin=colmap,
        images_dir=images_dir,
        workspace=args.output.resolve(),
        threads=args.threads,
        gpu_index=args.gpu,
        pm_max_size=args.pm_max_size,
    )

    dense_dir = args.output / "dense" / "0"
    print("\n✅ Finito. Risultati principali:")
    for p in [dense_dir / "fused.ply", dense_dir / "meshed-delaunay.ply"]:
        print("  •", p if p.exists() else f"(non trovato) {p}")

if __name__ == "__main__":
    main()
