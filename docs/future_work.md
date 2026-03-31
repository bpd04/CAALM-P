# Future Work & Hardware Translation Roadmap

## 1. Toward >90% and Robust Suppression

Current results demonstrate:
- Mean suppression ≈ 89.7%
- Multiple cases exceeding 90%

The remaining limitation is not controller design, but:

>  **Phase alignment accuracy and plant modeling fidelity**

Future improvements will focus on:
- Continuous phase tracking instead of blockwise estimation
- Frequency drift adaptation
- Improved antiphase matching using phase-locked loop (PLL)-like mechanisms

---

## 2. Why 100% Suppression is Not the Goal

In realistic neurophysiology:
- Complete elimination of oscillations is neither feasible nor desirable
- Over-suppression may distort normal neural signaling

Thus, the objective shifts to:

> **Controlled and selective suppression of pathological oscillatory components**

---

## 3. Real-World Hardware Translation

### Sensing Layer
- Surface electrodes (TENS / EMG-grade)
- Instrumentation amplifier (e.g., AD620 / INA333)
- ADC (12–16 bit resolution)

### Processing Layer
- Microcontroller (ESP32 / STM32) OR embedded processor
- Real-time filtering and feature extraction
- Phase estimation and classification

### Stimulation Layer
- Programmable current-controlled stimulator
- Biphasic waveform generation
- Safety-compliant current limits

---

## 4. Key Engineering Challenges

- Real-time phase estimation under noise
- Electrode-skin impedance variability
- Safety and current compliance
- Latency between sensing and stimulation

---

## 5. Experimental Validation Plan

1. Validate on recorded biosignals (offline replay)
2. Implement real-time closed-loop on microcontroller
3. Test on synthetic + controlled input signals
4. Gradually move toward human-safe pilot testing

---

## 6. What This Project Enables

This work establishes:

- A *closed-loop neuromodulation framework*
- A *testable control architecture*
- A *clear pathway from simulation → hardware*

---

## Final Direction

> The next milestone is not higher suppression in simulation,  
> but **bridging simulation with real-world bioelectronic systems.**