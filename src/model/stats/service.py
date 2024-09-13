from fastapi import HTTPException, status
from src.model.reservations.reservation import Reservation
from src.model.stats.provider import StatsProvider
from src.model.stats.stats_update import StatsUpdate
from src.model.stats.user_data import UserStatData
from src.model.stats.venue_data import VenueStatData


class StatsService():

    def __init__(self, provider: StatsProvider):
        self.provider = provider

    async def update(self, reservation: Reservation) -> None:
        try:
            update = StatsUpdate.from_reservation(reservation)
            await self.provider.update(update)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user data: {e.__str__()}"
            )
    
    async def get_user(self, user: str) -> UserStatData:
        try:
            return await self.provider.get_user(user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to recover user data: {e.__str__()}"
            )
        
    async def get_venue(self, venue: str) -> VenueStatData:
        try:
            return await self.provider.get_venue(venue)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to recover venue data: {e.__str__()}"
            )