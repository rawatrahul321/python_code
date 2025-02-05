# -*- coding: utf-8 -*-

from datetime import datetime, date,    timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models
import urllib 
import urllib2 

class HREmployee(models.Model):
    _inherit = "hr.employee"
    
    @api.model
    def _cron_attendance_reminder(self):
        print '++Entry Attendance Reminder+++'
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        current_date = datetime.now()
        print 'Current Date',current_date
        next_day = datetime.today() + timedelta(days=1)
        for employee in self.env['hr.employee'].search([]):
            if employee:
                print '++++Employee Name++++++\n',employee.name
                try:
                    if employee.contract_ids[0].working_hours.attendance_ids.search([('dayofweek', '=', date.today().weekday())]):
                        print 'entry check++++++++',employee.contract_ids[0].working_hours.attendance_ids.search([('dayofweek', '=', '0'),('hour_from','=','10')]).id
                        emp_attendance = self.env['hr.attendance'].search_count([('employee_id', '=', employee.id),('check_in', '>=', current_date.strftime('%Y-%m-%d 00:00:00')),('check_out', '<=', current_date.strftime('%Y-%m-%d 23:59:59'))])             
                        print '++emp attendance+++++',emp_attendance
                        if emp_attendance < 1:
                            emp_holiday = self.env['hr.holidays'].search_count([('employee_id', '=', employee.id),('date_from', '>=',current_date.strftime('%Y-%m-%d 00:00:00')),('date_to', '<=',current_date.strftime('%Y-%m-%d 23:59:59'))])          
                            if emp_holiday < 1:
                                
                                print '+++Check If Employee On Holiday Or Not+++',emp_holiday
                                authkey = "214866AaEV4njibw065af4929e" 
                                mobile1 = employee.mobile_phone
                                mobile2 = employee.boss_number
                                mobile3 = employee.boss_secretary
                                print 'MOBILES+++',mobile1, mobile2, mobile3
                                message = "Hi " + ""+ employee.name +""+ "  this is to inform you that today you have forgotten to mark your attendance. Kindly do so else it will consider absent. \n Regards Admin"
                                sender = "MSGIND" 
                                route = "4" 
                                # Prepare you post parameters
                                values = {
                                          'authkey' : authkey,
                                          'mobiles' : mobile1,
                                          'message' : message,
                                          'sender' : sender,
                                          'route' : route
                                          }
                                
                                url = "http://api.msg91.com/api/sendhttp.php?sender=MSGIND&route=4&mobiles=%s&authkey=%s&country=91&message=%s,(mobile1,authkey,message)" # API URL
                                
                                postdata = urllib.urlencode(values) # URL encoding the data here.
                                
                                req = urllib2.Request(url, postdata)
                                
                                response = urllib2.urlopen(req)
                                
                                output = response.read() # Get Response
                                print output # Print Response
                                
                                values1 = {
                                          'authkey' : authkey,
                                          'mobiles' : mobile2,
                                          'message' : message,
                                          'sender' : sender,
                                          'route' : route
                                          }
                                
                                url1 = "http://api.msg91.com/api/sendhttp.php?sender=MSGIND&route=4&mobiles=%s&authkey=%s&country=91&message=%s,(mobile2,authkey,message)" # API URL
                                
                                postdata1 = urllib.urlencode(values1) # URL encoding the data here.
                                
                                req1 = urllib2.Request(url1, postdata1)
                                
                                response1 = urllib2.urlopen(req1)
                                
                                output1 = response1.read() # Get Response
                                print output1 # Print Response

                                print "Message Sent Sucessfully To " + ""+ employee.name +""+ " For Late Comers.\n\n"
                                
                                values2 = {
                                          'authkey' : authkey,
                                          'mobiles' : mobile3,
                                          'message' : message,
                                          'sender' : sender,
                                          'route' : route
                                          }
                                
                                url2 = "http://api.msg91.com/api/sendhttp.php?sender=MSGIND&route=4&mobiles=%s&authkey=%s&country=91&message=%s,(mobile3,authkey,message)" # API URL
                                
                                postdata2 = urllib.urlencode(values2) # URL encoding the data here.
                                
                                req2 = urllib2.Request(url2, postdata2)
                                
                                response2 = urllib2.urlopen(req2)
                                
                                output2 = response2.read() # Get Response
                                print output2 # Print Response

                                print "Message Sent Sucessfully To Boss Secretary  For " + ""+ employee.name +""+ " For Late Comer.\n\n"

                                
                            get_holiday_date  = self.env['hr.holidays'].search([('employee_id', '=', employee.id),('date_from', '>=',current_date.strftime('%Y-%m-%d 00:00:00')),('date_to', '>=',current_date.strftime('%Y-%m-%d 23:59:59'))])
                            if get_holiday_date:
                                print 'Holiday Date ==++++',get_holiday_date.date_from,  get_holiday_date.id
                                a= self.env.cr.execute("select date_from::date from hr_holidays where id =%s",(get_holiday_date.id,))
                                b=self.env.cr.fetchall()[0][0]
                                print 'Holiday Date remove time++++++',b
                                c = self.env.cr.execute("SELECT current_date + 1;")
                                d = self.env.cr.fetchall()[0][0]
                                print 'NEXT DATE From current date+++++++',d
                            if  d == b:
                                print 'Alarm before 1 day+++++'
                                print '+++Check If Employee On Holiday Or Not+++',emp_holiday
                                authkey = "214866AaEV4njibw065af4929e" 
                                mobiles = employee.mobile_phone 
                                message = "Hi " + ""+ employee.name +""+ "  this is to inform you that Tommorow is Public Holiday and Office will remain closed. \n Regards Admin"
                                sender = "MSGIND" 
                                route = "4" 
                                # Prepare you post parameters
                                values = {
                                          'authkey' : authkey,
                                          'mobiles' : mobiles,
                                          'message' : message,
                                          'sender' : sender,
                                          'route' : route
                                          }
                                
                                url = "http://api.msg91.com/api/sendhttp.php?sender=MSGIND&route=4&mobiles=%s&authkey=%s&country=91&message=%s,(mobiles,authkey,message)" # API URL
                                
                                postdata = urllib.urlencode(values) # URL encoding the data here.
                                
                                req = urllib2.Request(url, postdata)
                                
                                response = urllib2.urlopen(req)
                                
                                output = response.read() # Get Response
                                print output # Print Response
                                print "Message Sent Sucessfully to " + ""+ employee.name +""+ " For Public Holiday\n\n."
                            
    
                            
                except:
                    continue
                
                
                
                
                
                
                
                
