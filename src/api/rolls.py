from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, or_, and_, text
import datetime

from src.api.dependencies import SessionDep
from src.models.rolls import RollModel
from src.schemas.rolls import NewRollSchema, RollsSchema, FilterRollsSchema, SelectRollsSchema, SelectSchema

router = APIRouter()

@router.post("/rolls", tags=['Рулоны'], summary="Добавить рулон")
async def add_roll(roll: NewRollSchema, session: SessionDep) -> RollsSchema:
    new_roll = RollModel(
        length=roll.length,
        weight=roll.weight,
        date_create=datetime.date.today(),
        date_delete=None
    )
    session.add(new_roll)
    await session.flush()
    await session.commit()
    return new_roll

@router.post("/filter_roll", tags=['Рулоны'], summary="Фильтрация рулонов") #Используется post, а не get, т.к. свагер не может работать с телом в get
async def filter_roll(filter: FilterRollsSchema, session: SessionDep) -> list[RollsSchema]:
    if filter.date_delete_is_null != None and filter.date_delete_more != None:
        raise HTTPException(status_code=400, detail="Поле date_delete_is_null не может одновременно использоваться с другими фильтрами даты удаления")
    elif filter.date_delete_is_null != None and filter.date_delete_less != None:
        raise HTTPException(status_code=400, detail="Поле date_delete_is_null не может одновременно использоваться с другими фильтрами даты удаления")
    else:
        query = select(RollModel)

        if filter.id_more != None:
            query = query.filter(RollModel.id >= filter.id_more)
        if filter.id_less != None:
            query = query.filter(RollModel.id <= filter.id_less)
        if filter.length_more != None:
            query = query.filter(RollModel.length >= filter.length_more)
        if filter.length_less != None:
            query = query.filter(RollModel.length <= filter.length_less)
        if filter.weight_more != None:
            query = query.filter(RollModel.weight >= filter.weight_more)
        if filter.weight_less != None:
            query = query.filter(RollModel.weight <= filter.weight_less)
        if filter.date_create_more != None:
            query = query.filter(RollModel.date_create >= filter.date_create_more)
        if filter.date_create_less != None:
            query = query.filter(RollModel.date_create <= filter.date_create_less)
        if filter.date_delete_more != None:
            query = query.filter(RollModel.date_delete >= filter.date_delete_more)
        if filter.date_delete_less != None:
            query = query.filter(RollModel.date_delete <= filter.date_delete_less)
        if filter.date_delete_is_null == True:
            query = query.filter(RollModel.date_delete == None)
        if filter.date_delete_is_null == False:
            query = query.filter(RollModel.date_delete != None)

        result = await session.execute(query)
        rolls = result.scalars().all()
        if len(rolls) == 0:
            raise HTTPException(status_code=404, detail="Нет рулонов, удовлетворяющих условиям")
        else:
            return rolls

