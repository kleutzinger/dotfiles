#!/usr/bin/env -S uv run --script --with openai
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)

completion = client.chat.completions.create(
    model="kimi-k3",
    messages=[{"role": "user", "content": "What are some cool things i can do as a programmer with LLMs? I have api access and I have a lot of scripts. What can I do?"}],
)

print(completion.choices[0].message.content)
