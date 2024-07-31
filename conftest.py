import src.model.summarizer.process.prompt as prompt
from src.model.opinions.opinion import Opinion
from src.model.summarizer.summary import Summary
from datetime import datetime, timedelta

private_key = ""
private_key_id = ""

prompt.init(private_key, private_key_id)

opinions = []
summaries = []
initial_date = datetime.today()

base_opinion = Opinion(venue="LoDeCarlitos", date=datetime.today(), opinion="", reservation="")

opinions = list(
        map(
            lambda op: Opinion(venue="LoDeCarlitos", date=datetime.today(), opinion=op, reservation=""),
            opinions
            )
        )

for index, opinion in enumerate(opinions):
    opinion.date = initial_date - timedelta(days=index)

result = prompt.create_prompt(opinions, summaries)
