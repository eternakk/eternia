from modules.emotion_data_loader import load_goemotions_sample, get_label_names, label_to_emotion
from modules.emotional_agent import EmotionProcessor

dataset = load_goemotions_sample()
label_names = get_label_names()

sample = dataset[0]
emotion_obj = label_to_emotion(sample["labels"], label_names)

agent = EmotionProcessor()
input_tensor = emotion_obj.to_tensor()
impact_score = agent(input_tensor)

print(f"💥 Emotion: {emotion_obj.name}, Score: {impact_score.item():.2f}")