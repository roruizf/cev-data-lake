import os
import fnmatch
import pandas as pd
import lxml.html as html

def find_html_files(directory):
    html_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if fnmatch.fnmatch(filename, '*.html'):
                html_files.append(os.path.join(root, filename))
    return html_files

def read_single_html_file(html_file_path):
    parsed = html.parse(html_file_path)
    tipo_evaluacion = os.path.split(html_file_path)[-1].split('_')[2]
    #tipo_evaluacion = '1'

    evals_page_dict = {}
    if str(tipo_evaluacion) == '1':    
        message_found = parsed.xpath('//strong/span[@id="ContentPlaceHolder1_ResultadoGrillaPre"]/descendant-or-self::*/text()')
        #message_found = []
        if message_found: # Se ha(n) encontrado XXX Vivienda(s).
            # identificacion_vivienda
            evals_page_dict['identificacion_vivienda'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][1]/text()')
            # tipologia
            evals_page_dict['tipologia'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][2]/text()')
            # comuna
            evals_page_dict['comuna'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][3]/text()')
            # proyecto
            evals_page_dict['proyecto'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][4]/text()')
            # CE
            evals_page_dict['CE'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[position() = (last()-2)]/div/img/@src')
            evals_page_dict['CE'] = [x.split('Letra')[1].split('.png')[0] for x in evals_page_dict['CE']]
            # CEE
            evals_page_dict['CEE'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[position() = (last()-1)]/div/img/@src')
            evals_page_dict['CEE'] = [x.split('Letra')[1].split('.png')[0] for x in evals_page_dict['CEE']]
            evals_page_dict['CEE'] = [None if item == '--' else item for item in evals_page_dict['CEE']]
            # Informe
            evals_page_dict['codigo_informe'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[position() = last()]/div/div[@class="BtVerEtiqueta"]/div/input/@name')
            # Etiqueta
            evals_page_dict['codigo_etiqueta'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[position() = last()]/div/div[@class="BtVerMapa"]/div/input/@name')
            # ViewState
            evals_page_dict['viewstate'] = parsed.xpath('//input[@name="__VIEWSTATE"]/@value') * len(evals_page_dict['comuna'])

        else: #No existen viviendas calificadas para los filtros ingresados.
            evals_page_dict = {'identificacion_vivienda': [],
                               'tipologia': [],
                               'comuna': [],
                               'proyecto': [],
                                'CE': [],
                                'CEE': [],
                                'codigo_informe': [],
                                'codigo_etiqueta': [],
                                'viewstate': []}

    elif str(tipo_evaluacion) == '2':    
        message_found = parsed.xpath('//strong/span[@id="ContentPlaceHolder1_ResultadoGrillaCal"]/descendant-or-self::*/text()')    
        if message_found: # Se ha(n) encontrado XXX Vivienda(s).        
            # identificacion_vivienda
            evals_page_dict['identificacion_vivienda'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][1]/text()')
            # tipologia
            evals_page_dict['tipologia'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][2]/text()')
            # comuna
            evals_page_dict['comuna'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][3]/text()')
            # proyecto
            evals_page_dict['proyecto'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][4]/text()')
            # CE
            evals_page_dict['CE'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[position() = (last()-2)]/div/img/@src')
            evals_page_dict['CE'] = [x.split('Letra')[1].split('.png')[0] for x in evals_page_dict['CE']]
            # CEE
            evals_page_dict['CEE'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[position() = (last()-1)]/div/img/@src')
            evals_page_dict['CEE'] = [x.split('Letra')[1].split('.png')[0] for x in evals_page_dict['CEE']]        
            evals_page_dict['CEE'] = [None if item == '--' else item for item in evals_page_dict['CEE']]
            # Informe
            evals_page_dict['codigo_informe'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[position() = last()]/div/div[@class="BtVerEtiqueta"]/div/input/@name')
            # Etiqueta
            evals_page_dict['codigo_etiqueta'] = parsed.xpath('//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[position() = last()]/div/div[@class="BtVerMapa"]/div/input/@name')
            # ViewState
            evals_page_dict['viewstate'] = parsed.xpath('//input[@name="__VIEWSTATE"]/@value') * len(evals_page_dict['comuna'])

        else: #No existen viviendas calificadas para los filtros ingresados.
            evals_page_dict = {'identificacion_vivienda': [],
                               'tipologia': [],
                               'comuna': [],
                               'proyecto': [],
                                'CE': [],
                                'CEE': [],
                                'codigo_informe': [],
                                'codigo_etiqueta': [],
                                'viewstate': []}
    else: 
        evals_page_dict = {'identificacion_vivienda': [],
                           'tipologia': [],
                           'comuna': [],
                           'proyecto': [],
                            'CE': [],
                            'CEE': [],
                            'codigo_informe': [],
                            'codigo_etiqueta': [],
                            'viewstate': []}
    
    # Find the maximum length among all lists in the dictionary
    max_length = max(len(lst) for lst in evals_page_dict.values())
    # Iterate through the dictionary and pad lists with None if they are shorter than the maximum length
    for key, lst in evals_page_dict.items():
        if len(lst) < max_length:
            lst.extend([None] * (max_length - len(lst)))

    # Data Frame
    df = pd.DataFrame.from_dict(evals_page_dict)
    #evals_page_dict
    return df