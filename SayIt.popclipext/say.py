#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Say it. - PopClip Extension
Say the selected text aloud using ByteDance TTS API.
"""

import os
import json
import base64
import uuid
import tempfile
import subprocess
import urllib.request

# Get the selected text and options from PopClip
text = os.environ.get("POPCLIP_TEXT", "我是一个中国人，哈哈哈哈。")
api_key = os.environ.get("POPCLIP_OPTION_API_KEY", "")
resource_id = "seed-tts-2.0"
speaker = os.environ.get("POPCLIP_OPTION_SPEAKER", "zh_female_xiaohe_uranus_bigtts")

# API endpoint
url = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

# Request payload
payload = {
    "req_params": {
        "text": text,
        "speaker": speaker,
        "additions": json.dumps({
            "disable_markdown_filter": True,
            "enable_language_detector": True,
            "enable_latex_tn": True,
            "disable_default_bit_rate": True,
            "max_length_to_filter_parenthesis": 0,
            "cache_config": {"text_type": 1, "use_cache": True}
        }),
        "audio_params": {
            "format": "mp3",
            "sample_rate": 24000
        }
    }
}

# Build request
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("x-api-key", api_key)
req.add_header("X-Api-Resource-Id", resource_id)
req.add_header("X-Api-Request-Id", str(uuid.uuid4()))
req.add_header("Connection", "keep-alive")

# Send request and parse streaming response
response = urllib.request.urlopen(req)

# Read line-delimited JSON and collect audio data
audio_chunks = []
for line in response:
    line = line.decode("utf-8").strip()
    if line:
        result = json.loads(line)
        if result.get("code") == 0 and result.get("data"):
            audio_chunks.append(base64.b64decode(result["data"]))

# Combine all audio chunks
audio_data = b"".join(audio_chunks)

# Save to temp file and play
with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
    f.write(audio_data)
    temp_path = f.name

subprocess.run(["afplay", temp_path])
os.unlink(temp_path)
