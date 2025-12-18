# Category X: Compilers & Toolchains

> **Tổng quan**: Deep Learning compilers và toolchains tự động hóa việc optimize và deploy models lên diverse hardware platforms.

---

## 96. Hardware-aware Deep Learning Compilers

### Mô tả
Compilers chuyển đổi high-level ML models thành optimized code cho specific hardware.

### Compilation Pipeline
```
Framework Model (PyTorch/TF)
        │
        ▼
┌───────────────────┐
│  High-level IR    │  (ONNX, Relay, MLIR)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Graph            │  Fusion, layout, scheduling
│  Optimizations    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Low-level IR     │  Loops, memory  
│  Optimizations    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Code Generation  │  CUDA, x86, ARM, FPGA
└───────────────────┘
```

### Major DL Compilers
| Compiler | Origin | Target Hardware |
|----------|--------|-----------------|
| **TVM** | Apache | All (extensible) |
| **XLA** | Google | TPU, GPU, CPU |
| **TensorRT** | NVIDIA | NVIDIA GPU |
| **ONNX Runtime** | Microsoft | Cross-platform |
| **OpenVINO** | Intel | Intel hardware |
| **Core ML** | Apple | Apple devices |

### Key Optimizations
1. **Operator fusion**: Combine ops to reduce memory traffic
2. **Layout optimization**: NCHW vs NHWC
3. **Memory planning**: Minimize activation memory
4. **Vectorization**: Use SIMD instructions

### Đọc thêm
- TVM: Automatic ML Compiler (2018)
- XLA Overview (Google)
- MLIR (2020)

---

## 97. Auto-tuning for Target Hardware

### Mô tả
Automatically search for best implementation parameters (tiling, vectorization, etc.) cho specific hardware.

### Tunable Parameters
```
For a convolution:
├── Tile sizes (block dimensions)
├── Loop ordering (nest permutation)
├── Vectorization width
├── Unroll factors
├── Parallelization
└── Memory layouts
```

### Search Space Size
```
Typical conv2d tuning space:
- Tile H: 1-32 (5 choices)
- Tile W: 1-32 (5 choices)  
- Tile C: 1-256 (8 choices)
- Unroll: 1-8 (3 choices)
- ...

Total: Millions of configurations!
```

### Auto-tuning Methods
| Method | Description | Speed |
|--------|-------------|-------|
| **Grid search** | Try all combinations | Slow |
| **Random search** | Random sampling | Medium |
| **Bayesian opt** | Guided search | Fast |
| **ML-based** | Learn from history | Very fast |
| **Transfer learning** | Reuse past tuning | Instant |

### TVM AutoTVM
```python
# Define tuning space
@autotvm.search_space
def conv2d_auto(cfg, data, kernel):
    cfg.define_split("tile_y", y, num_outputs=3)
    cfg.define_split("tile_x", x, num_outputs=3)
    cfg.define_split("tile_rc", rc, num_outputs=2)
    # ...
    
# Auto-tune
tuner = autotvm.tuner.XGBTuner()
tuner.tune(n_trial=1000)
```

### Đọc thêm
- AutoTVM (2018)
- Ansor (2020)
- FlexTensor (2020)

---

## 98. Graph-level Optimizations for Neural Networks

### Mô tả
Optimizations operating on computation graph level (before lowering to operators).

### Graph Representation
```
Input → Conv → BN → ReLU → MaxPool → ...
        ↓
[Graph with nodes = ops, edges = tensors]
```

### Common Graph Optimizations
| Optimization | Description | Benefit |
|--------------|-------------|---------|
| **Constant folding** | Pre-compute constant ops | Reduce ops |
| **Dead code elimination** | Remove unused nodes | Reduce memory |
| **Common subexpression** | Reuse identical computations | Reduce ops |
| **Operator fusion** | Combine adjacent ops | Reduce memory traffic |
| **Layout transformation** | Optimize data layout | Improve cache usage |

### Operator Fusion Examples
```
Before fusion:
Input → Conv → Store → Load → BN → Store → Load → ReLU → Output
        ↑ Memory write      ↑ Memory write

After fusion:
Input → [Conv + BN + ReLU] → Output
        ↑ Single fused kernel
        
Saves 2 memory round-trips!
```

### Fusion Rules
```python
# Example fusion patterns
patterns = [
    (Conv, BatchNorm, ReLU) → FusedConvBNReLU,
    (MatMul, Add) → LinearWithBias,
    (Conv, Add) → ConvWithResidual,
]
```

### Đọc thêm
- ONNX Graph Optimizer
- TensorRT Layer Fusion
- XLA Fusion

---

## 99. Cross-platform Model Deployment

### Mô tả
Deploy same model across diverse hardware platforms efficiently.

### Deployment Challenges
```
One model, many targets:
├── Cloud GPU (NVIDIA)
├── Cloud TPU (Google)  
├── Server CPU (x86)
├── Mobile GPU (Adreno, Mali)
├── Mobile NPU (Qualcomm, MediaTek)
├── Edge TPU (Coral)
├── FPGA (Various)
└── MCU (ARM Cortex-M)
```

