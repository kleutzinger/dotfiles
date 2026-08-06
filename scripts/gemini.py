#!/usr/bin/env -S uv run --script --with openai
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

completion = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "What are some cool things i can do as a programmer with LLMs? I have api access and I have a lot of scripts. What can I do?"}],
)

print(completion.choices[0].message.content)
