#include "vad.h"
#include <Arduino.h>
#include <stdlib.h>

VAD::VAD(uint16_t threshold, uint16_t hangoverMs)
    : _threshold(threshold), _hangoverMs(hangoverMs), _lastEnergy(0),
      _isSpeaking(false), _speechEndTime(0) {}

bool VAD::process(int16_t *samples, size_t numSamples) {
  if (samples == nullptr || numSamples == 0) {
    return false;
  }

  // Calculate average absolute energy
  uint32_t energy = 0;
  for (size_t i = 0; i < numSamples; i++) {
    energy += abs(samples[i]);
  }
  energy /= numSamples;
  _lastEnergy = energy;

  unsigned long now = millis();

  // Check if energy exceeds threshold
  if (energy > _threshold) {
    _isSpeaking = true;
    _speechEndTime = now + _hangoverMs;
    return true;
  }

  // Hangover period - continue transmitting for a short time after speech ends
  // This prevents cutting off the end of words/sentences
  if (now < _speechEndTime) {
    _isSpeaking = false; // Not actively speaking, but in hangover
    return true;
  }

  // No voice activity
  _isSpeaking = false;
  return false;
}
