import src.model.summarizer.process.prompt as prompt
from src.model.opinions.opinion import Opinion
from src.model.summarizer.summary import Summary
from datetime import datetime, timedelta

private_key = ""
private_key_id = ""

prompt.init(private_key, private_key_id)

opinions = ["Muy buen lugar, luminoso y espacioso. Quiza un poco caro",
            "Una lastima que los baños esten tan sucios, por que la comida es excelente",
            "De la mejor atencion que e tenido en mucho tiempo.",
            "Nada mejor que el pollo a la plancha",
            "Es increiblemente caro para lo que ofrece el lugar",
            "Precios accesibles y comida rica, lo mejor es la atencion que le dan a uno"]
summaries = [Summary(
        venue="LoDeCarlitos",
        date=datetime.today() - timedelta(days=14),
        text="El lugar deberia mejorar su atencion, muchos clientes se quejan del mozo con bigote. Sin embargo, la comida es de calidad y los baños se encuentran limpios"
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
