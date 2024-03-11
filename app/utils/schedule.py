from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from pytz import timezone


hour_to_time_index = {
    "8:00": 0, "8:30": 1, "9:00": 2, "9:30": 3, "10:00": 4, "10:30": 5, "11:00": 6, "11:30": 7,
    "12:00": 8, "12:30": 9, "13:00": 10, "13:30": 11, "14:00": 12, "14:30": 13, "15:00": 14, "15:30": 15,
    "16:00": 16, "16:30": 17, "17:00": 18, "17:30": 19, "18:00": 20, "18:30": 21, "19:00": 22, "19:30": 23,
    "20:00": 24, "20:30": 25, "21:00": 26, "21:30": 27
}

ba_tz = timezone('America/Argentina/Buenos_Aires')

def time_slot_from_time_index(time_index):
    hour = int(time_index / 2)
    minute = time_index % 2
    hour = f"{8 + hour}"
    minute = "00" if minute == 0 else "30"
    return f"{hour}:{minute}"


def time_index_from_time_slot(time_slot):
    return hour_to_time_index[time_slot]


def from_iso_to_date_and_hour(year, week_index, day_index, time_index):
    dt = date.fromisocalendar(year, week_index, day_index).date()
    hour = time_slot_from_time_index(time_index)
    return_value = (dt, hour)
    return return_value


def from_datetime_to_iso(dt):
    hour = dt.hour
    hour = hour if hour < 22 else 21
    hour = hour if hour > 8 else 8
    return from_date_and_hour_to_iso(dt, f"{hour}:{'00' if dt.minute < 30 else '30'}")


def from_date_and_hour_to_iso(dt, hour):
    year, week_index, day_index = dt.isocalendar()
    time_index = time_index_from_time_slot(hour)
    return_value = (year, week_index, day_index, time_index)
    return return_value


def from_iso_to_datetime(year, week_index, day_index, time_index):
    hour = int(time_index / 2)
    minute = time_index % 2
    hour = 8 + hour
    minute = 0 if minute == 0 else 30
    dt = datetime.fromisocalendar(year, week_index, day_index)
    dt = dt + timedelta(hours=hour, minutes=minute)
    return dt


def week_date(dt=None):
    if dt is None:
        dt = datetime.today()

    monday = dt
    for _ in range(0, 7):
        if monday.weekday() == 0:
            break
        monday = monday - timedelta(1)
    return monday.date()


def empty_single_week_schedule_df(year_index, week_index):
    """
    Returns a DataFrame with year_index, week_index, day_index, time_index columns for a specific year_index,
    week_index values.

    :param year_index: int,
    :param week_index: int,
    :return: pd.DataFrame
    """
    li = []
    for i in range(1, 8):
        li.append(pd.DataFrame({
            "year_index": [year_index] * 28,
            "week_index": [week_index] * 28,
            "day_index": [i] * 28, "time_index": list(range(28))
        }))
    return pd.concat(li)


def empty_week_schedules_df(start_date=None, n_weeks=8):
    """
    Returns a DataFrame with year_index, week_index, day_index, time_index columns for the n_weeks
    into the future starting from the current week.

    :param start_date: datetime.date
    :param n_weeks: int,
    :return: pd.DataFrame
    """
    li = []
    if not start_date:
        start_date = week_date()
    for w in range(n_weeks):
        dt = start_date + timedelta(days=7 * w)
        year_index = dt.isocalendar().year
        week_index = dt.isocalendar().week
        li.append(empty_single_week_schedule_df(year_index, week_index))
    return pd.concat(li)


def impute_past_availability_slots(availability_df, minutes_lag=15):
    now_ids = from_datetime_to_iso(datetime.now().astimezone(ba_tz) - timedelta(minutes=minutes_lag))
    now_condition = (availability_df["year_index"] == now_ids[0]) & \
                     (availability_df["week_index"] == now_ids[1]) & \
                      (availability_df["day_index"] == now_ids[2]) & \
                       (availability_df["time_index"] == now_ids[3])

    limit_index = availability_df[now_condition].iloc[0].name
    availability_df.loc[availability_df.index < limit_index, "availability_type"] = -1
    return availability_df


def slot_schedule_week_to_view(week_schedule_df, schedule_type="availability"):
    schedule_type = "availability" if schedule_type[0].lower() == "a" else "enrolled"
    li = []
    for j in range(1, 8):
        _df = week_schedule_df[week_schedule_df["day_index"] == j].copy()
        _df = _df.set_index(["time_index"]).drop(["day_index"], axis=1).rename(columns={
            f"{schedule_type}_type": j})
        li.append(_df)
    return pd.concat(li, axis=1)


def explode_week_schedule_days(week_schedule_df, schedule_type="availability"):
    schedule_type = "availability" if schedule_type[0].lower() == "a" else "enrolled"
    li = []
    for i in range(7):
        schedule_type_df = week_schedule_df[i].reset_index(drop=True)
        day_index_df = pd.Series([i+1] * 28, name="day_index")
        li.append(pd.concat(
            [schedule_type_df, day_index_df], axis=1
        ).rename(columns={i: f"{schedule_type}_type"}))
    week_df = pd.concat(li)
    week_df.index.names = ["time_index"]
    return week_df


def transform_view_schedule_db_format(schedule_data):
    schedule = pd.DataFrame(schedule_data).groupby(["tutor_id", "year_index", "week_index"]).apply(lambda x: transform_week(x)).reset_index().rename(columns={"level_3": "time_index"})
    schedule["availability_type"] = schedule["availability_type"].replace({"V": 1, "P": 2, "VyP": 3, "": np.nan})
    schedule[["tutor_id", "year_index", "week_index", "day_index", "time_index"]] = schedule[["tutor_id", "year_index", "week_index", "day_index", "time_index"]].astype(int)
    return schedule[schedule["availability_type"] != "B"]


def transform_week(week_df):
    li = []
    for i in range(7):
        df1 = week_df["availability_days"].apply(lambda x: pd.Series(x))[i].reset_index(drop=True)._set_name("availability_type")
        df2 = pd.Series([i + 1] * 28, name="day_index")
        li.append(pd.concat([df1, df2], axis=1))
    return pd.concat(li)
