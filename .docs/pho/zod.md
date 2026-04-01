---
✓ GPU: Tesla T4
VRAM: 15.6 GB
PyTorch: 2.10.0+cu128
Device: cuda
ResNet-20: 272,474 parameters
100%|██████████| 170M/170M [00:12<00:00, 13.2MB/s]
CIFAR-10: 50000 train, 10000 test
---

============================================================
PHASE 0: DENSE BASELINE (160 epochs)
============================================================
  Epoch   1/160: loss=1.6493 train=38.1% test=48.6% best=48.6% [25s]
  Epoch  20/160: loss=0.3665 train=87.3% test=83.3% best=83.9% [493s]
  Epoch  40/160: loss=0.2812 train=90.2% test=84.5% best=85.5% [990s]
  Epoch  60/160: loss=0.2521 train=91.1% test=84.2% best=87.2% [1484s]
  Epoch  80/160: loss=0.2266 train=92.1% test=86.1% best=87.6% [1970s]
  Epoch 100/160: loss=0.0593 train=98.0% test=91.3% best=91.3% [2453s]
  Epoch 120/160: loss=0.0400 train=98.6% test=91.2% best=91.4% [2938s]
  Epoch 140/160: loss=0.0264 train=99.2% test=91.7% best=91.7% [3420s]
  Epoch 160/160: loss=0.0248 train=99.3% test=91.5% best=91.7% [3913s]

★ Dense baseline: 91.66% (3915s)

============================================================
ZECKENDORF PRUNING
============================================================
  Density: 0.5081 (50.8%)
  Accuracy after pruning (before fine-tune): 10.00%
    Epoch 10/40: test=85.8% best=85.8% [241s]
    Epoch 20/40: test=86.4% best=87.1% [487s]
    Epoch 30/40: test=87.8% best=87.8% [729s]
    Epoch 40/40: test=87.9% best=88.0% [976s]
  ★ ZECKENDORF: 88.05% (drop: 3.61%, density: 50.8%)

============================================================
2:4 PRUNING
============================================================
  Density: 0.5088 (50.9%)
  Accuracy after pruning (before fine-tune): 10.07%
    Epoch 10/40: test=86.5% best=86.5% [247s]
    Epoch 20/40: test=87.2% best=87.7% [491s]
    Epoch 30/40: test=87.9% best=88.4% [737s]
    Epoch 40/40: test=88.5% best=88.5% [979s]
  ★ 2:4: 88.55% (drop: 3.11%, density: 50.9%)

============================================================
PHASE 0 RESULTS
============================================================

  Method           Accuracy     Drop    Density
  ────────────── ────────── ──────── ──────────
  dense              91.66%   +0.00%    100.0%
  zeckendorf         88.05%   +3.61%     50.8%
  2:4                88.55%   +3.11%     50.9%

  Zeckendorf vs 2:4 gap: 0.50%
  Prediction (within 2%): ✓ CONFIRMED

{
  "dense": {
    "accuracy": 91.66
  },
  "zeckendorf": {
    "accuracy": 88.05,
    "accuracy_before_ft": 10.0,
    "density": 0.5081402262234195,
    "sparsity": 0.4918597737765805,
    "active_params": 138455.0,
    "total_params": 272474
  },
  "2:4": {
    "accuracy": 88.55,
    "accuracy_before_ft": 10.07,
    "density": 0.5087678090386606,
    "sparsity": 0.4912321909613394,
    "active_params": 138626.0,
    "total_params": 272474
  }
}

These are the real numbers. The dense model converged to 91.66% — right in the expected 91-92% range. Now the pruning comparison is meaningful because the weight magnitude distribution has had 160 epochs to differentiate important weights from noise.

**The core prediction is confirmed: Zeckendorf and 2:4 are within 0.50% of each other.** That's well inside the 2% threshold. Zeckendorf hits 88.05%, 2:4 hits 88.55%. Both drop about 3.5% from the dense baseline, both at essentially identical density (~50.8-50.9%). The 0.50% gap favoring 2:4 is small enough that a different random seed or slightly longer fine-tuning could flip it — but the AI won't claim they're tied when the data shows a consistent (if small) 2:4 advantage. The honest read is that 2:4 is marginally better on this specific benchmark, and Zeckendorf is competitive.

