import src.model.summarizer.process.prompt as prompt
from src.model.opinions.opinion import Opinion
from src.model.summarizer.summary import Summary
from datetime import datetime, timedelta

private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCPCIXAKZsC3akG\nA2FsCuNERVf/3A69c+y1mrm84L0EV/xh86+N4v2Ep1caZWEFExDkX1hI93dBQfys\nXPR5RLCzHqo+YzzEx0aoOquiZYlwkrubkt0jgP8qCz/e3bcvYRXmTGO3yzF8jy89\n7+XWF2iYgnF6nPIYmK07QL+AXSrXtRkN2JJA5UKuNWRzskGIo7ETJhVPhtuYvJW6\nY+Sct0f89TtPTTmCNK2lZZOduxRoQOlfpxQpVxj7M54Z2MCuhGncsHisBEmIi8e3\nB81V8svLvcu/u37woLDxHAO36CeHU+8Bwz9uuSVZaI3ouvY0kpvYAZ5WVRiIghfL\nQaHK6EXbAgMBAAECggEANsn88e7+AcsGw9bnqotBIxWs78VLoCaXtbjfDQrJXLCX\nbK37wU4B7p5rLyFGWLtE7TXYi5q/g6/TKfMxcoJtbS+B5wP8cyQiXK6csEhUrVqH\nosBPFRqEo4ZLoQMs+GkoCl+Ykv6yphPy9LbAQ5IT7teIwH79/Y3+TYQv1uvZTWbu\n00GPGHk5c/YSXOHL5G2uuA1vlGKj13JOGmQBvIJhjBLNnS7r+jGPTlPiTf+xCd9A\nY76PJzZoABayhGlAbNFBx6kGYQngd48/cUXegk9SGvMfgljZDuaVQTt9ABREel4J\naObOoGOgXbojSBrYygYnPDTCn/E8mS028wiJP1AKAQKBgQDF6LMFeOM5oqOUOW24\n+u456/+DreeUJMgI0yRch5c112aCqNM4af3nIVowdJOwlYEBH4Aco6xvvlVvXDtw\nidgBLEWBd1OHwU49Asc3q97E2GeYXT/TeGtz0XURJGCDIF+LNuWBdf/P9K4ShGD6\ntx2N4PzsHg/wCZ+tITOuk/ypEQKBgQC5BFjr9xOjGR3nh5BQXNN0e97c/kZvfN3Q\nfFslM5gtaQ/YoUpuUdXCw6UUK+hBoADnZ3wbhZwl06RlnNy7xI3pft6qvmVccMSR\nY27stYWK199QC5iYoIMv/bT/WRruKjunG3czNgyzhhHDUr/JL82jZYTz7QNwgbil\nZlkKyvngKwKBgBpKWU3Gy1iitFxCbMMAApmLMjxJ49OYN0KE2fW4xWuPm7yLtNNv\nsRz9H0AEnIH+uk5t4tTrIUMO48aRWAwRI7K0MN+L/HqyQTR1pAVPPZ6kqM5ixNHQ\n02VlU8ndLTz+FfMmbcKO7FaxyFYJY+CqZrCsTK0JKVDX1nBnUrhETHIhAoGAN7a2\nbEAX2rpahfkNnRWG24Hdp6CuZy4rwXdhHv+9aJdFnU9ckYH1I9Q0ZrGeG/zpqMVB\n2yvNzJpB3BNzaNuUfGam+LWi4kZW+wz9PyyeTSQabAlB51wWhSIaGfakJGn1Uqnz\nqCkzg+/wc2f8tsG9Y+HTOnz51yxJBQ2f7J8YxccCgYBDLy24aq2i/3kxStwZTMnD\nsjrXvy70IWxxY6BF38Sk/g1k4gJwjd1lbviu5IPw6d8/GJDOqwcspBM8TerWtY9J\n8XM1DeNiM/rHRM+lyEyrImN4Eeae18AqCQ2dZJs5JNOoKldKBvktbFHdIf0kH7Gv\nc8thmkD8HLon0DYj1j60pQ==\n-----END PRIVATE KEY-----\n"
private_key_id = "a25b80a7ec98ef96b3b22ed36a91c05068d11ff3"

prompt.init(private_key, private_key_id)

opinions = ["Muy buen lugar, luminoso y espacioso. Bastante caro para la calidad de la comida",
            "Una lastima que los baños esten tan sucios y la comida, menos el pollo, deja mucho que desear",
            "De la mejor atencion que e tenido en mucho tiempo.",
            "Nada mejor que el pollo a la plancha, lastima que sea tan caro",
            "Es increiblemente barato para lo que ofrece el lugar",
            "Precios accesibles y comida rica, lo mejor es la atencion que le dan a uno"]
summaries = [Summary(
        venue="LoDeCarlitos",
        date=datetime.today() - timedelta(days=14),
        text="El lugar deberia mejorar su atencion, muchos clientes se quejan del mozo pelado. Sin embargo, la comida es de calidad y los baños se encuentran limpios"
    ),
             Summary(
                 venue="LoDeCarlitos",
                 date=datetime.today() - timedelta(days=28),
                 text="El lugar es caro y eso no se refleja en la calidad de la comida, un mozo con bigote suele molestar a los clientes. Los baños y la atencion del resto de los mozos es destacable."
                 )]
initial_date = datetime.today()


opinions = list(
        map(
            lambda op: Opinion(venue="LoDeCarlitos", date=datetime.today(), opinion=op, reservation=""),
            opinions
            )
        )

for index, opinion in enumerate(opinions):
    opinion.date = initial_date - timedelta(days=index)

result = prompt.create_prompt(opinions, summaries)['output_text']

print(result)
