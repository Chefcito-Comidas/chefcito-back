from datetime import datetime, timedelta,timezone

from typing import List

from src.model.commons.logger import Logger
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion_query import OpinionQuery
from src.model.summarizer.summary import Summary
from src.model.opinions.opinion import Opinion
import src.model.summarizer.process.prompt as prompt


class Summarizer:
    async def summarize(self, since: datetime, venue: str, opinions: List[Opinion], summaries: List[Summary]) -> Summary:
       raise Exception("Interface method should not be called") 

class MockSummarizer(Summarizer):
    
    async def summarize(self, since: datetime, venue: str, opinions: List[Opinion], summaries: List[Summary]) -> Summary:
        text = ""
        for opinion in opinions:
            text += opinion.opinion
        for summary in summaries:
            text += summary.text
        
        return Summary(
                date = since + timedelta(days=14),
                text = text,
                venue = venue
                )

class VertexSummarizer(Summarizer):
    

    async def summarize(self, since: datetime, venue: str, opinions: List[Opinion], summaries: List[Summary]) -> Summary:
        
        summary: str = await prompt.create_prompt(opinions, summaries)
        return Summary(
                date = since + timedelta(days=14),
                text = summary,
                venue = venue
                )

class SummaryAlgorithm:

    def __init__(self, summarizer: Summarizer = MockSummarizer()):
        self.summarizer = summarizer

    def __get_min_date(self) -> datetime:
        """
            Returns a datetime 14 days ago
        """
        min = datetime.now() - timedelta(days=14)
        return min.replace(tzinfo=timezone.utc)

    def __is_too_past(self, some_date: datetime) -> bool:
        """
            Returns True if the date passed is older than 14 days ago (+- 12 hours)
        """
        max_diff = timedelta(hours=12)
        Logger.info(f"{some_date} vs {self.__get_min_date()}")
        diff = some_date - self.__get_min_date()
        return max_diff <= abs(diff) and diff <= timedelta(hours=12)

    def generate_query(self, venue: str, since: datetime) -> OpinionQuery:
        """
            Generates a query for the database to get the values needed
        """
        to_date=None
        if self.__is_too_past(since):
            to_date = since + timedelta(days=14)

        return OpinionQuery(
                venue=venue,
                from_date=since,
                to_date=to_date
                )
    
    async def get_older_summaries(self, db: OpinionsDB, venue: str, since: datetime) -> List[Summary]:
        return await db.get_summaries(venue, since)

    async def generate(self, db: OpinionsDB, venue: str, since: datetime) -> Summary:
        """
            Generates summaries from since to today (may generate more than one summary)
        """
        query = self.generate_query(venue, since)
        Logger.info("Generated query to create summary")
        summaries = await self.get_older_summaries(db, venue, since)
        opinions = await db.get(query)
        Logger.info("Got all the information to create the summary") 
        summary = await self.summarizer.summarize(since, venue, opinions.result, summaries) 
        Logger.info(f"Generated summary: {summary}")
        await db.store_summary(summary)
        if query.to_date:
            return await self.generate(db, venue, query.to_date)
        
        return summary
