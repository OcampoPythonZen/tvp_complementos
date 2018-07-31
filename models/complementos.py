# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime,date
from dateutil.relativedelta import relativedelta

class SegurosVar(models.Model):
    _name = 'hr.segurosvar'
    _inherit = ['mail.thread']

    @api.depends('vigencia_meses', 'fecha_inicio')
    def get_fecha_vencimiento(self):
        for rec in self:
            fecha_inicio2 = fields.Datetime.from_string(rec.fecha_inicio)
            if rec.vigencia_meses:
                rec.fecha_vencimiento = fecha_inicio2 + relativedelta(months=rec.vigencia_meses)

    name = fields.Char('Clave de Seguro', required=True,size=14)
    employee_id = fields.Many2one('hr.employee', "Empleado", required=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Departamento", track_visibility='onchange')
    job_id = fields.Many2one('hr.job', 'Puesto', track_visibility='onchange')
    tipo_de_seguro_id = fields.Many2one('tipo.seguro', ondelete='restrict', string="Tipo de Seguro",
                                        track_visibility='onchange', index=True)
    tipo_de_moneda_id = fields.Many2one('moneda.seguro', ondelete='restrict', string="Moneda del Seguro",
                                        track_visibility='onchange', index=True)
    prima_neta = fields.Float('Prima Neta', help="Monto Mensual de la tarjeta", track_visibility='onchange')
    derecho_poliza = fields.Float('Derecho de Poliza', help="Monto Anual de la tarjeta", track_visibility='onchange')
    proveedor = fields.Many2one('res.partner', string='Proveedor', track_visibility='onchange')

    vigencia_meses = fields.Integer('Vigencia en Meses', default="12", help="Monto Anual de la tarjeta",
                                    track_visibility='onchange')
    fecha_inicio = fields.Date('Fecha de inicio', default=datetime.today(), track_visibility='onchange')

    fecha_vencimiento = fields.Date('Vencimiento', compute='get_fecha_vencimiento', track_visibility='onchange')
    active = fields.Boolean('Seguro Activo', track_visibility='onchange', default=True)
    notes = fields.Text('Notas')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.resource_calendar_id = self.employee_id.resource_calendar_id


class TipoSeguro(models.Model):
    _name = 'tipo.seguro'
    name = fields.Char(string='Tipo de Seguro')
    notas = fields.Char(string='Notas')

class MonedaSeguro(models.Model):
    _name = 'moneda.seguro'
    name = fields.Char(string='Tipo de Moneda')
    notas = fields.Char(string='Notas')


class Employee(models.Model):

    _inherit = "hr.employee"

    seguros_ids = fields.One2many('hr.segurosvar', 'employee_id', string='Seguros')
    seguros_id = fields.Many2one('hr.segurosvar', compute='_compute_seguros_id', string='Seguros Actuales', help='Último seguro del empleado')
    seguros_count = fields.Integer(compute='_compute_seguros_count', string='Seguros')


    def _compute_seguros_id(self):
        """ get the lastest seguro """
        Seguros = self.env['hr.segurosvar']
        for employee in self:
            employee.seguros_id = Seguros.search([('employee_id', '=', employee.id)], order='fecha_inicio desc', limit=1)

    def _compute_seguros_count(self):
        # read_group as sudo, since seguros count is displayed on form view
        seguros_data = self.env['hr.segurosvar'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in seguros_data)
        for employee in self:
            employee.seguros_count = result.get(employee.id, 0)


#--------------------------------------Segunda class de tarjetas de Gasolina ----------------------------------
class hr_gasolina(models.Model):
    _name = 'hr.gasolina'
    _inherit = ['mail.thread']


    name = fields.Char('No. de Tarjeta', required=True,size=12)
    employee_id = fields.Many2one('hr.employee', "Empleado", track_visibility='onchange', required=True)
    department_id = fields.Many2one('hr.department', track_visibility='onchange', string="Departamento")
    job_id = fields.Many2one('hr.job', 'Puesto', track_visibility='onchange')
    monto_mensual = fields.Float('Monto Mensual', track_visibility='onchange', help="Monto Mensual de la tarjeta")
    monto_anual = fields.Float('Monto Anual', help="Monto Anual de la tarjeta", track_visibility='onchange')
    proveedor = fields.Many2one('res.partner', string='Proveedor', track_visibility='onchange')
    active = fields.Boolean('Tarjeta Activa', track_visibility='onchange', default=True)
    notes = fields.Text('Notas')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.resource_calendar_id = self.employee_id.resource_calendar_id

    @api.onchange('monto_mensual')
    def calcular_anual_onchange(self):
            self.monto_anual = self.monto_mensual * 12


class Employee(models.Model):

    _inherit = "hr.employee"

    gasolina_ids = fields.One2many('hr.gasolina', 'employee_id', string='Gasolina')
    gasolina_count = fields.Integer(compute='_compute_gasolina_count', string='Gasolina')


    def _compute_gasolina_count(self):
        # read_group as sudo, since gasolina count is displayed on form view
        gasolina_data = self.env['hr.gasolina'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in gasolina_data)
        for employee in self:
            employee.gasolina_count = result.get(employee.id, 0)


#CLASE DE TVP.EMPLEADO PARA AGREGAR LOS CAMPOS A LA VISTA DE EMPLEADOS

TIPO_SANGRE_EMPLEADO=[
    ('O-','O Negativo'),
    ('O+','O Positivo'),
    ('A-','A Negativo'),
    ('A+','A Positivo'),
    ('B-','B Negativo'),
    ('B+','B Positivo'),
    ('AB-','AB Negativo'),
    ('AB+','AB Positivo'),
]

class tvp_empleado(models.Model):
    _inherit='hr.employee'

    curp=fields.Char(string='C.U.R.P',size=18,required=True)
    rfc=fields.Char(string='R.F.C.',size=13,required=True)
    nss=fields.Char(string='N.S.S.',size=11,required=True)

    nom_contacto=fields.Char('Nombre del contacto')
    tel_contacto=fields.Char('Tel. de contacto',size=10)
    fecha_ingreso=fields.Date('Fecha de ingreso',default=datetime.today())


    edad=fields.Char('Edad',readonly=True)#,compute='_cal_edad'
    antiguedad = fields.Char('Antiguedad',size=2,readonly=True)#,compute='_cal_antiguedad'

    tipo_sangre=fields.Selection(TIPO_SANGRE_EMPLEADO,'Tipo de sangre',required=True)
    num_empleado=fields.Integer('Numero de empleado',required=True,size=4,help='Los numeros de empleado son de solo 4 DIGITOS.')
    fecha_baja=fields.Date('Fecha de baja',help='Si lo requiere llene este campo con la fecha correspondiente a la baja...')


class tvp_contract(models.Model):
    _inherit = "hr.contract"

    active = fields.Boolean('Contrato Activo', default=True)
    meses_prestaciones = fields.Float('Prestaciones en Meses', help="Meses de Bonificación al Año según Nivel")
    sueldo_bruto_mensual = fields.Float('Sueldo Bruto Mensual')
    sueldo_bruto_anualp = fields.Float('SBA con Prestaciones', help="Sueldo Bruto anual con Prestaciones")
    sueldo_bruto_mensualp = fields.Float('SBM con Prestaciones', help="Sueldo Bruto Mensual con Prestaciones")
    nivel_id = fields.Many2one('nivel.nivel', ondelete='restrict', string="Nivel del Puesto", index=True)
    base_id = fields.Many2one('base.anual', ondelete='restrict', string="Base Anual", index=True)
    compania_contratadora = fields.Many2one('res.company', ondelete='restrict', string="Empresa", index=True)
    motivo = fields.Selection([('aumento', 'Aumento de sueldo'),
                               ('cambio', 'Cambio de Puesto'),
                               ('renovacion', 'Renovación de Contrato'),
                               ('vencimiento', 'Vencimiento de Contrato'),
                               ('recorte', 'Recorte de Personal'),
                               ('cancelacion', 'Cancelación de Contrato')],string='Motivo')
    porcentaje = fields.Float(string='Porcentaje Aumentado', help="Porcentaje Aumentado")
    nuevo_sueldo = fields.Float(string='Nuevo SBM', help="Nuevo Sueldo Bruto Mensual que recibirá el empleado")
    monto = fields.Float(string='Monto Finiquitado', help="Monto entregado como liquidación o finiquito del contrato")
    comentarios = fields.Char(string='Comentarios')

    @api.onchange('sueldo_bruto_mensual')
    def calcular_onchange(self):
        meses_totales = 12 + self.meses_prestaciones
        self.sueldo_bruto_anualp = self.sueldo_bruto_mensual * meses_totales

    @api.onchange('meses_prestaciones')
    def calcular2_onchange(self):
        meses_totales = 12 + self.meses_prestaciones
        self.sueldo_bruto_anualp = self.sueldo_bruto_mensual * meses_totales

    @api.onchange('sueldo_bruto_anualp')
    def calcular3_onchange(self):
        self.sueldo_bruto_mensualp = self.sueldo_bruto_anualp / 12

    @api.onchange('porcentaje')
    def calcular4_onchange(self):
        monto_aumentado = self.porcentaje * self.sueldo_bruto_mensual
        self.nuevo_sueldo = self.sueldo_bruto_mensual + monto_aumentado

class NiveldelPuesto(models.Model):
    _name = 'nivel.nivel'
    name = fields.Char(string='Nivel de Puesto')
    notas = fields.Char(string='Notas')

class BaseAnual(models.Model):
    _name = 'base.anual'
    name = fields.Char(string='Base Anual')
    notas = fields.Char(string='Notas')




