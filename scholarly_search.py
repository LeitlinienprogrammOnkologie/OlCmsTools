from scholarly import ProxyGenerator
from scholarly import scholarly

pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

search_query = scholarly.search_pubs("S3-Leitlinie Analrandkarzinom")
pass