import datetime


def year(request):
    date = datetime.date.today()
    return {'year': date.year}
