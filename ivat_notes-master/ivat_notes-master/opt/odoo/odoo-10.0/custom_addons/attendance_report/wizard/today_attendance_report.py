#-*- coding:utf-8 -*-
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import os
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import StringIO
import base64
import csv
import pandas as pd

class TodayAttendanceReport(models.TransientModel):
    _name = 'today.attendance.report'
    
    name = fields.Char('Name')
    filename = fields.Char('Filename', size = 64, readonly=True)
    filedata = fields.Binary('File', readonly=True)

    @api.multi
    def print_today_attendance_report(self):
        reg_obj=self.env['today.attendance.report'].search([])
        self.env.cr.execute("SELECT(todays_attendance_report())",());
       
        print"successful"
        res = self.env.cr.fetchall()
       
        a=self.env.cr.execute("SELECT * from todays_attendance_reports");
        res = self.env.cr.fetchall()
        fp = StringIO.StringIO()
        writer = csv.writer(fp)
        writer.writerow([ i[0] for i in self.env.cr.description ])
        for data in res:
            row = []
            for d in data:
                if isinstance(d, basestring):
                    d = d.replace('\n',' ').replace('\t',' ')
                    try:
                        d = d.encode('utf-8')
                    except:
                        pass
                if d is False: d = None
                row.append(d)
            writer.writerow(row)
        fp.seek(0)
        data = fp.read()
        fp.close()
        out=base64.encodestring(data)
        file_name = 'Todays Attendance Report.csv'
        self.write({'filedata':out, 'filename':file_name})
        return {
                    'name':'Todays Attendance Report',
                    'res_model':'today.attendance.report',
                    'type':'ir.actions.act_window',
                    'view_type':'form',
                    'view_mode':'form',
                    'target':'new',
                    'nodestroy': True,
                    'res_id': self.id,
                    } 












