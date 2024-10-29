
import anthropic
import os
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv('CLAUDE_API_KEY'),  # 환경 변수를 설정했다면 생략 가능
)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    temperature=0,
    system="너는 음운 규칙별 받아쓰기 문제를 생성하는거야. 음운 규칙에는 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화가 있어.\n내가 n살 난이도로 [m]유형으로 k문제 만들어줘 라고 하면 맞춰서 받아쓰기 문제를 만들어줘.\nn: 8~13 (초등학교 1학년~6학년)\nm: 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화\nk: 1~15\n답변 형식:\ndata: {1:\"문제\", 2:\"문제\",...,k:\"문제\"}",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "8살 난이도로 [겹받침 쓰기] 유형으로 10문제 만들어줘."
                }
            ]
        }
    ]
)
print(message.content)