@router.post("/select_roll", tags=['Рулоны'], summary="Статистика по рулонам")
async def select_roll(filter: SelectRollsSchema, session: SessionDep) -> SelectSchema:
    query_car = select(func.count(RollModel.id)).where(RollModel.date_create >= filter.date_more, RollModel.date_create <= filter.date_less)
    query_cdr = select(func.count(RollModel.id)).where(RollModel.date_delete >= filter.date_more, RollModel.date_delete <= filter.date_less)

    # можно было также получить выборку всех рулонов одним запросом и дальше обработать внутри роутера
    query_alr = select(func.avg(RollModel.length)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_awr = select(func.avg(RollModel.weight)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_maxlr = select(func.max(RollModel.length)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_minlr = select(func.min(RollModel.length)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_maxwr = select(func.max(RollModel.weight)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_minwr = select(func.min(RollModel.weight)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_sumwr = select(func.sum(RollModel.weight)).where(or_(and_(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more), and_(RollModel.date_create <= filter.date_less, RollModel.date_delete == None)))
    query_maxdel = select(func.max(func.julianday(RollModel.date_delete) - func.julianday(RollModel.date_create))).where(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more)
    query_mindel = select(func.min(func.julianday(RollModel.date_delete) - func.julianday(RollModel.date_create))).where(RollModel.date_create <= filter.date_less, RollModel.date_delete >= filter.date_more)

    query_day_count = text(f"""WITH RECURSIVE date_series AS (SELECT date('{filter.date_more}') AS date UNION ALL SELECT date(date, '+1 day') FROM date_series WHERE date < date('{filter.date_less}'))
    SELECT ds.date, COUNT(r.id) AS roll_count FROM date_series ds LEFT JOIN rolls r ON r.date_create <= ds.date AND (r.date_delete > ds.date OR r.date_delete IS NULL) GROUP BY ds.date ORDER BY ds.date""")
    query_day_weight = text(f"""WITH RECURSIVE date_series AS (SELECT date('{filter.date_more}') AS date UNION ALL SELECT date(date, '+1 day') FROM date_series WHERE date < date('{filter.date_less}'))
    SELECT ds.date, COALESCE(SUM(r.weight), 0) AS rolls_weight FROM date_series ds LEFT JOIN rolls r ON r.date_create <= ds.date AND (r.date_delete > ds.date OR r.date_delete IS NULL) GROUP BY ds.date ORDER BY ds.date""")

    result_car = await session.execute(query_car)
    result_cdr = await session.execute(query_cdr)
    result_alr = await session.execute(query_alr)
    result_awr = await session.execute(query_awr)
    result_maxlr = await session.execute(query_maxlr)
    result_minlr = await session.execute(query_minlr)
    result_maxwr = await session.execute(query_maxwr)
    result_minwr = await session.execute(query_minwr)
    result_sumwr = await session.execute(query_sumwr)
    result_maxdel = await session.execute(query_maxdel)
    result_mindel = await session.execute(query_mindel)

    result_c = await session.execute(query_day_count)
    result_w = await session.execute(query_day_weight)

    rolls_car = result_car.scalars().all()
    rolls_cdr = result_cdr.scalars().all()
    rolls_alr = result_alr.scalars().all()
    rolls_awr = result_awr.scalars().all()
    rolls_maxlr = result_maxlr.scalars().all()
    rolls_minlr = result_minlr.scalars().all()
    rolls_maxwr = result_maxwr.scalars().all()
    rolls_minwr = result_minwr.scalars().all()
    rolls_sumwr = result_sumwr.scalars().all()
    rolls_maxdel = result_maxdel.scalars().all()
    rolls_mindel = result_mindel.scalars().all()



    rolls_c = result_c.fetchall()
    min_day_c, min_count_c = min(rolls_c, key=lambda x: x[1])
    max_day_c, max_count_c = max(rolls_c, key=lambda x: x[1])
    rolls_w = result_w.fetchall()
    min_day_w, min_count_w = min(rolls_w, key=lambda x: x[1])
    max_day_w, max_count_w = max(rolls_w, key=lambda x: x[1])


    if rolls_alr[0] != None:
        return {"count_add_rolls": rolls_car[0],
                "count_delete_rolls": rolls_cdr[0],
                "avg_lenght": rolls_alr[0],
                "avg_weight": rolls_awr[0],
                "max_lenght": rolls_maxlr[0],
                "min_lenght": rolls_minlr[0],
                "max_weight": rolls_maxwr[0],
                "min_weight": rolls_minwr[0],
                "sum_weight": rolls_sumwr[0],
                "max_day_delay": rolls_maxdel[0],
                "min_day_delay": rolls_mindel[0],
                "max_count_day": max_day_c,
                "min_count_day": min_day_c,
                "max_weight_day": max_day_w,
                "min_weigth_day": min_day_w}
    else:
        raise HTTPException(status_code=404, detail="Нет рулонов, удовлетворяющих условиям")


@router.get("/rolls", tags=['Рулоны'], summary="Получить все рулоны")
async def get_rolls(session: SessionDep) -> list[RollsSchema]:
    query = select(RollModel)
    result = await session.execute(query)
    rolls = result.scalars().all()
    if len(rolls) == 0:
        raise HTTPException(status_code=404, detail="В БД нет рулонов")
    else:
        return rolls

@router.get("/rolls/{roll_id}", tags=['Рулоны'], summary="Получить рулон по id")
async def get_roll(roll_id: int, session: SessionDep) -> RollsSchema:
    roll = await session.get(RollModel, roll_id)
    if roll != None:
        return roll
    raise HTTPException(status_code=404, detail="Рулон не найден")


@router.put("/delete/{roll_id}", tags=['Рулоны'], summary="Удалить рулон по id")
async def delete_roll(roll_id: int, session: SessionDep):
    roll = await session.get(RollModel, roll_id)
    if roll != None and roll.date_delete == None:
        roll.date_delete = datetime.date.today()
        await session.commit()
        return roll
    raise HTTPException(status_code=404, detail="Рулон не найден или был удален ранее")

