import urllib
from typing import Dict
from requests import Response, get
from bs4 import BeautifulSoup
from requests.api import post

base = "http://boadica.com.br"

KEYS = {"classeprodutox": "classe_produto", "codcategoriax": "cod_categoria"}


def __find_links(page: Response) -> list:
    soup = BeautifulSoup(page.text, "html.parser")
    uls = soup.find_all("ul", class_="list3")
    links = [l.find("a") for l in uls]
    lista = []

    for a in links:
        if a:
            is_category = "precos?" not in a["href"]
            item = {
                "label": a.text,
                "categoria": a["href"].split("/")[2],
            }
            if not is_category:
                params = {
                    KEYS.get(i.split("=")[0].lower(), i.split("=")[0].lower()): i.split(
                        "="
                    )[1]
                    for i in a["href"].split("?")[1].split("&")
                }
                params.update({"categoria": item["categoria"]})
                item.update({"link": urllib.parse.urlencode(params)})
            lista.append(item)

    return lista


def get_loja(id: str) -> dict:
    page = get(f"{base}/detalhe-loja-popup/{id}")
    soup = BeautifulSoup(page.text, "html.parser")
    rows = soup.find_all("div", class_="row")
    row = rows[-2:][0]
    info = row.find_all("p")
    try:
        detalhes = info[2].find_all("span")
    except IndexError:
        return {}

    def __get_or_none(detalhes, index):
        try:
            return detalhes[index].text.strip()
        except IndexError:
            return ""

    return {
        "endereco": __get_or_none(detalhes, 1),
        "bairro": __get_or_none(detalhes, 2),
        "cidade": f"{__get_or_none(detalhes,3)} - {__get_or_none(detalhes,4)}",
        "cep": __get_or_none(detalhes, 5),
    }


def __get_filtros(
    classe_produto: str,
    categoria: str,
    cod_categoria: str,
    xt: str = None,
    xf: str = None,
    xg: str = None,
    xe: str = None,
    xj: str = None,
    id_modelo: str = None,
    id_regiao: str = None,
    em_box: str = None,
    cod_loja: str = None,
    preco_min: str = None,
    preco_max: str = None,
) -> dict:
    uri = f"{base}/pesquisa/{categoria}/filtros?ClasseProdutoX={classe_produto}&CodCategoriaX={cod_categoria}&XT={xt}&XF={xf}&XG={xg}&XE={xe}&XJ={xj}&modelo={id_modelo}&regiao={id_regiao}&em_box={em_box}&cl={cod_loja}&preco_min={preco_min}&preco_max={preco_max}"
    return post(uri).json()


def __find_lista_produtos(
    page: Response,
    classe_produto,
    categoria,
    cod_categoria,
    xt,
    xf,
    xg,
    xe,
    xj,
    id_modelo,
    id_regiao,
    em_box,
    cod_loja,
    preco_min,
    preco_max,
) -> list:
    pagination = [0, 0, 0, 0]
    soup = BeautifulSoup(page.text, "html.parser")
    rows = soup.find_all("div", class_="detalhe")
    if rows:
        pagination = (
            soup.find("div", class_="paginacao").find("p").text.strip().split(" ")
        )
    produtos = []

    def __get_or_none(detalhes, index):
        try:
            return detalhes[index].text.strip()
        except IndexError:
            return ""

    def __get_image(element):
        if element:
            return element.get("data-href", None)
        return None

    for p in rows:
        data = {}

        elements = {
            "nome": p.find("div", class_="produto").find("a").find_all("span")[0],
            "embalagem": __get_or_none(
                p.find("div", class_="produto").find("a").find_all("span"), 1
            ),
            "descricao": p.find("div", class_="especificacao"),
            "imagem": __get_image(p.find("a", class_="modal-foto")),
            "preco": p.find("div", class_="preco"),
            "telefone": p.find("span", {"title": "Telefone"}),
            "whatsapp": p.find("div", {"title": "WhatsApp"}),
            "lojaNome": p.find("a", class_="modal-loja-dotnet"),
            "lojaId": p.find("a", class_="modal-loja-dotnet")["data-codigo"],
            "endereco": p.find("div", class_="popup-loja-mobile").text.split("\n"),
        }

        for k, v in elements.items():
            if v:
                if isinstance(v, str):
                    data.update({k: v.strip()})
                elif isinstance(v, list):
                    data.update({k: [s.strip() for s in v if s.strip()]})
                else:
                    data.update({k: v.text.strip()})

        produtos.append(data)

    return {
        "meta": {
            "filtros": __get_filtros(
                classe_produto,
                categoria,
                cod_categoria,
                xt,
                xf,
                xg,
                xe,
                xj,
                id_modelo,
                id_regiao,
                em_box,
                cod_loja,
                preco_min,
                preco_max,
            ),
            "pagination": {"current": int(pagination[1]), "total": int(pagination[3])},
        },
        "data": produtos,
    }


def get_categories() -> list:
    page = get(f"{base}/")
    return __find_links(page)


def get_subcategories(cat: str) -> list:
    page = get(f"{base}/pesquisa/{cat}")
    return __find_links(page)


def get_sub_page(
    classe_produto: str,
    categoria: str,
    cod_categoria: str,
    page: int = 1,
    xt: str = "",
    xf: str = "",
    xg: str = "",
    xe: str = "",
    xj: str = "",
    id_modelo: str = "",
    id_regiao: str = "",
    em_box: str = "",
    cod_loja: str = "",
    preco_min: str = "",
    preco_max: str = "",
):
    uri = f"{base}/pesquisa/{categoria}/precos?ClasseProdutoX={classe_produto}&CodCategoriaX={cod_categoria}&XT={xt}&XF={xf}&XG={xg}&XE={xe}&XJ={xj}&modelo={id_modelo}&regiao={id_regiao}&em_box={em_box}&cl={cod_loja}&preco_min={preco_min}&preco_max={preco_max}&curpage={page}"
    page = get(uri)

    return __find_lista_produtos(
        page,
        classe_produto,
        categoria,
        cod_categoria,
        xt,
        xf,
        xg,
        xe,
        xj,
        id_modelo,
        id_regiao,
        em_box,
        cod_loja,
        preco_min,
        preco_max,
    )