### Cross-platform Strategy
```
Model (PyTorch/TF)
        │
        ▼
    ┌───────────────┐
    │  ONNX/TFLite  │  Intermediate format
    └───────┬───────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌─────────┐   ┌─────────┐
│ TensorRT│   │ TFLite  │
│ (GPU)   │   │ (Mobile)│
└─────────┘   └─────────┘
```

### Platform-specific Optimizations
| Platform | Optimization | Tool |
|----------|--------------|------|
| NVIDIA GPU | FP16, INT8, fusion | TensorRT |
| Intel CPU | AVX-512, VNNI | OpenVINO |
| Arm CPU | NEON, INT8 | Arm NN |
| Qualcomm | HTP, Hexagon | Qualcomm AI Engine |
| Apple | ANE, Metal | Core ML |

### ONNX Workflow
```python
# Export from PyTorch
torch.onnx.export(model, input, "model.onnx")

# Optimize for target
# Option 1: TensorRT
trt_engine = tensorrt.convert(onnx_model)

# Option 2: ONNX Runtime
ort_session = onnxruntime.InferenceSession("model.onnx")

# Option 3: TFLite
tflite_model = tf.lite.TFLiteConverter.from_onnx("model.onnx")
```

### Đọc thêm
- ONNX Specification
- Multi-platform Deployment Guide

---

## 100. Runtime Adaptation based on Hardware State

### Mô tả
Dynamically adapt model execution based on current hardware conditions.

### Hardware State Variables
```
Runtime conditions:
├── Thermal state (temperature)
├── Power state (battery level)
├── Load (other processes)
├── Frequency (current clock)
└── Memory (available RAM)
```

### Adaptation Strategies
| Condition | Adaptation |
|-----------|------------|
| High temperature | Reduce precision, batch size |
| Low battery | Use efficient model variant |
| High load | Queue or defer inference |
| Memory pressure | Use streaming inference |

### Dynamic Model Switching
```python
class AdaptiveInference:
    def __init__(self):
        self.models = {
            'full': load_model('model_fp32.tflite'),
            'efficient': load_model('model_int8.tflite'),
            'tiny': load_model('model_tiny.tflite'),
        }
    
    def infer(self, input):
        hw_state = get_hardware_state()
        
        if hw_state.temperature > 80 or hw_state.battery < 20:
            model = self.models['tiny']
        elif hw_state.temperature > 60 or hw_state.battery < 50:
            model = self.models['efficient']
        else:
            model = self.models['full']
            
        return model.predict(input)
```

### Thermal Throttling Awareness
```
Monitor:
├── CPU temperature → Predict throttling
├── Reduce workload before throttling
├── Maintain consistent performance
└── Avoid thermal shutdown
```

### Đọc thêm
- Adaptive Computing Survey (2021)
- Mobile Inference Optimization

---

## 📚 Toolchain Summary

### Complete Deployment Pipeline
```
1. TRAINING
   PyTorch / TensorFlow / JAX
           │
           ▼
2. EXPORT
   ONNX / SavedModel / TorchScript
           │
           ▼
3. OPTIMIZE
   TVM / TensorRT / OpenVINO
           │
           ▼
4. QUANTIZE
   INT8 / INT4 / FP16
           │
           ▼
5. COMPILE
   Target-specific code generation
           │
           ▼
6. DEPLOY
   Runtime integration
           │
           ▼
7. MONITOR
   Performance tracking, adaptation
```

### Choosing the Right Tool
| Scenario | Recommended Tool |
|----------|------------------|
| NVIDIA GPU deployment | TensorRT |
| Intel CPU/GPU | OpenVINO |
| Mobile (Android/iOS) | TFLite, Core ML |
| Multi-platform | ONNX Runtime |
| MCU/Embedded | TF Lite Micro, Edge Impulse |
| Custom hardware | TVM, MLIR |
| Research/Flexibility | TVM, PyTorch |

### Essential Resources
- TVM Documentation
- TensorRT Developer Guide
- ONNX Runtime docs
- MLCommons Inference Benchmark

---

# 🎯 Tổng Kết 100 Chủ Đề

```
Hardware-aware AI Research Topics:

┌──────────────────────────────────────────────────────────────┐
│  Category                              │ Topics │ Core Theme │
├────────────────────────────────────────┼────────┼────────────┤
│  I.   Neural Architecture Search       │   15   │ AutoML     │
│  II.  Quantization                     │   12   │ Precision  │
│  III. Pruning & Sparsity               │   10   │ Efficiency │
│  IV.  Knowledge Distillation           │    8   │ Transfer   │
│  V.   Model Compression                │    8   │ Size       │
│  VI.  Hardware Accelerators            │   12   │ Hardware   │
│  VII. Memory & Compute                 │   10   │ Bottleneck │
│  VIII.Emerging Technologies            │   10   │ Future     │
│  IX.  TinyML & Edge AI                 │   10   │ Deploy     │
│  X.   Compilers & Toolchains           │    5   │ Tools      │
├────────────────────────────────────────┼────────┼────────────┤
│  TOTAL                                 │  100   │            │
└────────────────────────────────────────┴────────┴────────────┘
```
