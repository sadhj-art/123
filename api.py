import os
import requests
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
# 从环境变量中获取API密钥和基础URL
api_key = ("sk-MDVCXWtAxKYFTI92KUOdlL3dP4oQ00uYfC6HghLEgfsIUMOL")
base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")

# 初始化OpenAI客户端
from openai import OpenAI
client = OpenAI(api_key=api_key, base_url=base_url)

# 定义API接口和消息处理逻辑
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system_message = "现在请你扮演一温柔善良，体贴，热心的虚拟女友聊天伴侣，需要陪我不断的聊天，提供情绪价值，回答的话语需要简短干练一点。"

class ChatParams(BaseModel):
    message: str

# 全局变量，用于存储会话消息
messages = [{"role": "system", "content": system_message}]

@app.post("/chat_with_kimi")
async def chat_with_kimi(params: ChatParams):
    global messages
    messages.append({"role": "user", "content": params.message})

    # 保持消息条数不超过5条，但始终保留system消息
    if len(messages) > 5:
        messages = [messages[0]] + messages[-4:]

    # 调用OpenAI API获取回复
    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",  # 可以根据需要选择模型
            messages=messages,
            temperature=0.3,  # 可以根据需要调整温度参数
        )
        kimi_reply = completion.choices[0].message.content

        # 将AI回复加入会话列表
        messages.append({"role": "assistant", "content": kimi_reply})

        # 返回AI的回复
        return {"message": kimi_reply}
    except Exception as e:
        # 处理API调用失败的情况
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    # 运行FastAPI服务器
    uvicorn.run(app, host="0.0.0.0", port=8888)
