# Category IX: TinyML & Edge AI

> **Tổng quan**: TinyML và Edge AI tập trung vào việc deploy machine learning trên các thiết bị cực kỳ hạn chế về tài nguyên như microcontrollers.

---

## 86. TinyML Model Optimization for Microcontrollers

### Mô tả
Tối ưu ML models để chạy trên MCUs với KB memory và MHz clock speeds.

### MCU Constraints
```
Typical MCU (ARM Cortex-M4):
├── Flash:  256KB - 2MB (model storage)
├── SRAM:   64KB - 512KB (runtime memory)
├── Clock:  80-200 MHz
├── Power:  10-100 mW
└── No FPU or limited FP support
```

### Optimization Techniques
| Technique | Memory Reduction | Compute Reduction |
|-----------|-----------------|-------------------|
| INT8 quantization | 4x | 2-4x |
| Pruning | 2-10x | 2-10x |
| Architecture search | 10-100x | 10-100x |
| Operator fusion | 1.2-2x | 1.2-2x |

### MCUNet Approach
```
1. Neural Architecture Search for MCUs
2. TinyNAS: Search in micro-scale space
3. TinyEngine: Optimized inference engine
4. Result: ImageNet on 256KB SRAM!
```

### Đọc thêm
- MCUNet (MIT, 2020)
- TinyML Book (O'Reilly, 2022)
- TensorFlow Lite Micro

---

## 87. On-device Learning with Limited Resources

### Mô tả
Thực hiện training hoặc fine-tuning trực tiếp trên edge devices.

### Why On-device Learning?
```
Cloud training:              On-device learning:
├── Privacy issues           ├── Data stays local
├── Latency                  ├── Real-time adaptation
├── Connectivity required    ├── Works offline
└── Data transfer costs      └── Personalization
```

### Memory Challenge
```
Inference memory: Weights + Activations
Training memory:  Weights + Activations + Gradients + Optimizer states
                  ~4-10x more memory than inference!
```

### Techniques for On-device Training
1. **Sparse updates**: Only update subset of weights
2. **Gradient checkpointing**: Trade compute for memory
3. **Low-rank adaptation**: Train small adapter layers
4. **Quantized training**: Train in low precision

### Đọc thêm
- On-device Training Survey (2022)
- TinyTL (MIT, 2020)

---

## 88. Federated Learning on Edge Devices

### Mô tả
Distributed training across edge devices mà không chia sẻ raw data.

### Federated Learning Process
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Device1 │     │ Device2 │     │ Device3 │
│ Local   │     │ Local   │     │ Local   │
│ Training│     │ Training│     │ Training│
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
                     ▼
              ┌────────────┐
              │   Server   │
              │ Aggregate  │
              │   Models   │
              └─────┬──────┘
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ Updated │   │ Updated │   │ Updated │
│ Device1 │   │ Device2 │   │ Device3 │
└─────────┘   └─────────┘   └─────────┘
```

### Challenges
| Challenge | Solution |
|-----------|----------|
| Non-IID data | FedProx, SCAFFOLD |
| Communication | Gradient compression |
| Heterogeneity | Personalization |
| Privacy | Differential privacy |
| Stragglers | Asynchronous aggregation |

### Đọc thêm
- FedAvg (Google, 2017)
- Federated Learning Survey (2021)

---

## 89. Privacy-preserving Edge AI

### Mô tả
Techniques để protect user privacy trong edge AI deployments.

### Privacy Threats
```
Threats:
├── Data leakage (raw data exposed)
├── Model inversion (reconstruct inputs)
├── Membership inference (detect training data)
└── Gradient leakage (in federated learning)
```

### Privacy Techniques
| Technique | Protection | Overhead |
|-----------|------------|----------|
| **On-device inference** | Data stays local | None |
| **Differential privacy** | Statistical guarantees | Accuracy loss |
| **Secure aggregation** | Protect gradients | Computation |
| **Homomorphic encryption** | Compute on encrypted | Very high |
| **TEE** | Hardware isolation | Moderate |

### Differential Privacy
```python
# Add calibrated noise to gradients
noisy_gradient = gradient + Laplace(0, sensitivity/epsilon)

# Provides (ε, δ)-differential privacy
# Smaller ε = more privacy, less accuracy
```

### Đọc thêm
- Differential Privacy for ML (2016)
- Private AI Survey (2021)

---

## 90. Real-time Object Detection on MCUs

### Mô tả
Deploy object detection models như YOLO trên microcontrollers.

### Object Detection Progression
```
YOLO:        ~7M params,  ~70 FPS on GPU
YOLOv5-nano: ~1.9M params
Tiny models: ~100K params, ~10 FPS on MCU
```

### MCU-friendly Architectures
| Model | Params | SRAM | Flash | Accuracy |
|-------|--------|------|-------|----------|
| MobileNetV2-SSD | 2M | 265KB | 2MB | 20% mAP |
| YOLO-Fastest | 230K | 120KB | 900KB | 13% mAP |
| MCUNet-Det | 500K | 256KB | 1MB | 25% mAP |

### Optimization Pipeline
```
Full YOLO → Prune → Quantize → NAS → Optimize ops
    │         │        │        │        │
    │         │        │        │        └─ Fused ops, INT8
    │         │        │        └─ Tiny architecture
    │         │        └─ INT8/INT4
    │         └─ 80% sparsity
    └─ 7M params
```

### Đọc thêm
- YOLO-Fastest (2020)
- Person Detection on MCU (Google, 2019)

---

## 91. Voice Recognition for Ultra-low Power Devices

### Mô tả
Keyword spotting và voice recognition trên always-on devices.

### Always-on Voice Detection
```
Power budget: <1mW (battery life months/years)
Latency: <200ms
Accuracy: >95% for keywords

Pipeline:
Audio → MFCC features → Tiny DNN → Keyword detected?
                            │
                    ~10-50KB model
```

### Model Architectures
| Model | Size | Power | Accuracy |
|-------|------|-------|----------|
| DS-CNN | 50KB | 500μW | 95% |
| BC-ResNet | 20KB | 200μW | 92% |
| TC-ResNet | 30KB | 300μW | 94% |

### Feature Extraction
```
Raw audio → MFCC features:
- Window: 25ms
- Hop: 10ms  
- Features: 13 MFCC coefficients
- Stacked: 1s context = 40 frames × 13 = 520 features
```

### Đọc thêm
- Hello Edge (ARM, 2018)
- Keyword Spotting (Google Speech Commands)

---

## 92. Sensor Fusion on Resource-constrained Hardware

### Mô tả
Combine multiple sensor inputs cho AI inference trên limited hardware.

### Sensor Types for Edge AI
```
Common sensors:
├── IMU (accelerometer, gyroscope): ~100Hz, 6-9 channels
├── Microphone: 16kHz, 1-4 channels
├── Camera: 30Hz, 640×480
├── Pressure/Temperature: 1Hz
└── GPS: 1Hz
```

### Fusion Strategies
| Level | Description | Compute |
|-------|-------------|---------|
| **Early** | Concatenate raw features | High |
| **Late** | Fuse predictions | Low |
| **Intermediate** | Fuse embeddings | Medium |

### Early Fusion Example
```python
def fused_model(imu_data, audio_data):
    imu_features = imu_encoder(imu_data)      # 32 dims
    audio_features = audio_encoder(audio_data) # 64 dims
    combined = concat(imu_features, audio_features)  # 96 dims
    return classifier(combined)
```

### Đọc thêm
- Multi-modal TinyML (2021)
- Sensor Fusion Survey (2020)

---

## 93. Predictive Maintenance with TinyML

### Mô tả
Deploy anomaly detection và failure prediction trên industrial edge devices.

### Use Cases
```
Industrial TinyML:
├── Vibration analysis (motor bearings)
├── Acoustic monitoring (equipment sounds)
├── Thermal monitoring
├── Power quality analysis
└── Visual inspection (simple cameras)
```

### Anomaly Detection Models
| Approach | Model Size | Accuracy | Interpretability |
|----------|------------|----------|------------------|
| Autoencoder | 10-50KB | High | Low |
| One-class SVM | 1-5KB | Medium | High |
| Isolation Forest | 5-20KB | Medium | Medium |
| Threshold-based | <1KB | Low | Very High |

### Implementation Example
```python
# Vibration anomaly detection
class VibrateAnomalyDetector:
    def __init__(self):
        self.autoencoder = TinyAutoencoder(input_dim=32)
        self.threshold = 0.1
    
    def is_anomaly(self, vibration_fft):
        reconstruction = self.autoencoder(vibration_fft)
        error = mse(vibration_fft, reconstruction)
        return error > self.threshold
```

### Đọc thêm
- TinyML for Industrial IoT (2021)
- Edge Impulse Case Studies

---

## 94. Wearable AI System Design

### Mô tả
Design AI systems cho wearables như smartwatches, fitness trackers, health monitors.

### Wearable Constraints
```
Constraints:
├── Battery: 100-500mAh (1-7 day life)
├── Size: <1cm³ for electronics
├── Weight: <50g total
├── Heat: Must not be noticeable to user
└── Comfort: Minimal sensor contact
```

### Wearable AI Applications
| Application | Sensors | Model Size | Power |
|-------------|---------|------------|-------|
| Step counting | Accelerometer | <1KB | <10μW |
| Activity recognition | IMU | 10-50KB | <1mW |
| Heart rate estimation | PPG | 5-20KB | <500μW |
| Atrial fibrillation | ECG | 20-100KB | <2mW |
| Sleep staging | Multiple | 50-200KB | <5mW |

### Power-Accuracy Trade-off
```
Duty cycling:
├── Continuous: 100% accuracy, 100% power
├── 10% duty: 90% accuracy, 15% power
├── 1% duty: 70% accuracy, 5% power
└── Event-triggered: Variable accuracy, minimal power
```

### Đọc thêm
- Wearable AI Survey (2022)
- Apple Watch Health Features

---

## 95. Battery-aware Inference Scheduling

### Mô tả
Schedule AI inference tasks based on battery state và usage patterns.

### Scheduling Factors
```
Consider:
├── Battery level (current charge)
├── Charging state (plugged in?)
├── Time to next charge (predicted)
├── Task urgency (real-time vs deferrable)
└── Model importance/accuracy needs
```

### Dynamic Scheduling
```python
def schedule_inference(battery_level, task_urgency, model_options):
    if battery_level > 0.7:
        return model_options['high_accuracy']
    elif battery_level > 0.3:
        if task_urgency == 'high':
            return model_options['high_accuracy']
        else:
            return model_options['efficient']
    else:  # Low battery
        if task_urgency == 'critical':
            return model_options['efficient']
        else:
            return defer_task()
```

### Energy Harvesting
```
Supplement battery with:
├── Solar cells
├── Vibration harvesting
├── RF harvesting
└── Thermal harvesting

AI can predict energy availability
and schedule accordingly
```

### Đọc thêm
- Energy-aware ML (2020)
- Battery-aware Computing Survey

---

## 📚 TinyML Ecosystem

### Frameworks
| Framework | Supported HW | Features |
|-----------|--------------|----------|
| TensorFlow Lite Micro | All MCUs | Quantization, interpreter |
| Edge Impulse | Nordic, ST, Arm | End-to-end platform |
| CMSIS-NN | Arm Cortex-M | Optimized kernels |
| STM32Cube.AI | STM32 | ST optimization |
| TinyEngine | Various | Memory efficient |

### Development Workflow
```
1. Train on PC (TensorFlow/PyTorch)
2. Optimize (quantize, prune)
3. Convert (TFLite, ONNX)
4. Deploy (generate C code)
5. Profile (latency, memory)
6. Iterate
```
