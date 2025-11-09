import asyncio
from edge_tts import Communicate, VoicesManager

async def list_and_test_voices():
    """List available voices and test TTS with a valid voice."""
    text = "Breathe easy. Take one small step today."
    output_path = "test_output.wav"

    # List available voices
    voices_manager = await VoicesManager.create()
    voices = voices_manager.voices

    print("Available voices:")
    for voice in voices[:10]:  # Print the first 10 voices for brevity
        print(f"Name: {voice['Name']}, Gender: {voice['Gender']}, Locale: {voice['Locale']}")

    # Select a valid voice (e.g., af-ZA-AdriNeural)
    valid_voice = "af-ZA-AdriNeural"  # Replace with a valid voice from the list

    try:
        print(f"\nTesting EdgeTTS with voice: {valid_voice}")
        communicate = Communicate(text=text, voice=valid_voice)
        await communicate.save(output_path)
        print(f"Audio generated successfully! File saved at: {output_path}")
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the function
asyncio.run(list_and_test_voices())