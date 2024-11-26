from openai import OpenAI
import json
from Global_Var import G

class AI:
    def get_response(self):
        api_key = ""
        try:
            with open('key.json', 'r', encoding='utf-8') as f:
                api_key = json.load(f)
        except FileNotFoundError:
            print("파일을 찾을 수 없습니다.")
        bot = OpenAI(api_key=api_key['key'])
        content = "json 형식으로 RC Car의 행동 양식을 줄게, 너가 판단해서 잘 이동했는 지 분석해"
        sentense = json.dumps(G.gptdata)
        response = bot.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": content},
                {"role":"user", "content" : sentense}
            ],
            #max_tokens 1~16383
            max_tokens=256,
            #temperature 0 ~ 2
            temperature=1,
            #top_p 0 ~ 1
            top_p=1.0,
            #frequency_penalty 0 ~ 2
            frequency_penalty=0,
            #presence_penalty 0 ~ 2
            presence_penalty=0
        )
        return response.choices[0].message.content
    
Ai = AI()