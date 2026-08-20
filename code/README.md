# Code snapshots

Source-only mirrors for running the G-Safeguard-family defenses. **No checkpoints and no generated dialogue datasets** (hundreds of MB).

## BlindGuard

ACL 2026. Apache-2.0. See `blindguard/LICENSE` and `blindguard/README.md`.

```text
PI/ TA/ MA/ MA_CSQA/   # four attack settings
train.py               # supervised G-Safeguard
train_un1.py / train_un2.py
```

You still need to generate graphs and embeddings locally (`gen_graph`, `merge_datasets`, `gen_training_dataset`).

## XG-Guard

ACL 2026. The snapshot we used had **no LICENSE file**. Original authors retain copyright. Do not treat this tree as an open-source grant. See `xg-guard/NOTICE.md`.

`datasets_local/` and `datasets_online/` are omitted; configure paths in `load_data/dataset_paths.py` after you obtain the authors' data.

## Related original work

G-Safeguard (ACL 2025) is the supervised backbone both papers extend.
