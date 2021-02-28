from typing import List

from fastapi import APIRouter, Depends, status
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app import models, schemas
from app.deps import get_db


router = APIRouter()


@router.get("/decks/", response_model=schemas.Decks)
async def list_decks(db: AsyncSession = Depends(get_db)):
    objects = await models.Deck.all(db)
    return schemas.Decks(decks=parse_obj_as(List[schemas.Deck], objects))


@router.get("/decks/{deck_id}/", response_model=schemas.Deck)
async def get_deck(deck_id: int, db: AsyncSession = Depends(get_db)):
    instance = await models.Deck.get_by_id(db, deck_id)
    return schemas.Deck.from_orm(instance)


@router.put("/decks/{deck_id}/", response_model=schemas.Deck)
async def update_deck(
    deck_id: int, data: schemas.DeckCreate, db: AsyncSession = Depends(get_db)
):
    instance = await models.Deck.get_by_id(db, deck_id)
    await instance.update(db, **data.dict())
    return schemas.Deck.from_orm(instance)


@router.post("/decks/", response_model=schemas.Deck)
async def create_deck(
    data: schemas.DeckCreate, db: AsyncSession = Depends(get_db)
):
    instance = models.Deck(**data.dict())
    await instance.save(db)
    return schemas.Deck.from_orm(instance)


@router.get("/decks/{deck_id}/cards/", response_model=schemas.Cards)
async def list_cards(deck_id: int, db: AsyncSession = Depends(get_db)):
    objects = await models.Card.filter(db, [models.Card.deck_id == deck_id])
    return schemas.Cards(cards=parse_obj_as(List[schemas.Card], objects))


@router.get("/cards/{card_id}/", response_model=schemas.Card)
async def get_card(card_id: int, db: AsyncSession = Depends(get_db)):
    instance = await models.Card.get_by_id(db, card_id)
    return schemas.Card.from_orm(instance)


@router.post("/decks/{deck_id}/cards/", status_code=status.HTTP_204_NO_CONTENT)
async def create_cards(
    deck_id: int,
    data: List[schemas.CardCreate],
    db: AsyncSession = Depends(get_db),
):
    await models.Card.bulk_create(
        db,
        [models.Card(**card.dict(), deck_id=deck_id) for card in data],
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/decks/{deck_id}/cards/", status_code=status.HTTP_204_NO_CONTENT)
async def update_cards(
    deck_id: int,
    data: List[schemas.Card],
    db: AsyncSession = Depends(get_db),
):
    await models.Card.bulk_update(
        db,
        [
            models.Card(**card.dict(exclude={"deck_id"}), deck_id=deck_id)
            for card in data
        ],
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
