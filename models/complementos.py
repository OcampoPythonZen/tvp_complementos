# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime,date,time,timedelta
from dateutil.relativedelta import relativedelta

MONEDA_SEGUROS_SEGUROS_VARIOS=[
    ('MXN','Moneda Nacional'),
    ('DLL','Dolares'),
    ('E','Euros'),
    ]

TIPO_SEGURO_SEGUROS_VARIOS=[
    ('SV','Vida'),
    ('SGM','Gastos Medicos Mayores'),
    ('SDV','Viaje'),
    ('OS','Otro Seguro')
    ]

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

GRADO_ESTUDIOS_ESCOLARIDAD=[
    ('P1','Preescolar'),
    ('P2','Primaria'),
    ('S1','Secundaria'),
    ('P3','Preparatoria'),
    ('M1','Media Superior'),
    ('S2','Superior'),
    ('M2','Maestria'),
    ('D','Doctorado'),
    ]

ESTADO_ESTUDIOS_ESCOLARIDAD=[
    ('I','Inscrito'),
    ('C','Cursando'),
    ('F','Finalizado'),
    ]

CONSTANCIA_ESCOLARIDAD=[
    ('D','Diploma'),
    ('C1','Certificado'),
    ('C2','Cedula'),
    ('C3','Constancia'),
    ('T','En tramite...'),
    ]
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
    tipo_de_seguro_id = fields.Selection(TIPO_SEGURO_SEGUROS_VARIOS, string="Tipo de Seguro")
    tipo_de_moneda_id = fields.Selection(MONEDA_SEGUROS_SEGUROS_VARIOS, string="Moneda del Seguro",
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
    notes = fields.Text('Notas',track_visibility='onchange')

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


#CLASE DE TVP.EMPLEADO PARA AGREGAR LOS CAMPOS A LA VISTA DE EMPLEADOS-------------------------------------

class tvp_empleado(models.Model):
    _inherit='hr.employee'

    active = fields.Boolean('Empleado Activo', default=True, track_visibility='onchange')
    curp=fields.Char(string='C.U.R.P',size=18,required=True, track_visibility='onchange')
    rfc=fields.Char(string='R.F.C.',size=13,required=True, track_visibility='onchange')
    nss=fields.Char(string='N.S.S.',size=11,required=True, track_visibility='onchange')
    nom_contacto=fields.Char('Nombre del contacto', track_visibility='onchange')
    tel_contacto=fields.Char('Tel. de contacto',size=10, track_visibility='onchange')
    fecha_ingreso=fields.Date('Fecha de ingreso',default=datetime.today(), track_visibility='onchange')
    edad=fields.Char(string='Edad', track_visibility='onchange')
    antiguedad=fields.Char(string='Antiguedad', track_visibility='onchange')
    antiguedad_inactive=fields.Char(string='Inactivo, antiguedad', track_visibility='onchange')
    tipo_sangre=fields.Selection(TIPO_SANGRE_EMPLEADO,'Tipo de sangre', track_visibility='onchange')
    num_empleado=fields.Integer('Numero de empleado',required=True,size=4,help='Los numeros de empleado son de solo 4 DIGITOS.', track_visibility='onchange')
    fecha_baja=fields.Date('Fecha de baja',help='Si lo requiere llene este campo con la fecha correspondiente a la baja...', track_visibility='onchange')

    @api.onchange('birthday','edad')
    def calcula_edad(self):
        if self.birthday!=False:

            formato_fecha="%Y-%m-%d"
            fecha_cumple=datetime.strptime(str(self.birthday),formato_fecha)
            fecha_actual=datetime.strptime(str(date.today()),formato_fecha)
            resultado=fecha_actual.year-fecha_cumple.year
            if (fecha_actual.month and fecha_actual.day) > (fecha_cumple.month and fecha_cumple.day):
                resultado-=1
            self.edad=resultado

    @api.onchange('fecha_ingreso','antiguedad')
    def calcula_antiguedad(self):
        if self.fecha_ingreso!=False:
            formato_fecha="%Y-%m-%d"
            fecha_ingre=datetime.strptime(str(self.fecha_ingreso), formato_fecha)
            fecha_actual=datetime.strptime(str(date.today()), formato_fecha)
            resultado = fecha_actual.year - fecha_ingre.year
            if (fecha_actual.month and fecha_actual.day) > (fecha_ingre.month and fecha_ingre.day):
                resultado -= 1
            self.antiguedad=resultado

    @api.onchange('antiguedad_inactive','fecha_ingreso','fecha_baja')
    def calc_fecha_final_antiguedad(self):
        if self.fecha_ingreso!=False and self.fecha_baja!=False:
            formato_fecha="%Y-%m-%d"
            fecha_ingre = datetime.strptime(str(self.fecha_ingreso), formato_fecha)
            fecha__de_baja = datetime.strptime(str(self.fecha_baja), formato_fecha)
            resultado = fecha__de_baja.year - fecha_ingre.year
            if (fecha__de_baja.month and fecha__de_baja.day) < (fecha_ingre.month and fecha_ingre.day):
                resultado -= 1
            self.antiguedad_inactive = resultado


#---------------------CLASE PARA MODIFICACINO DE CONTRATOS--------------------------------------------------------
class tvp_contract(models.Model):
    _inherit = "hr.contract"

    active = fields.Boolean('Contrato Activo', default=True,track_visibility='onchange')
    meses_prestaciones = fields.Float('Prestaciones en Meses', help="Meses de Bonificación al Año según Nivel",track_visibility='onchange')
    sueldo_bruto_mensual = fields.Float('Sueldo Bruto Mensual',track_visibility='onchange')
    sueldo_bruto_anualp = fields.Float('SBA con Prestaciones', help="Sueldo Bruto anual con Prestaciones",track_visibility='onchange')
    sueldo_bruto_mensualp = fields.Float('SBM con Prestaciones', help="Sueldo Bruto Mensual con Prestaciones",track_visibility='onchange')
    nivel_id = fields.Many2one('nivel.nivel', ondelete='restrict', string="Nivel del Puesto", index=True,track_visibility='onchange')
    base_id = fields.Many2one('base.anual', ondelete='restrict', string="Base Anual", index=True,track_visibility='onchange')
    compania_contratadora = fields.Many2one('res.company', ondelete='restrict', string="Empresa", index=True,track_visibility='onchange')
    motivo = fields.Selection([('aumento', 'Aumento de sueldo'),
                               ('cambio', 'Cambio de Puesto'),
                               ('renovacion', 'Renovación de Contrato'),
                               ('vencimiento', 'Vencimiento de Contrato'),
                               ('recorte', 'Recorte de Personal'),
                               ('cancelacion', 'Cancelación de Contrato')],string='Motivo',track_visibility='onchange')
    porcentaje = fields.Float(string='Porcentaje Aumentado', help="Porcentaje Aumentado",track_visibility='onchange')
    nuevo_sueldo = fields.Float(string='Nuevo SBM', help="Nuevo Sueldo Bruto Mensual que recibirá el empleado",track_visibility='onchange')
    monto = fields.Float(string='Monto Finiquitado', help="Monto entregado como liquidación o finiquito del contrato",track_visibility='onchange')
    comentarios = fields.Char(string='Comentarios',track_visibility='onchange')

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



class Employee(models.Model):
    _inherit = "hr.employee"

    experiencia_academica_ids = fields.One2many('hr.escolaridad', 'employee_id', 'Experiencia Académica', help="Experiencia Académica")

#----------------------------------MODELO CLASS ESCOLARIDAD PARA LA VISTA DE EMPLEADO------------------------------------------
class Escolaridad(models.Model):
    _name = 'hr.escolaridad'
    _inherit = ['mail.thread']
    _description = 'Escolaridad del Empleado'

    name = fields.Char(string='Nombre del Estudio', required=True,track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True,track_visibility='onchange')
    nivel_estudio = fields.Selection(GRADO_ESTUDIOS_ESCOLARIDAD, string='Nivel de Estudios',track_visibility='onchange')
    estado = fields.Selection(ESTADO_ESTUDIOS_ESCOLARIDAD, string='Estado de Estudios',track_visibility='onchange')
    escuela = fields.Char(string='Nombre de la Escuela',track_visibility='onchange')
    constancia_recibida = fields.Selection(CONSTANCIA_ESCOLARIDAD,string='Constancia Recibida',track_visibility='onchange')
    notas = fields.Char('Notas',track_visibility='onchange')