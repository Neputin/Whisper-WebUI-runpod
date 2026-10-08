"""Batch export, isolated from the UI so output handling can be tested."""
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED
import re


def transcribe_batch(files, model, output_root, language=None, progress=None):
    if not files:
        raise ValueError('Upload at least one audio file.')
    job = Path(output_root) / uuid4().hex
    job.mkdir(parents=True, exist_ok=False)
    outputs, errors = [], []
    for index, source in enumerate(files, 1):
        source = Path(source)
        stem = re.sub(r'[^\w .-]', '_', source.stem).strip(' .')[:120] or 'audio'
        target = job / f'{index:04d}_{stem}.txt'
        if progress:
            progress((index - 1) / len(files), desc=f'{index}/{len(files)}: {source.name}')
        try:
            segments, _ = model.transcribe(str(source), language=language, task='transcribe',
                beam_size=5, vad_filter=True, condition_on_previous_text=False)
            # Write incrementally: a long recording does not accumulate in RAM.
            partial = target.with_suffix('.partial')
            with partial.open('w', encoding='utf-8') as handle:
                for segment in segments:
                    line = segment.text.strip()
                    if line:
                        handle.write(line + '\n')
            partial.replace(target)
            outputs.append(target)
        except Exception as exc:
            target.with_suffix('.partial').unlink(missing_ok=True)
            errors.append(f'{source.name}: {type(exc).__name__}: {exc}')
    if errors:
        (job / 'ERRORS.txt').write_text('\n'.join(errors), encoding='utf-8')
    archive = job / 'transcripts.zip'
    with ZipFile(archive, 'w', ZIP_DEFLATED) as bundle:
        for output in outputs:
            bundle.write(output, output.name)
        if errors:
            bundle.write(job / 'ERRORS.txt', 'ERRORS.txt')
    if progress:
        progress(1, desc='Finished')
    status = f'{len(outputs)}/{len(files)} files transcribed.'
    if errors:
        status += ' Some files failed; see ERRORS.txt in the ZIP.'
    return str(archive), [str(p) for p in outputs], status
