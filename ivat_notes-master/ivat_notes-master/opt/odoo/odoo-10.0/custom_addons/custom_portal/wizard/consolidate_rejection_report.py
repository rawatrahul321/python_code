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

class ConsolidateRejectionReport(models.TransientModel):
    _name = 'consolidate.rejection.report'
    
    name = fields.Char('Name')
    date_from = fields.Date('From Date',required=True,default = lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('To Date',required=True,default = lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])
    filename = fields.Char('Filename', size = 64, readonly=True)
    filedata = fields.Binary('File', readonly=True)

    @api.multi
    def print_rejection_report(self):
        reg_obj=self.env['consolidate.rejection.report'].search([])
        for sal in self:
            c = ''
            date_from = "'"+ sal.date_from +"'"
            print"date_from",date_from            
            date_to = "'"+ sal.date_to +"'"
            print"date_to",date_to
            if sal.date_from > sal.date_to:
                raise UserError(_('From Date Should be Larger Than To Date !'))
            self.env.cr.execute("SELECT(rejection_report(%s,%s))",(date_from,date_to));
       
            print"successful"
            res = self.env.cr.fetchall()
       
        a=self.env.cr.execute("""SELECT scrap_date as "Scrap Date",mrp_no as "MRP No.",
        workorder_id as "Work Order",total_production as "Total Production Quantity",
        scrap_product as "Scrapped Product",rejection_quantity as "Rejection Quantity",
        rejection_reason as "Rejection Reason",ok_production as "OK Production",rejection_percent as "Rejection Percent (%)" 
        from consolidate_rejection_reports""");
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
        file_name = 'Rejection Report.csv'
        self.write({'filedata':out, 'filename':file_name})
        return {
                    'name':'Rejection Report',
                    'res_model':'consolidate.rejection.report',
                    'type':'ir.actions.act_window',
                    'view_type':'form',
                    'view_mode':'form',
                    'target':'new',
                    'nodestroy': True,
                    'res_id': self.id,
                    } 










