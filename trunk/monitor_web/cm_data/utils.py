import datetime


class TimePeriod(object):
    current_time=datetime.datetime.now()
    def visit(self,period):
        meth = None
        if period is not None:
            meth_name = 'visit_'+period
            meth = getattr(self, meth_name, None)
        if not meth:
            meth = self.visit_all
        return meth()

    def visit_all(self):
        date_from = datetime.datetime(2000, 1, 1, 0, 0, 0)
        date_to = datetime.datetime(self.current_time.year, self.current_time.month, self.current_time.day, self.current_time.hour, self.current_time.minute, self.current_time.second)
        return date_from, date_to

    def visit_month(self):
        date_from = datetime.datetime(self.current_time.year, self.current_time.month, 1, 0, 0, 0)
        date_to = datetime.datetime(self.current_time.year, self.current_time.month, self.current_time.day, self.current_time.hour, self.current_time.minute, self.current_time.second)
        return date_from, date_to

    def visit_quarter(self):
        month_index=self.current_time.month
        if month_index in (1,2,3):
            start_month=1
        elif month_index in (4,5,6):
            start_month=4
        elif month_index in (7,8,9):
            start_month=7
        elif month_index in (10,11,12):
            start_month=10
        date_from = datetime.datetime(self.current_time.year, start_month, 1, 0, 0, 0)
        date_to = datetime.datetime(self.current_time.year, self.current_time.month, self.current_time.day, self.current_time.hour, self.current_time.minute, self.current_time.second)
        return date_from, date_to

    def visit_year(self):
        date_from = datetime.datetime(self.current_time.year, 1, 1, 0, 0, 0)
        date_to = datetime.datetime(self.current_time.year, self.current_time.month, self.current_time.day, self.current_time.hour, self.current_time.minute, self.current_time.second)
        return date_from, date_to

