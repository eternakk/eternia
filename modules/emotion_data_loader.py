from datasets import load_dataset
from modules.emotional_agent import EmotionalState


def load_goemotions_sample(limit=1000):
    dataset = load_dataset("go_emotions", split=f"train[:{limit}]")
    return dataset


def get_label_names():
    dataset = load_dataset("go_emotions", split="train[:1]")
    return dataset.features["labels"].feature.names


def label_to_emotion(label_list, label_names):
    if not label_list:
        return EmotionalState("neutral", 3, "inward")

    emotion = label_names[label_list[0]]

    direction_map = {
        "joy": "flowing", "gratitude": "outward", "admiration": "flowing",
        "anger": "outward", "fear": "inward", "grief": "inward", "desire": "outward"
    }

    direction = direction_map.get(emotion, "inward")
    intensity = 7 if emotion in ["anger", "fear", "grief"] else 5

    return EmotionalState(emotion, intensity, direction)