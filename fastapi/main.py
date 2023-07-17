from fastapi import FastAPI
import uvicorn
from typing import List, Union
from pydantic import BaseModel

class CategoryInput(BaseModel):
    genres: Union[List[str], None]
    instruments: Union[List[str], None]
    moods: Union[List[str], None]
    etc: Union[List[str], None]
    duration: int
    tempo: str

class TextInput(BaseModel):
    genre: List[str]
    instrument: List[str]
    mood: List[str]
    etc: List[str]
    text: str
    time: int
    tempo: str


app = FastAPI()
    

@app.get("/")
def test():
    print("hello~")


@app.post("/choice_category")
def choice_category(inputs: CategoryInput):
    print(inputs)
    return {"message": "test"}


@app.post("/text_analysis")
def text_analysis(inputs: TextInput):
    print(inputs)
    return {"message": "test"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)