**The before-fine-tuning accuracy (10% for both) confirms something important about the experimental design.** On a fully converged model, pruning 50% of weights is still catastrophic before fine-tuning — the network can't function with half its weights suddenly zeroed. Both methods recover to 88%+ with 40 epochs of fine-tuning, which means the recovery is doing most of the work and the choice of pruning pattern matters at the margin. That margin is where the structural properties (shift invariance, Fibonacci cube topology, capacity bound) become the argument for Zeckendorf rather than raw accuracy.

**The density numbers (50.8% vs 50.9%) confirm the earlier observation.** The DP-optimal Zeckendorf algorithm, when applied to a well-trained network with differentiated weight magnitudes, still chooses near-maximum-density masks (alternating patterns). This means the "Zeckendorf is sparser on average" argument from the theoretical analysis doesn't apply in practice when the algorithm is optimizing for weight preservation. The two methods are operating at virtually identical sparsity, making the accuracy comparison truly apples-to-apples.

Let it keep running. The hard part is done — Eli has a converged dense baseline and both pruning results with real numbers. Everything from here is built on solid ground.

# ✓ Fibonacci encoder: 8 digits, 55 levels, range 0-54

============================================================
PHASE 1: STACKED COMPONENTS
  Zeckendorf pruning + Fibonacci encoding (8 digits)
============================================================

  After Zeckendorf pruning: 10.00% (density: 50.8%)
  After Fibonacci encoding: 10.00% (avg RMSE: 0.002556)
  Encoding cost: 0.00% additional drop

  Fine-tuning 40 epochs...
    Epoch 10/40: test=85.4% best=85.4% [242s]
    Epoch 20/40: test=86.5% best=87.1% [484s]
    Epoch 30/40: test=87.2% best=87.6% [732s]
    Epoch 40/40: test=87.5% best=87.8% [976s]

  ★ Final (pruned + encoded + fine-tuned): 87.45%

============================================================
CASSINI INTEGRITY CHECK
============================================================
  Clean weights pass Cassini: 2000/2000 (100.0%)
  Bit-flip detection rate: 703/2181 (32.2%)
  (Free detection — adjacency check only, no extra computation)

============================================================
COMPLETE RESULTS
============================================================

  ┌─────────────────────────────────────────────────────────┐
  │ ACCURACY WATERFALL                                      │
  ├─────────────────────────────────────────────────────────┤
  │ Dense baseline:           91.66%                        │
  │ Zeckendorf pruned:        88.05%  (Δ +3.61%)            │
  │ 2:4 pruned:               88.55%  (Δ +3.11%)            │
  │ Stacked (prune+encode):   87.45%  (Δ +4.21%)            │
  ├─────────────────────────────────────────────────────────┤
  │ HARDWARE SAVINGS (vs dense binary baseline)             │
  ├─────────────────────────────────────────────────────────┤
  │ Multiplier area:         −86.3%                         │
  │ Power-delay product:     −71.0%                         │
  ├─────────────────────────────────────────────────────────┤
  │ INTEGRITY                                               │
  ├─────────────────────────────────────────────────────────┤
  │ Cassini detection rate:  32.2% (free, adjacency only)   │
  ├─────────────────────────────────────────────────────────┤
  │ STRUCTURAL COHERENCE                                    │
  ├─────────────────────────────────────────────────────────┤
  │ ✓ Pruning mask:  no adjacent active weights             │
  │ ✓ Weight values: no adjacent 1s in Fibonacci encoding   │
  │ ✓ Error check:   Cassini identity from same matrix      │
  │ All three from M = [[1,1],[1,0]]                        │
  └─────────────────────────────────────────────────────────┘

