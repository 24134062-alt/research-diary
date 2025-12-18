#ifndef VAD_H
#define VAD_H

#include <stdint.h>
#include <stdbool.h>

// VAD Configuration
#define VAD_THRESHOLD_DEFAULT   300     // Energy threshold for voice detection
#define VAD_HANGOVER_MS         300     // Continue for 300ms after voice stops
#define VAD_FRAME_SIZE_SAMPLES  256     // Number of samples per frame

/**
 * Voice Activity Detection (VAD) Class
 * 
 * Uses energy-based detection with hangover mechanism to reduce
 * bandwidth by only transmitting when speech is detected.
 */
class VAD {
public:
    VAD(uint16_t threshold = VAD_THRESHOLD_DEFAULT, 
        uint16_t hangoverMs = VAD_HANGOVER_MS);
    
    /**
     * Process audio samples and determine if voice is present
     * @param samples Pointer to 16-bit PCM samples
     * @param numSamples Number of samples
     * @return true if voice activity detected (including hangover period)
     */
    bool process(int16_t* samples, size_t numSamples);
    
    /**
     * Get the current energy level (for debugging/display)
     */
    uint32_t getEnergy() const { return _lastEnergy; }
    
    /**
     * Check if currently in active speech (not hangover)
     */
    bool isSpeaking() const { return _isSpeaking; }
    
    /**
     * Set new threshold value
     */
    void setThreshold(uint16_t threshold) { _threshold = threshold; }
    
    /**
     * Get current threshold
     */
    uint16_t getThreshold() const { return _threshold; }

private:
    uint16_t _threshold;
    uint16_t _hangoverMs;
    uint32_t _lastEnergy;
    bool _isSpeaking;
    unsigned long _speechEndTime;
};

#endif // VAD_H
