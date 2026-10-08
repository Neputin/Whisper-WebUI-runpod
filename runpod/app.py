"""Simple RunPod entrypoint. Does not import Torch, torchaudio or pyannote."""
import os
from pathlib import Path
from functools import lru_cache
import gradio as gr
from faster_whisper import WhisperModel
from batch import transcribe_batch

ROOT = Path(os.environ.get('DATA_DIR', '/workspace/whisper-txt'))
OUTPUT = ROOT / 'outputs'
for folder in (OUTPUT, ROOT / 'models', ROOT / 'uploads'):
    folder.mkdir(parents=True, exist_ok=True)
os.environ['GRADIO_TEMP_DIR'] = str(ROOT / 'uploads')

@lru_cache(maxsize=1)
def load_model():
    return WhisperModel(os.environ.get('WHISPER_MODEL', 'large-v3'),
        device=os.environ.get('WHISPER_DEVICE', 'cuda'),
        compute_type=os.environ.get('WHISPER_COMPUTE_TYPE', 'float16'),
        download_root=str(ROOT / 'models'))


def run(files, language, progress=gr.Progress()):
    if not files:
        raise gr.Error('Upload at least one audio file first.')
    progress(0, desc='Loading model. First use downloads the model and can take several minutes.')
    return transcribe_batch(files, load_model(), OUTPUT,
        language=language.strip() or None, progress=progress)

with gr.Blocks(title='Audio to TXT') as demo:
    gr.Markdown('# Audio to TXT\nUpload your audio, transcribe it, and download all text files in one ZIP.')
    files = gr.File(label='Upload audio files', file_count='multiple', type='filepath')
    language = gr.Textbox(label='Language (optional)', placeholder='Leave blank for auto-detect, or enter en / pl / de …')
    start = gr.Button('Transcribe', variant='primary')
    status = gr.Textbox(label='Status', interactive=False)
    archive = gr.File(label='Download all TXT files as ZIP', interactive=False)
    individual = gr.File(label='Individual TXT downloads', file_count='multiple', interactive=False)
    gr.Markdown('Keep this page open during processing. Results are also saved on the pod. '
                'Transcription preserves the spoken language. No timestamps or speaker labels.')
    start.click(run, [files, language], [archive, individual, status], concurrency_limit=1)

def main():
    password = os.environ.get('WHISPER_PASSWORD', '')
    if not password:
        raise SystemExit('Set WHISPER_PASSWORD in your RunPod environment variables before starting.')
    demo.queue(default_concurrency_limit=1, api_open=False).launch(
        server_name='0.0.0.0', server_port=7860, share=False,
        auth=(os.environ.get('WHISPER_USERNAME', 'matt'), password),
        allowed_paths=[str(OUTPUT.resolve())], show_error=False)

if __name__ == '__main__':
    main()
