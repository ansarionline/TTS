import os
import io
import base64
import torch
import soundfile as sf
from . import se_extractor
from .api import BaseSpeakerTTS, ToneColorConverter

device = "cuda:0" if torch.cuda.is_available() else "cpu"
base_ckpt = 'backend/checkpoints/base_speakers/EN'
converter_ckpt = 'backend/checkpoints/converter'

base_speaker_tts = BaseSpeakerTTS(f'{base_ckpt}/config.json', device=device)
base_speaker_tts.load_ckpt(f'{base_ckpt}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{converter_ckpt}/config.json', device=device)
tone_color_converter.load_ckpt(f'{converter_ckpt}/checkpoint.pth')

def generate_voice(
    text: str,
    reference_voice_path: str = '',
    speaker_tone: str = "default",
    speed: float = 1.0,
    language: str = "English",
    clone: bool = False,
    style_tag: str = "@ANSARITTS",
    tmp_dir: str = '.data/tmp',
    filename: str = 'asdf'
) -> str:
    os.makedirs(tmp_dir, exist_ok=True)
    tts_path = os.path.join(tmp_dir, filename)
    audio = base_speaker_tts.tts(
                        text, tts_path, speaker=speaker_tone, 
                        language=language, speed=speed)
    if clone:
        final_path = os.path.join(tmp_dir, "final_output.wav")
        source_se = torch.load(f'{base_ckpt}/en_default_se.pth').to(device)
        target_se, _ = se_extractor.get_se(reference_voice_path, tone_color_converter, target_dir=tmp_dir, vad=True)
        tone_color_converter.convert(
            audio_src_path=tts_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=final_path,
            message=style_tag
        )
        result_path = final_path
    else:
        result_path = tts_path
    audio_data, sr = sf.read(result_path)
    with io.BytesIO() as buf:
        sf.write(buf, audio_data, sr, format='WAV')
        audio_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return audio_base64