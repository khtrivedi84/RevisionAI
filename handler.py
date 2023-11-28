import runpod

import os
import subprocess
from typing import Optional, List, Dict, Any
import time
import psutil
import GPUtil
from pytube import YouTube
import matplotlib.pyplot as plt
import whisper
from whisperx import load_align_model, align
from whisperx.diarize import DiarizationPipeline, assign_word_speakers
import gc
import json
import pandas as pd
import requests 

def handler(job):

    job_input = job["input"]
    public_ip = job_input["public_ip"]
    port = job_input["port"]
    course_name = job_input["course_name"]
    user_email = job_input["user_email"]
    lecture_number = job_input["lecture_number"]
    file_name = job_input["file_name"]


    final_url = f"http://{public_ip}:{port}/download?courseName={course_name}&userEmail={user_email}&lectureNumber={lecture_number}&filename={file_name}"

    response_file = requests.get(f"http://{public_ip}:{port}/download?courseName={course_name}&userEmail={user_email}&lectureNumber={lecture_number}&filename={file_name}")
    if response_file.status_code == 200:
        with open('audio.wav', "wb") as file:
            file.write(response_file.content)
    else:
        return {"result": "File save failed!!", "final_url": final_url}

    filename = '/audio.wav'

    
    import whisperx
    device = "cuda" 
    my_audio_file = filename
    # return {"result": my_audio_file, "result_array": result_array}
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)
    
    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    audio = whisperx.load_audio(my_audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    
    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model
    
    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    
    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model_a
    
    # 3. Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token="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", device=device)
    
    # add min/max number of speakers if known
    diarize_segments = diarize_model(my_audio_file)
    # diarize_model(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)
    
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return {"result": result }

runpod.serverless.start({"handler": handler})
