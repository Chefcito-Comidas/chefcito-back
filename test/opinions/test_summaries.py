import asyncio
from datetime import datetime, timedelta
from typing import List
from src.model.opinions.data.base import MockedOpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.provider import LocalOpinionsProvider, OpinionsProvider
from src.model.summarizer.process.algorithm import SummaryAlgorithm
from src.model.summarizer.service import LocalSummarizerProvider


def generate_same_text_opinions(
                                total: int, 
                                venue: str, 
                                opinion: str = "Some opinion text"
                                ) -> List[Opinion]:
    opinions = []
    for _ in range(total):
        opinions.append(
                Opinion(
                    venue=venue,
                    opinion=opinion,
                    date=datetime.today(),
                    reservation="SomeInvalidReservation"
                    )
                )
    return opinions

def test_summary_text_has_all_opinions():
    db = MockedOpinionsDB()
    summarizer = LocalSummarizerProvider(db, SummaryAlgorithm())
    opinions = LocalOpinionsProvider(db, summarizer)
    generic_opinion = "Opinion generica"
    for opinion in generate_same_text_opinions(10, "Lo de Carlitos", generic_opinion):
        asyncio.run(opinions.create_opinion(opinion))
    
    summary = asyncio.run(
            summarizer.create_summary("Lo de Carlitos", since=datetime.today() - timedelta(days=1))
            )

    assert summary.text == generic_opinion * 10

def test_summary_algorithm_generates_correct_query():
    summary_algo = SummaryAlgorithm()
    from_date = datetime.today() - timedelta(days=14)
    expected_query = OpinionQuery(
            venue="VenueIdPassedToAlgorithm",
            from_date=from_date
            )
    
    generated_query = summary_algo.generate_query("VenueIdPassedToAlgorithm", from_date)

    assert expected_query == generated_query

def test_summary_algorithm_generated_query_for_14_days():
    summary_algo = SummaryAlgorithm()
    since = datetime.today() - timedelta(days=20)
    expected_query = OpinionQuery(
            venue="Chachito's",
            from_date=since,
            to_date=since + timedelta(days=14)
            )
    generated_query = summary_algo.generate_query("Chachito's", since)
    assert expected_query == generated_query

def test_summary_algorithm_generates_a_summary_for_14_days_and_adds_it_to_the_new_one():
    opinions = list(
            map(
                lambda opinion: Opinion(
                        venue=opinion[1].venue,
                        opinion=opinion[1].opinion,
                        date=opinion[1].date - timedelta(days=opinion[0]),
                        reservation=opinion[1].reservation
                    ),
                enumerate(generate_same_text_opinions(20, "Chachito's", "Opinion"))
                )
            )

    db = MockedOpinionsDB()
    for opinion in opinions:
        asyncio.run(db.store(opinion))

    summarizer = SummaryAlgorithm()
    asyncio.run(summarizer.generate(db, venue="Chachito's", since=(datetime.today() - timedelta(days=20))))

    final_list = db.opinions["Chachito's"]['summaries']
    summaries_text = [value.text for value in final_list]
    assert len(final_list) == 2
    assert "Opinion" * 14 in summaries_text
    assert "Opinion" * 20 in summaries_text





