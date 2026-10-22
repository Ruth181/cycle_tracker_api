from datetime import datetime, timedelta, date


def calculate_period_days_remaining(period_duration:int, last_period_first_day : datetime):
    return last_period_first_day + timedelta(days=period_duration -1)

def calculate_next_period(last_period_first_day : datetime, cycle_length : int):
    return last_period_first_day + timedelta(days=cycle_length)

def calculate_ovulation(last_period_first_day : datetime, cycle_length : int):
    return  last_period_first_day + timedelta(days=cycle_length -14)

def calculate_follicular(last_period_first_day : datetime, cycle_length : int) -> dict:
    follicular_end = calculate_ovulation(last_period_first_day, cycle_length) - timedelta(days=1)
    return {
        "start" : last_period_first_day,
        "end" :  follicular_end
    }

def calculate_luteal(last_period_first_day : datetime, cycle_length : int) -> dict:
    luteal_start = calculate_ovulation(last_period_first_day, cycle_length) + timedelta(days=1)
    luteal_end = calculate_next_period(last_period_first_day,cycle_length) - timedelta(days=1)

    return {
        "start" : luteal_start,
        "end" : luteal_end
    }


def calculate_fertile_window(last_period_first_day : datetime, cycle_length : int) -> dict:
    ovulation = calculate_ovulation(last_period_first_day, cycle_length)
    return {
        "start" : (ovulation - timedelta(days=5)),
        "end" : (ovulation + timedelta(days=1))
    }


def calculate_date(start_date:date, end_date:date) -> bool:
    today_date = date.today()
    start = date(start_date.year, start_date.month,start_date.day)
    end = date(end_date.year, end_date.month, end_date.day)

    if start <= today_date <= end:
        return True

    return False

if __name__ == "__main__":
    first_period_first_day = datetime.strptime("29/09/2026", "%d/%m/%Y")
    print(calculate_next_period(first_period_first_day, 22))
    print(calculate_fertile_window(first_period_first_day,22))
