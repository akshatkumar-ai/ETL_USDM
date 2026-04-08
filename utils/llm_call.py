from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
key = os.environ["GROQ_API_KEY"]


def llm_call(prompt):
  client = Groq(api_key=key)
  completion = client.chat.completions.create(
      model="llama-3.1-8b-instant",
      messages=[
        {
          "role": "user",
          "content": prompt
        }
      ],
      temperature=1,
      max_completion_tokens=1024,
      top_p=1,
      stream=True,
      stop=None
  )
  full_content = ""
  for chunk in completion:
      if chunk.choices[0].delta.content:
          full_content += chunk.choices[0].delta.content
  return full_content


# print(llm_call("What is 2+2?", key))