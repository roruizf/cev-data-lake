import os
import requests
import lxml.html as html
import math
import time
from datetime import datetime


def form_data_consulta(region_id, commune_id, rating_type, viewstate):
    return {
        'ToolkitScriptManager2_HiddenField': ';;AjaxControlToolkit, Version=4.1.60501.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:es-CL:5c09f731-4796-4c62-944b-da90522e2541:de1feab2:f2c8e708:720a52bf:f9cec9bc:589eaa30:a67c2700:ab09e3fe:87104b7c:8613aea7:3202a5a2:be6fb298',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': '2B422A52',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '0',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$ContentPlaceHolder1$look': '0',
        'ctl00$ContentPlaceHolder1$dbRegion': region_id,
        'ctl00$ContentPlaceHolder1$dbComuna': commune_id,
        'ctl00$ContentPlaceHolder1$dbCertificacion': rating_type,
        'ctl00$ContentPlaceHolder1$dbTipologia': '-1',
        'ctl00$ContentPlaceHolder1$TxtNombrePry': '',
        'ctl00$ContentPlaceHolder1$txtIdentificacion': '',
        'ctl00$ContentPlaceHolder1$BtnConsultarbusq': 'Consultar',
        'ctl00$ContentPlaceHolder1$txtCampo': '0',
        'ctl00$ContentPlaceHolder1$txtOrden': '0'
    }

def form_data_evaluacion(eventtarget, eventargument, region_id, commune_id, rating_type, viewstate):
    return {
        'ToolkitScriptManager2_HiddenField': ';;AjaxControlToolkit, Version=4.1.60501.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:es-CL:5c09f731-4796-4c62-944b-da90522e2541:de1feab2:f2c8e708:720a52bf:f9cec9bc:589eaa30:a67c2700:ab09e3fe:87104b7c:8613aea7:3202a5a2:be6fb298',
        '__EVENTTARGET': eventtarget,
        '__EVENTARGUMENT': eventargument,
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': '2B422A52',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '0',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$ContentPlaceHolder1$look': '0',
        'ctl00$ContentPlaceHolder1$dbRegion': region_id,
        'ctl00$ContentPlaceHolder1$dbComuna': commune_id,
        'ctl00$ContentPlaceHolder1$dbCertificacion': rating_type,
        'ctl00$ContentPlaceHolder1$dbTipologia': '-1',
        'ctl00$ContentPlaceHolder1$TxtNombrePry': '',
        'ctl00$ContentPlaceHolder1$txtIdentificacion': '',
        'ctl00$ContentPlaceHolder1$txtCampo': '0',
        'ctl00$ContentPlaceHolder1$txtOrden': '0'
    }

def form_data_pdf_report(eventtarget, eventargument, viewstate, region_id, comuna_id, tipo_evaluacion, target_report_label_code):
    return {
        'ToolkitScriptManager2_HiddenField': ';;AjaxControlToolkit, Version=4.1.60501.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:es-CL:5c09f731-4796-4c62-944b-da90522e2541:de1feab2:f2c8e708:720a52bf:f9cec9bc:589eaa30:a67c2700:ab09e3fe:87104b7c:8613aea7:3202a5a2:be6fb298',
        '__EVENTTARGET': eventtarget,
        '__EVENTARGUMENT': eventargument,
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': '2B422A52',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '395',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$ContentPlaceHolder1$look': '0',
        'ctl00$ContentPlaceHolder1$dbRegion': region_id,
        'ctl00$ContentPlaceHolder1$dbComuna': comuna_id,
        'ctl00$ContentPlaceHolder1$dbCertificacion': tipo_evaluacion,
        'ctl00$ContentPlaceHolder1$dbTipologia': '-1',
        'ctl00$ContentPlaceHolder1$TxtNombrePry': '',
        'ctl00$ContentPlaceHolder1$txtIdentificacion': '',
        target_report_label_code + '.x': '7',
        target_report_label_code + '.y': '7',
        'ctl00$ContentPlaceHolder1$txtCampo': '0',
        'ctl00$ContentPlaceHolder1$txtOrden': '0'
    }