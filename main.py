from fastapi import FastAPI
from pydantic import BaseModel
from scrapper import get_categories, get_subcategories, get_sub_page, get_loja

app = FastAPI()


class ListParams(BaseModel):
    classe_produto: str
    cod_categoria: str
    categoria: str
    xt: str = ""
    xf: str = ""
    page: int = 1
    id_modelo: str = ""
    id_regiao: str = ""
    em_box: str = ""
    cod_loja: str = ""
    preco_min: str = ""
    preco_max: str = ""


@app.get("/")
async def index():
    return get_categories()


@app.get("/cat/{category}")
async def index(category: str):
    return get_subcategories(category)


@app.post("/lista/")
async def list_prod(params: ListParams):
    return get_sub_page(**params.dict())


@app.get("/loja/{id}")
async def list_prod(id: int):
    return get_loja(id)
