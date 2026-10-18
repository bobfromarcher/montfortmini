# Setup verification — October18,2026

A fresh local Git clone of commit `e7d7444e9de8e31420e4643cd831cfd0424e1c3c` used a new
Python3.14 virtual environment. This is the same operator and computer, not
independent reproduction. Only evaluation dependencies were installed from the
pinned requirements file. No GPU generation was repeated.

Commands executed from the clean clone:

```sh
python -m venv .venv
# Activate the new environment, then:
python -m pip install -r evaluation/requirements.txt
python -m unittest discover -s tests
python -m unittest test_reference_alignment
python evaluation/audit_cascade.py --run evaluation/recovery/synthetic-regression --output audit.json
python evaluation/prepare_confirmation.py --output /path/to/new-reconstruction
```

Results:10 existing production tests and2 reference-geometry tests passed.
The bundled17-frame synthetic result passed technical decode/frame/size/rate
checks. Every one of the11 frozen runtime Python source hashes matched in the
fresh clone. Python files preserve their recorded line endings through Git to
keep those byte hashes meaningful. Original/new-input SHA256 values matched;
the historical input MP4 was reproduced byte for byte using FFmpeg9.0.2.

This validates CPU setup/analysis and input reconstruction, not perceptual
quality or bit-identical GPU inference on another machine. Modal's CPU preflight
and both full-cascade GPU calls separately passed imports/model presence and
returned complete evidence; the quality tests failed. GPU Docker execution
could not be verified with the available GTX1650/4GB. Frontend code was unchanged;
its prior TypeScript/build checks are retained, not presented as newly rerun.

The existing deployed API was also read without submitting generation: authorized
/status returned200 and the original480px/33frame limits, unauthenticated access
returned401. No new pipeline was deployed. Independent professional review and
independent full GPU reproduction remain outstanding.
