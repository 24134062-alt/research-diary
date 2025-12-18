# 🧠 Neuromorphic Computing - Research Hub

> **Hướng nghiên cứu chuyên sâu về Neuromorphic Computing**  
> **Cập nhật**: 12/2024

---

## 📁 Cấu Trúc Thư Mục

```
neuromorphic-computing/
├── README.md (file này)
├── fundamentals/          # Kiến thức nền tảng
├── papers/               # Notes về papers quan trọng
├── projects/             # Projects thực hành
├── tutorials/            # Hướng dẫn từng bước
└── resources/            # Tài liệu tham khảo
```

---

## 🎯 Mục Tiêu Học Tập

### Phase 1: Fundamentals (4 tuần)
- [ ] Hiểu neuron models (LIF, Izhikevich)
- [ ] Spiking Neural Networks basics
- [ ] Temporal coding vs Rate coding
- [ ] STDP learning rule

### Phase 2: Frameworks (4 tuần)
- [ ] snnTorch - PyTorch-based SNN
- [ ] Norse - Norse framework
- [ ] Intel Lava - Loihi programming
- [ ] BindsNET - Simulation

### Phase 3: Projects (4 tuần)
- [ ] SNN MNIST classification
- [ ] Gesture recognition với DVS
- [ ] Keyword spotting
- [ ] Energy comparison

---

## 📚 Key Topics

| Topic | File | Status |
|-------|------|--------|
| Spiking Neuron Models | `fundamentals/neuron-models.md` | 🔲 Todo |
| SNN Training Methods | `fundamentals/snn-training.md` | 🔲 Todo |
| Neuromorphic Hardware | `fundamentals/hardware.md` | 🔲 Todo |
| Intel Loihi | `hardware/intel-loihi.md` | 🔲 Todo |
| IBM TrueNorth | `hardware/ibm-truenorth.md` | 🔲 Todo |

---

## 🔗 Quick Links

### Frameworks
- [snnTorch](https://snntorch.readthedocs.io/) - Recommended starting point
- [Norse](https://norse.github.io/norse/)
- [Intel Lava](https://lava-nc.org/)
- [BindsNET](https://bindsnet-docs.readthedocs.io/)

### Datasets
- N-MNIST (Neuromorphic MNIST)
- DVS-Gesture
- SHD (Spiking Heidelberg Digits)
- N-Caltech101

### Papers
- See `emerging-research/01-neuromorphic-computing.md` for detailed paper list

---

## 🚀 Getting Started

```bash
# Setup environment
conda create -n neuromorphic python=3.10
conda activate neuromorphic

# Install snnTorch
pip install snntorch

# Verify installation
python -c "import snntorch; print('Success!')"
```

### First Exercise
```python
import snntorch as snn
import torch

# Create a Leaky Integrate-and-Fire neuron
lif = snn.Leaky(beta=0.9)

# Simulate
mem = torch.zeros(1)
spk_rec = []

for step in range(100):
    cur_in = torch.rand(1)  # Random input
    spk, mem = lif(cur_in, mem)
    spk_rec.append(spk)

print(f"Total spikes: {sum(spk_rec)}")
```

---

## 📝 Notes

*Thêm ghi chú của bạn tại đây...*
