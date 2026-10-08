# Audio → TXT → ZIP on RunPod

A minimal additional entrypoint for jhj0517/Whisper-WebUI forks. The original
application is untouched. This mode uses faster-whisper directly, without
Torch, torchaudio, diarization, or music separation.

## Build once on GitHub

1. This fork already includes the RunPod app and build workflow.
2. Open https://github.com/Neputin/Whisper-WebUI-runpod.
3. Open the fork's **Actions** tab and enable workflows if GitHub requests it.
4. Run **Build RunPod image**. Wait for a green result.
5. Open your GitHub profile → Packages → the new `whisper-webui-runpod` package
   → Package settings → Change visibility → Public. A public repository does
   not automatically make its container package public. Alternatively configure
   private-registry credentials in RunPod.

For this fork under Neputin, the built image will be:

`ghcr.io/neputin/whisper-webui-runpod:latest`

This is an EXPECTED image name, not an image published by this source package.
For reproducible deployments, use the commit-SHA tag shown by the build instead
of `latest`. The Python entrypoint and batch exporter are tested during build;
an actual GPU transcription is still required to validate the deployed pod.

## Create the RunPod pod after the image is built

- Container image: the image above (only after the build succeeds).
- One CUDA 12-capable NVIDIA GPU; 12+ GB VRAM recommended for the default model.
- HTTP port: **7860**.
- Container start command: **leave blank**. The image already starts the UI.
- Persistent storage: mount at `/workspace` for saved models and results.
- Disk space: allow room for your uploads, the cached model, and outputs. Audio
  uploads remain on disk, so upload in batches that fit the available space.
- Environment variable `WHISPER_PASSWORD`: choose your own password.
- Optional `WHISPER_USERNAME`: defaults to `matt`.

Connect → HTTP service on port 7860. Sign in, select multiple audio files,
click Transcribe, and download the resulting ZIP. It includes one UTF-8 TXT
per successful input. Numeric prefixes prevent filename collisions. Failures
are listed separately in ERRORS.txt, rather than silently omitted.

The first transcription downloads the large-v3 model. Files run sequentially
on the GPU; there is no hour quota imposed by this app. RunPod compute/storage
charges still apply. Keep the page open while processing. Results are saved in
`/workspace/whisper-txt/outputs/<job-id>`; uploaded files and model cache are
also under `/workspace/whisper-txt`. Persistence requires an appropriate RunPod
volume. Export results before removing a pod or its storage.

For a first check, upload one short recording and confirm the downloaded TXT
before sending a large batch. The app does not resume unfinished jobs after
pod restart and is intended for one trusted user.

Optional environment settings:

- `WHISPER_MODEL`: defaults to `large-v3`; choose `small` for a quick smoke test.
- `WHISPER_DEVICE`: defaults to `cuda`; use `cpu` with compute type `int8` for CPU tests.
- `WHISPER_COMPUTE_TYPE`: defaults to `float16`.
- `DATA_DIR`: defaults to `/workspace/whisper-txt`.

## Local tests

`PYTHONPATH=runpod python3 -m unittest discover -s runpod/tests -v`

Tests cover UTF-8 content, duplicate basenames, independent jobs, empty input,
and failures occurring partway through a recording. They use a simulated
transcription model; they do not verify GPU drivers or recognition accuracy.

The Docker image uses the CUDA 12/cuDNN 9 runtime recommended in faster-whisper's
README: https://github.com/SYSTRAN/faster-whisper#gpu
Direct application dependencies are version-pinned. Transitive dependencies
and the base image's digest are not fully locked.

## License

These additional files are supplied under Apache-2.0, matching the upstream
Whisper-WebUI project. Keep the upstream LICENSE and notices in your fork.
