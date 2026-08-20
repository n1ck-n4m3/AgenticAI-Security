# Code snapshots

Source-only mirrors of the official implementations, used to run G-Safeguard-family defenses. **No checkpoints and no generated dialogue datasets** (hundreds of MB).

Executable source matches the upstream repos. Comments and docstrings in a few files are English translations; runtime strings are unchanged.

## BlindGuard

ACL 2026. Apache-2.0. Upstream: [MR9812/BlindGuard](https://github.com/MR9812/BlindGuard). See `blindguard/LICENSE` and `blindguard/README.md`.

```text
PI/ TA/ MA/ MA_CSQA/   # four attack settings
train.py               # supervised G-Safeguard
train_un1.py / train_un2.py
```

You still need to generate graphs and embeddings locally (`gen_graph`, `merge_datasets`, `gen_training_dataset`).

## XG-Guard

ACL 2026. Upstream: [CampanulaBells/XG-Guard](https://github.com/CampanulaBells/XG-Guard). The snapshot has **no LICENSE file**. Original authors retain copyright. Do not treat this tree as an open-source grant. See `xg-guard/NOTICE.md`.

`datasets_local/` and `datasets_online/` are omitted; configure paths in `load_data/dataset_paths.py` after you obtain the authors' data.

## Related original work

G-Safeguard (ACL 2025) is the supervised backbone both papers extend.
