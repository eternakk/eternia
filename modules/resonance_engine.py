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

    def get_resonance(self, zone_name):
        return self.zone_resonance.get(zone_name, None)

    def apply_resonance_effects(self, zone_name):
        profile = self.get_resonance(zone_name)
        if not profile:
            print(f"❓ No resonance profile set for zone: {zone_name}")
            return

        print(f"🔊 Applying Resonance to {zone_name}: {profile['frequency_hz']}Hz {profile['waveform']}")
        if profile['emotional_resonance']:
            print(f"💓 Emotional tones: {', '.join(profile['emotional_resonance'])}")
        else:
            print("🎵 No emotional overlay applied.")
