"""Paired reference-role experiment; retain old conditioning pixels and output canvas."""
from contextlib import contextmanager
import hashlib
import io
import json
import re
from pathlib import Path
import zipfile
import pose_reference_alignment as previous
import qwen_reference_alignment as qwen


def relabel(prompt):
    return re.sub(r'(?i)(image )([12])', lambda m: m[1] + ('2' if m[2] == '1' else '1'), prompt)


@contextmanager
def identity_first():
    builder, prompt = qwen.build_graph, previous.PROMPT
    def build(*args, **kwargs):
        graph = builder(*args, **kwargs)
        for key in ('6', '7'):
            inputs = graph[key]['inputs']
            inputs['image1'], inputs['image2'] = inputs['image2'], inputs['image1']
        return graph
    try:
        qwen.build_graph = build
        previous.PROMPT = relabel(prompt)
        yield
    finally:
        qwen.build_graph, previous.PROMPT = builder, prompt


def run_reference_alignment(source, identity, guide):
    with identity_first():
        data = previous.run_reference_alignment(source, identity, guide)
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as new:
        for entry in old.infolist():
            if entry.is_dir():
                continue
            value = old.read(entry)
            if entry.filename == 'manifest.json':
                record = json.loads(value)
                record['candidate'] = 'Identity-first Qwen2511; same prepared guide/identity/canvas as pose-first control'
                record['software_sha256']['identity_first_alignment.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
                record['limitations'].append('Paired change includes reference slot order and semantically equivalent image-number labels in prompt. No claim of a pure slot-only causal effect.')
                value = json.dumps(record, indent=2).encode()
            new.writestr(entry.filename, value)
    return output.getvalue()
