from fastapi import FastAPI
import uvicorn
from dfatest import DFA
app = FastAPI() # 创建API实例

dfa = DFA(2)
@app.post("/ins_moderation_query",description='query检测')
async def ins_moderation_query(params: dict):
    query = params.get("query","")
    result = dfa.add(query)
    return {"message": result}

@app.post("/update_data",description='query检测')
async def update_data():
    DFA(4)
    return {"message": "update success!"}


if __name__== '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8188)