import os

from openai import OpenAI


class RAGChat:
    def __init__(self) -> None:
        self.client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), #If you have not configured environment variables, replace them with your API Key here
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", #Enter the base_url for the DashScope SDK
    )
    def chat(self,messages):
        query = messages[-1].get("content")
        query_emb = ''

        completion = self.client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=False
        )
        result = completion.choices[0].message.content
        print(result)
        return result