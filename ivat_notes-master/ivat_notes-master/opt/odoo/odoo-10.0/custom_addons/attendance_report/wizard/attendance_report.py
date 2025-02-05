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

class attendance_report(models.TransientModel):
    _name = 'attendance.report'
    
    name = fields.Char('Name')
    date_from = fields.Date('From Date',required=True,default = lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('To Date',required=True,default = lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])
    filename = fields.Char('Filename', size = 64, readonly=True)
    filedata = fields.Binary('File', readonly=True)
    employee = fields.Many2one('hr.employee','Employee',required=False)
    mydates  = fields.Char('MYdates')

    @api.multi
    def print_employee_report(self):
        reg_obj=self.env['attendance.report'].search([])
        for sal in self:
            date_from = "'"+ sal.date_from +"'"
            print"date_from",date_from            
            date_to = "'"+ sal.date_to +"'"
            print"date_to",date_to
            employee=sal.employee.id
            if sal.date_from > sal.date_to:
                raise UserError(_('From Date Should be Larger Than To Date !'))
            self.env.cr.execute("SELECT(attendance_report())",());
       
     
            print"successful"
            res = self.env.cr.fetchall()
       
        a=self.env.cr.execute("SELECT * from attendance_reports");
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
        file_name = 'Attendance_Report.csv'
        self.write({'filedata':out, 'filename':file_name})
        return {
                    'name':'Attendance Report',
                    'res_model':'attendance.report',
                    'type':'ir.actions.act_window',
                    'view_type':'form',
                    'view_mode':'form',
                    'target':'new',
                    'nodestroy': True,
                    'res_id': self.id,
                    } 












