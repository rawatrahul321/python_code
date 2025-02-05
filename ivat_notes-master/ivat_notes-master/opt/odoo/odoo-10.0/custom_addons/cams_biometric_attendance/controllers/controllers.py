# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime
import time

class CamsAttendance(http.Controller):

    @http.route('/web/cams-attendance/new-entry/',method=["POST"], csrf=False, auth='public')
    def generate_attendance(self, **params):
        """
        Gets the params from the machine data and create 
        record in attendance module.
        """
        employee_ref = params.get('userid')
        employee = request.env['hr.employee'].sudo().search([('employee_ref','=', employee_ref)])
        
        attendance_type = params.get('att_type')
        attendance_time = params.get('att_time')        
        timezone_difference_seconds = 19800
        attendance_time = float(attendance_time) - float(timezone_difference_seconds)
        machine_id = params.get('stgid')
       
        try:
            att_time_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(attendance_time)))
            att_time_obj = datetime.strptime(att_time_string, '%Y-%m-%d %H:%M:%S')
        except:
            return "ok"
        
        if employee:
            auth_token = "token"
            if params.get('auth_token') == auth_token:
                if attendance_type == 'in':
                    vals = {'employee_id': employee.id,'check_in': att_time_obj,'machine_id':machine_id} 
                    attendance = request.env['hr.attendance'].sudo().create(vals)
                if attendance_type == 'out':                
                    attendance = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)
                    if attendance:
                        attendance.check_out = att_time_obj
                    else:
                        vals = {'employee_id': employee.id,'check_out': att_time_obj,'machine_id':machine_id} 
                        attendance = request.env['hr.attendance'].sudo().create(vals)
                return "ok"     
            else:
                return "ok"     

        else:
            return 'ok'
      

            