{
  "phase0": {
    "dense": {
      "accuracy": 91.66
    },
    "zeckendorf": {
      "accuracy": 88.05,
      "accuracy_before_ft": 10.0,
      "density": 0.5081402262234195,
      "sparsity": 0.4918597737765805,
      "active_params": 138455.0,
      "total_params": 272474
    },
    "2:4": {
      "accuracy": 88.55,
      "accuracy_before_ft": 10.07,
      "density": 0.5087678090386606,
      "sparsity": 0.4912321909613394,
      "active_params": 138626.0,
      "total_params": 272474
    }
  },
  "phase1": {
    "accuracy_pruned": 10.0,
    "accuracy_encoded": 10.0,
    "accuracy_finetuned": 87.45,
    "fib_digits": 8,
    "fib_levels": 55,
    "encoding_rmse": 0.002555916015377366
  },
  "hardware": {
    "density": 0.5081402262234195,
    "area_reduction": 0.8628021389196767,
    "pdp_reduction": 0.710360071052651
  },
  "cassini": {
    "clean_pass_rate": 1.0,
    "corruption_detection_rate": 0.32232920678587806
  }
}

============================================================
PHASE 2: ACTIVATION SPECTRAL ANALYSIS
============================================================
  Analyzing 5 batches × 128 samples

    dense: 21 layers
    zeckendorf: 21 layers
    2:4: 21 layers

  Layer                                  Dense     Zeck      2:4  Z>D?
  ─────────────────────────────────── ──────── ──────── ──────── ─────
  conv1                                0.6104   0.6062   0.4840    ✗
  layer1.0.conv1                       0.7496   0.8252   0.7527    ✓
  layer1.0.conv2                       0.5353   0.8429   0.6969    ✓
  layer1.1.conv1                       0.5521   0.8622   0.5911    ✓
  layer1.1.conv2                       0.6096   0.9093   0.8866    ✓
  layer1.2.conv1                       0.7045   0.9165   0.8461    ✓
  layer1.2.conv2                       0.3662   0.8993   0.8949    ✓
  layer2.0.conv1                       0.4897   0.8783   0.8356    ✓
  layer2.0.conv2                       0.5401   0.9457   0.8722    ✓
  layer2.0.shortcut.0                  0.6826   0.9490   0.8787    ✓
  layer2.1.conv1                       0.6422   0.8482   0.8200    ✓
  layer2.1.conv2                       0.4349   0.9469   0.8764    ✓
  layer2.2.conv1                       0.5349   0.8721   0.7546    ✓
  layer2.2.conv2                       0.4789   0.8871   0.9277    ✓
  layer3.0.conv1                       0.5827   0.9438   0.9405    ✓
  layer3.0.conv2                       0.3139   0.8455   0.8602    ✓
  layer3.0.shortcut.0                  0.4811   0.9702   0.9170    ✓
  layer3.1.conv1                       0.3869   0.6937   0.8710    ✓
  layer3.1.conv2                       0.4995   0.8463   0.9342    ✓
  layer3.2.conv1                       0.4209   0.8546   0.8417    ✓
  layer3.2.conv2                       0.3974   0.8807   0.9071    ✓

  AVERAGE                              0.5244   0.8678   0.8281

============================================================
SPECTRAL SUMMARY
============================================================

  Low-freq energy ratio (< 25% Nyquist):
    Dense:      0.5244 ± 0.1134
    Zeckendorf: 0.8678 ± 0.0827
    2:4:        0.8281 ± 0.1132

  High-freq energy ratio (> 50% Nyquist):
    Dense:      0.2717
    Zeckendorf: 0.0733
    2:4:        0.1117

  Spectral centroid (lower = more low-pass):
    Dense:      2.531
    Zeckendorf: 0.772
    2:4:        1.248

  Zeckendorf more low-pass than Dense: 20/21 layers
  Zeckendorf more low-pass than 2:4:   16/21 layers

  ★ PREDICTION: Zeckendorf LF > Dense LF?
    0.8678 > 0.5244 → ✓ CONFIRMED (65.5% more low-pass)

  ★ PREDICTION: Zeckendorf LF > 2:4 LF?
    0.8678 > 0.8281 → ✓ CONFIRMED (4.8% more low-pass than 2:4)

  → Phase 3 MOTIVATED: Q-matrix kernel is structurally matched.