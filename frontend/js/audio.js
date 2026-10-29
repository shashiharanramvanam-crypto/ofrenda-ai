/**
 * Procedural Web Audio API Soundscape Engine for Ofrenda AI
 * Generates wind through marigolds, ember crackles, and resonant singing bowl chimes.
 * 100% procedural code — zero external audio assets required.
 */

class OfrendaAudio {
  constructor() {
    this.ctx = null;
    this.isPlaying = false;
    this.windGain = null;
    this.crackleGain = null;
    this.crackleTimer = null;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggle() {
    this.init();
    if (this.isPlaying) {
      this.stop();
      return false;
    } else {
      this.start();
      return true;
    }
  }

  start() {
    if (!this.ctx) this.init();
    this.isPlaying = true;

    // Master Ambient Gain
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.setValueAtTime(0.3, this.ctx.currentTime);
    this.masterGain.connect(this.ctx.destination);

    // 1. Procedural Wind (Filtered Pink/Brown Noise)
    this.startWind();

    // 2. Procedural Candle Ember Crackles
    this.startCrackles();
  }

  stop() {
    this.isPlaying = false;
    if (this.windGain) {
      this.windGain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 1.0);
    }
    if (this.crackleTimer) {
      clearInterval(this.crackleTimer);
    }
  }

  startWind() {
    const bufferSize = this.ctx.sampleRate * 2;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0;

    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99 * b0 + white * 0.05;
      b1 = 0.95 * b1 + white * 0.05;
      b2 = 0.85 * b2 + white * 0.1;
      output[i] = (b0 + b1 + b2) * 0.3;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = noiseBuffer;
    whiteNoise.loop = true;

    // Lowpass filter with subtle modulation
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(220, this.ctx.currentTime);

    // Gentle LFO for wind swell
    const lfo = this.ctx.createOscillator();
    lfo.frequency.setValueAtTime(0.15, this.ctx.currentTime);
    const lfoGain = this.ctx.createGain();
    lfoGain.gain.setValueAtTime(140, this.ctx.currentTime);
    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);

    this.windGain = this.ctx.createGain();
    this.windGain.gain.setValueAtTime(0.25, this.ctx.currentTime);

    whiteNoise.connect(filter);
    filter.connect(this.windGain);
    this.windGain.connect(this.masterGain);

    whiteNoise.start();
    lfo.start();
  }

  startCrackles() {
    // Generate sporadic micro crackle impulses resembling glowing candle wick / copal incense
    this.crackleTimer = setInterval(() => {
      if (!this.isPlaying || !this.ctx) return;
      if (Math.random() > 0.45) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      
      const freq = 600 + Math.random() * 2400;
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      const burstLen = 0.005 + Math.random() * 0.015;
      gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + burstLen);

      osc.connect(gain);
      gain.connect(this.masterGain);

      osc.start();
      osc.stop(this.ctx.currentTime + burstLen);
    }, 180);
  }

  // Play a sacred singing bowl chime when candle is lit or altar is opened
  playChime(fundamental = 432) {
    if (!this.ctx) this.init();
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const now = this.ctx.currentTime;
    const harmonics = [1, 2.02, 3.01, 4.2];
    const weights = [0.25, 0.12, 0.05, 0.02];

    harmonics.forEach((h, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(fundamental * h, now);

      gain.gain.setValueAtTime(weights[idx], now);
      // Long gentle ringing decay
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 3.2);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 3.2);
    });
  }
}

window.ofrendaAudio = new OfrendaAudio();
