# 📡 resonance_engine.py — Environmental energy resonance per zone

class ResonanceEngine:
    def __init__(self):
        self.zone_resonance = {}

    def tune_zone(self, zone_name, frequency_hz, waveform="sine", emotional_resonance=None):
        self.zone_resonance[zone_name] = {
            "frequency_hz": frequency_hz,
            "waveform": waveform,
            "emotional_resonance": emotional_resonance or []
        }
        print(f"🎼 Tuned {zone_name} to {frequency_hz}Hz ({waveform}) with emotional overlays: {emotional_resonance or 'None'}")
        pass

    def get_resonance(self, zone_name):
        return self.zone_resonance.get(zone_name, None)

    def apply_resonance_effects(self, zone_name, frequency_hz=None, waveform="sine", emotional_resonance=None):
        profile = self.get_resonance(zone_name)
        if not profile:
            print(f"❓ No resonance profile set for zone: {zone_name}")
            return

        print(f"🔊 Applying resonance to {zone_name} — Frequency: {frequency_hz}Hz, Waveform: {waveform}, Emotion: {emotional_resonance}")
        if profile['emotional_resonance']:
            print(f"💓 Emotional tones: {', '.join(profile['emotional_resonance'])}")
        else:
            print("🎵 No emotional overlay applied.")

    # ---------------------------------------------------------------------
    # Back‑compat alias: world_builder.py calls `tune_environment`, which
    # should behave exactly like `tune_zone`. We expose a thin wrapper so
    # older scripts don't crash.
    # ---------------------------------------------------------------------
    def tune_environment(self, zone_name, frequency, waveform="sine", emotional_resonance=None):
        """
        Alias for `tune_zone` kept for compatibility with earlier code.
        Parameters mirror `tune_zone` but accept `frequency` instead of
        `frequency_hz` to make the call site read nicely.
        """
        # Delegate to the canonical API
        self.tune_zone(
            zone_name=zone_name,
            frequency_hz=frequency,
            waveform=waveform,
            emotional_resonance=emotional_resonance,
        )
