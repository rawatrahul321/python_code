from datetime import datetime, timedelta
from odoo import api, fields, models, tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import date
import calendar

HOURS_PER_DAY = 8

class HRHolidays(models.Model):
    _inherit = 'hr.holidays'
    
    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
            print 'No. Of Days 1 @@@@@@@@@@@=',self.number_of_days_temp
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to
        temp = 0.0        

        if date_from:
            day_start = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S').strftime('%A')
            day_end = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S').strftime('%A')
            print 'DAY NAME@@@@@@@=',day_start, day_end
        if (date_to and date_from) and (date_from <= date_to) and day_start == 'Monday':
            temp = self._get_number_of_days(date_from, date_to, self.employee_id.id) + 1
            print 'Temp',temp
            self.number_of_days_temp = temp
            print 'No. Of Days If leave on Monday ++++',self.number_of_days_temp
        if (date_to and date_from) and (date_from <= date_to) and day_start == 'Saturday':
            temp = self._get_number_of_days(date_from, date_to, self.employee_id.id) + 1
            print 'Temp',temp
            self.number_of_days_temp = temp
            print 'No. Of Days If leave on Saturday ++++',self.number_of_days_temp
        if (date_to and date_from) and (date_from <= date_to) and day_start == 'Saturday' and day_end == 'Monday':
            temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
            print 'Temp',temp
            self.number_of_days_temp = temp
            print 'No. Of Days If leave on Sat & Mon ++++',self.number_of_days_temp

        
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to) and day_start != 'Monday' and day_start !='Saturday':
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
            print 'No. Of Days 2 @@@@@@@@@@@=',self.number_of_days_temp
#         else:
#             self.number_of_days_temp = 0






