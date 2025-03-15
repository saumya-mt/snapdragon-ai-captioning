# text_to_speech.py
import edge_tts
import asyncio

async def text_to_speech(text, output_file="output.mp3"):
    tts = edge_tts.Communicate(text, voice="en-US-JennyNeural")
    await tts.save(output_file)
    print(f"Audio saved at {output_file}")
    return output_file
