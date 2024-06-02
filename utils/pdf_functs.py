import pandas as pd
import fitz  # PyMuPDF
import os
import fnmatch

def find_pdf_files(directory):
    pdf_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if fnmatch.fnmatch(filename, '*.pdf'):
                pdf_files.append(os.path.join(root, filename))
    return pdf_files

def extract_text_from_area(page, area):
    """
    Extract text from a specific area of a PDF page.

    Args:
    - page (fitz.Page): Page object from which to extract text.
    - area (tuple): Tuple containing (x1, y1, x2, y2) coordinates of the area to extract text from.

    Returns:
    - extracted_text (str): Text extracted from the specified area.
    """
    extracted_text = ""
    try:
        # Clean the page contents to avoid misplaced item insertions
        page.clean_contents()

        # Pdf Report Dimensions
        report_width = 215.9  # mm
        report_height = 330.0  # mm

        # Get page dimensions
        width = page.rect.width
        height = page.rect.height

        # Normalize the coordinates
        x1, y1, x2, y2 = area
        rx1, ry1, rx2, ry2 = x1 / report_width, y1 / report_height, x2 / report_width, y2 / report_height

        # Define the rectangle area to extract text from
        rect = fitz.Rect(rx1 * width, ry1 * height, rx2 * width, ry2 * height)

        # Extract text from the specified area
        extracted_text = page.get_textbox(rect)
    except Exception as e:
        print(f"Error: {e}")

    return extracted_text

def _from_procentaje_ahorro_to_letra(porcentaje_ahorro: float) -> str:
        """
        Convert a savings percentage to a corresponding letter grade.

        Args:
        - porcentaje_ahorro (float): The savings percentage value, should be between -1 and 100.

        Returns:
        - letra (str): The corresponding letter grade based on the savings percentage.
        """
        if porcentaje_ahorro > 0.85 and porcentaje_ahorro <= 100:
            letra = 'A+'
        elif porcentaje_ahorro > 0.7 and porcentaje_ahorro <= 0.85:
            letra = 'A'
        elif porcentaje_ahorro > 0.55 and porcentaje_ahorro <= 0.7:
            letra = 'B'
        elif porcentaje_ahorro > 0.4 and porcentaje_ahorro <= 0.55:
            letra = 'C'
        elif porcentaje_ahorro > 0.2 and porcentaje_ahorro <= 0.4:
            letra = 'D'
        elif porcentaje_ahorro > -0.1 and porcentaje_ahorro <= 0.20:        
            letra = 'E'
        elif porcentaje_ahorro > -0.35 and porcentaje_ahorro <= -0.1:        
            letra = 'F'
        elif porcentaje_ahorro <= -0.35:
            letra = 'G'
        else:
            letra = None
        return letra

def scrape_informe_cev_v2_pagina1(pdf_file_path):
    # Informe CEV (v.2) - Page 1

    pdf_report = fitz.open(pdf_file_path)
    page_number = 0  # Page number (starting from 0)
    page = pdf_report[page_number]

    ### Seccion 1: Datos vivienda y Evaluación

    area_coordinates = (8.3, 10.3, 165.6, 65.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    datos_vivienda = extracted_text.splitlines()[-8:]
    datos_vivienda

    index = ['tipo_evaluacion', 'codigo_evaluacion', 'region', 'comuna', 'direccion', 'rol_vivienda_proyecto', 'tipo_vivienda', 'superficie_interior_util_m2']


    # ### Convert list to dictionary
    _dict = dict(zip(index, datos_vivienda))
    _dict['tipo_evaluacion'] = _dict['tipo_evaluacion'].title()
    _dict['superficie_interior_util_m2'] = float(_dict['superficie_interior_util_m2'].replace(',', '.'))

    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(_dict, orient='index').T
    
    # ### Seccion 2: Letra de eﬁciencia energética - Diseño de arquitectura
    area_coordinates = (5.6, 78.6, 165.8, 191.3)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    porcentaje_ahorro_list = extracted_text.splitlines()

    porcentaje_ahorro = None
    for item in porcentaje_ahorro_list:
        if item.replace('-', '').isdigit():
            porcentaje_ahorro = int(item)
            break
    df['porcentaje_ahorro'] = porcentaje_ahorro
    df['letra_eficiencia_energetica_dem'] = _from_procentaje_ahorro_to_letra(porcentaje_ahorro/100)
    
    ### Section 3: Requerimientos anuales de energía para calefacción y enfriamiento

    ### Subsection 1: Demanda energética para calefacción
    area_coordinates = (15.6, 220.0, 73.0, 230.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_calefaccion_kwh_m2_ano = float(extracted_text.splitlines()[-1].replace(',', '.'))
    df['demanda_calefaccion_kwh_m2_ano'] = demanda_calefaccion_kwh_m2_ano
    
    ### Subsection 2: Demanda energética para enfriamiento
    area_coordinates = (90.0, 220.0, 151.5, 230.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_enfriamiento_kwh_m2_ano = float(extracted_text.splitlines()[-1].replace(',', '.'))
    df['demanda_enfriamiento_kwh_m2_ano'] = demanda_enfriamiento_kwh_m2_ano

    ### Subsection 3: Demanda energética total
    area_coordinates = (167.0, 225.0, 209.0, 245.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_total_kwh_m2_ano = float(extracted_text.splitlines()[-1].replace(',', '.'))
    df['demanda_total_kwh_m2_ano'] = demanda_total_kwh_m2_ano

    # ### Subsection 4: Fecha de Emision
    area_coordinates = (35.5, 247.5, 57.0, 255.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    emitida_el = extracted_text.splitlines()[-1]
    emitida_el
    df['emitida_el'] = emitida_el
    # Close the PDF document
    pdf_report.close()
    # END
    return df

def scrape_informe_cev_v2_pagina2(pdf_file_path):
    # Informe CEV (v.2) - Page 1

    pdf_report = fitz.open(pdf_file_path)
    page_number = 1  # Page number (starting from 0)
    page = pdf_report[page_number]
    # ## Pagina 2

    # ### Seccion 1: Datos vivienda y Evaluación
    # #### Subsection 1: Izquierda
    area_coordinates = (7.8, 46.3, 96.8, 74.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    datos_vivienda = extracted_text.splitlines()[-5:]
    # Swap the elements
    datos_vivienda[2], datos_vivienda[3] = datos_vivienda[3], datos_vivienda[2]

    index = ['region', 'comuna', 'direccion', 'rol_vivienda', 'tipo_vivienda']

    _dict = dict(zip(index, datos_vivienda))
    _dict

    # Convert dictionary to DataFrame
    df1 = pd.DataFrame.from_dict(_dict, orient='index').T

    # #### Subsection 2: Derecha
    area_coordinates = (98.6, 46.3, 209.3, 74.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    datos_vivienda = extracted_text.splitlines()[-5:]
    
    # Swap the elements
    datos_vivienda[2], datos_vivienda[3] = datos_vivienda[3], datos_vivienda[2]

    index = ['zona_termica', 'superficie_interior_util_m2', 'solicitado_por', 'evaluado_por', 'codigo_evaluacion']
    _dict = dict(zip(index, datos_vivienda))
    _dict['superficie_interior_util_m2'] = float(_dict['superficie_interior_util_m2'].replace(',', '.'))

    # Convert dictionary to DataFrame
    df2 = pd.DataFrame.from_dict(_dict, orient='index').T

    df = pd.concat([df1, df2], axis=1)

    # ### Seccion 2: Demanda energética promedio según tipología y zona térmica (kWh/m2 año)

    # #### Subsection: Demanda Energetica para Calefaccion
    area_coordinates = (99.1, 99.1, 135.3, 105.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_calefaccion_kwh_m2_ano = extracted_text.split('\n')[-1]
    df['demanda_calefaccion_kwh_m2_ano'] = float(demanda_calefaccion_kwh_m2_ano.replace(',', '.'))

    # #### Subsection: Demanda Energetica para Enfriamiento

    area_coordinates = (99.1, 120.5, 135.3, 126.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_enfriamiento_kwh_m2_ano = extracted_text.split('\n')[-1]
    df['demanda_enfriamiento_kwh_m2_ano'] = float(demanda_enfriamiento_kwh_m2_ano.replace(',', '.'))

    # #### Subsection: Demanda Energetica Total
    area_coordinates = (99.1, 137.4, 135.3, 150.4)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_total_kwh_m2_ano = extracted_text.split('\n')[-1]
    df['demanda_total_kwh_m2_ano'] = float(demanda_total_kwh_m2_ano.replace(',', '.'))

    # ### Seccion 3
    # ### Subsection 1: Demanda Energética Total
    area_coordinates = (39.2, 159.8, 122.8, 166.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_total_bis_kwh_m2_ano = extracted_text.split('\n')[-1]
    df['demanda_total_bis_kwh_m2_ano'] = float(demanda_total_bis_kwh_m2_ano.replace(',', '.'))

    # ### Subsection 2: Demanda Energética Total de Referencia
    area_coordinates = (16.9, 168.3, 146.2, 173.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_total_referencia_kwh_m2_ano = extracted_text.split('\n')[-1]
    df['demanda_total_referencia_kwh_m2_ano'] = float(demanda_total_referencia_kwh_m2_ano.replace(',', '.'))

    # ### Porcentaje de Ahorro
    area_coordinates = (152.0, 162.6, 201.5, 168.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    porcentaje_ahorro = extracted_text.split('\n')[-1]
    df['porcentaje_ahorro'] = float(porcentaje_ahorro.replace(',', '.'))

    # ### Seccion 4: Principales características del Diseño de Arquitectura
    # ### Muro Principal

    # Muro principal: Descripcion
    # Define section coordinates
    area_coordinates = (46.2, 202.2, 184.5, 209.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    muro_principal_descripcion = extracted_text.replace('\n', '')
    df['muro_principal_descripcion'] = muro_principal_descripcion

    # Muro principal: Exigencia
    # Define section coordinates
    area_coordinates = (185.5, 202.2, 209.5, 209.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    muro_principal_exigencia = extracted_text.split('\n')[-1]
    try:
        df['muro_principal_exigencia_W_m2_K'] = float(muro_principal_exigencia.replace('[W/m2K]', '').replace(',', '.'))
    except ValueError:
        df['muro_principal_exigencia_W_m2_K'] = None
        
    # ### Muro Secundario
    # Muro secundario: Descripcion
    # Define section coordinates
    area_coordinates = (46.2, 209.2, 184.5, 215.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    muro_secundario_descripcion = extracted_text.replace('\n', '')
    df['muro_secundario_descripcion'] = muro_secundario_descripcion if muro_secundario_descripcion != '0' else None


    # Muro secundario: Exigencia
    # Define section coordinates
    area_coordinates = (185.5, 202.2, 209.5, 209.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    muro_secundario_exigencia = extracted_text.split('\n')[-1]
    try:
        df['muro_secundario_exigencia_W_m2_K'] = float(muro_secundario_exigencia.replace('[W/m2K]', '').replace(',', '.'))
    except ValueError:
        df['muro_secundario_exigencia_W_m2_K'] = None
        

    # ### Piso Principal
    # Piso principal: Descripcion
    # Define section coordinates
    area_coordinates = (46.2, 216.4, 184.5, 223.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    piso_principal_descripcion = extracted_text.replace('\n', '')
    df['piso_principal_descripcion'] = piso_principal_descripcion

    # Piso principal: Exigencia
    area_coordinates = (185.5, 216.4, 209.5, 223.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    piso_principal_exigencia = extracted_text.split('\n')[-1]
    try:
        df['piso_principal_exigencia_W_m2_K'] = float(piso_principal_exigencia.replace('[W/m2K]', '').replace(',', '.'))
    except ValueError:
        df['piso_principal_exigencia_W_m2_K'] = None

    # ### Puerta principal
    # Puerta principal: Descripcion
    area_coordinates = (46.2, 223.5, 184.5, 230.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    puerta_principal_descripcion = extracted_text.replace('\n', '')
    df['puerta_principal_descripcion'] = puerta_principal_descripcion

    # Puerta principal: Exigencia
    # Define section coordinates
    area_coordinates  = (185.5, 223.9, 209.5, 230.2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    puerta_principal_exigencia = extracted_text.strip()
    df['puerta_principal_exigencia_W_m2_K'] = puerta_principal_exigencia if puerta_principal_exigencia.isalpha() else None

    # ### Techo Principal

    # Techo principal: Descripcion
    area_coordinates = (46.2, 230.5, 184.5, 237.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    techo_principal_descripcion = extracted_text.replace('\n', '')
    df['techo_principal_descripcion'] = techo_principal_descripcion

    # Techo principal: Exigencia
    # Define section coordinates
    area_coordinates  = (185.5, 230.5, 209.5, 237.2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    techo_principal_exigencia = extracted_text.strip()
    try:
        df['techo_principal_exigencia_W_m2_K'] = float(techo_principal_exigencia.replace('[W/m2K]', '').replace(',', '.'))
    except ValueError:
        df['techo_principal_exigencia_W_m2_K'] = None

    # ### Techo Secundario
    # Techo secundario: Descripcion
    area_coordinates = (46.2, 237.2, 184.5, 244.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    techo_secundario_descripcion = extracted_text.replace('\n', '')
    df['techo_secundario_descripcion'] = techo_secundario_descripcion if techo_secundario_descripcion != '0' else None

    # Techo secundario: Exigencia
    # Define section coordinates
    area_coordinates  = (185.5, 237.2, 209.5, 244.1)
    extracted_text = extract_text_from_area(page, area_coordinates)
    techo_secundario_exigencia = extracted_text.strip()
    try:
        df['techo_secundario_exigencia_W_m2_K'] = float(techo_secundario_exigencia.replace('[W/m2K]', '').replace(',', '.'))
    except ValueError:
        df['techo_secundario_exigencia_W_m2_K'] = None

    # ### Superficie vidriada principal
    # Superficie vidriada principal: Descripcion
    area_coordinates = (46.2, 244.2, 184.5, 251.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    superficie_vidriada_principal_descripcion = extracted_text.replace('\n', '')
    df['superficie_vidriada_principal_descripcion'] = superficie_vidriada_principal_descripcion

    # Superficie vidriada principal: Exigencia
    # Define section coordinates
    area_coordinates  = (185.5, 244.3, 209.5, 251.0)
    extracted_text = extract_text_from_area(page, area_coordinates)
    superficie_vidriada_principal_exigencia = extracted_text.strip()
    df['superficie_vidriada_principal_exigencia'] = superficie_vidriada_principal_exigencia.strip() if superficie_vidriada_principal_exigencia.isalpha() else None

    # ### Superficie vidriada secundaria
    # Superficie vidriada secundaria: Descripcion
    area_coordinates = (46.2, 251.3, 184.5, 258.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    superficie_vidriada_secundaria_descripcion = extracted_text.replace('\n', '')
    df['superficie_vidriada_secundaria_descripcion'] = superficie_vidriada_secundaria_descripcion if superficie_vidriada_secundaria_descripcion != '0' else None


    # Superficie vidriada secundaria: Exigencia
    # Define section coordinates
    area_coordinates  = (185.5, 251.3, 209.5, 258.0)
    extracted_text = extract_text_from_area(page, area_coordinates)
    superficie_vidriada_secundaria_exigencia = extracted_text.strip()
    df['superficie_vidriada_secundaria_exigencia'] = superficie_vidriada_secundaria_exigencia.strip() if superficie_vidriada_secundaria_exigencia.isalpha() else None

    # ### Ventilación (RAH)
    # Ventilación (RAH): Descripcion
    area_coordinates = (46.2, 258.3, 184.5, 265.0)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ventilacion_rah_descripcion = extracted_text
    df['ventilacion_rah_descripcion'] = ventilacion_rah_descripcion.replace('\n', '').strip()

    # Ventilación (RAH): Exigencia
    # Define section coordinates
    area_coordinates = (185.5, 258.3, 209.5, 265.0)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ventilacion_rah_exigencia = extracted_text
    df['ventilacion_rah_exigencia'] = ventilacion_rah_exigencia.strip()

    # ### Inﬁltraciones (RAH)
    # Infiltraciones (RAH): Descripcion
    area_coordinates = (46.2, 265.3, 184.5, 272.0)
    extracted_text = extract_text_from_area(page, area_coordinates)
    infiltraciones_rah_descripcion = extracted_text
    df['infiltraciones_rah_descripcion'] = infiltraciones_rah_descripcion.replace('\n', '').strip()

    # Infiltraciones (RAH): Exigencia
    area_coordinates = (185.5, 265.3, 209.5, 272.0)
    extracted_text = extract_text_from_area(page, area_coordinates)
    infiltraciones_rah_exigencia = extracted_text
    df['infiltraciones_rah_exigencia'] = infiltraciones_rah_exigencia.replace('\n', '').strip()
    # Close the PDF document
    pdf_report.close()

    # ### END
    return df

def scrape_informe_cev_v2_pagina3_consumos(pdf_file_path):

    # # Informe CEV (v.2) - Page 3
    pdf_report = fitz.open(pdf_file_path)
    page_number = 2  # Page number (starting from 0)
    page = pdf_report[page_number]


    # ## Pagina 3
    # Código evaluación energética
    area_coordinates = (62.3, 30.7, 88.1, 35.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    codigo_evaluacion = extracted_text
    codigo_evaluacion

    df = pd.DataFrame(data=[codigo_evaluacion], columns=['codigo_evaluacion'])
 
    # ## DISTRIBUCIÓN DEL CONSUMO ENERGÉTICO ARQUITECTURA + EQUIPOS + TIPO DE ENERGÍA
    ## Agua caliente sanitaria
    area_coordinates = (78.1, 73.9, 98.0, 76.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    agua_caliente_sanitaria_kwh_m2 = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['agua_caliente_sanitaria_kwh_m2'] = agua_caliente_sanitaria_kwh_m2

    area_coordinates = (98.7, 73.9, 116.3, 76.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    agua_caliente_sanitaria_perc = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['agua_caliente_sanitaria_perc'] = agua_caliente_sanitaria_perc
   
    ## Iluminación
    area_coordinates = (79.2, 78.1, 98.3, 81.4)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_kwh_m2 = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['iluminacion_kwh_m2'] = iluminacion_kwh_m2
   
    area_coordinates = (98.7, 78.1, 116.3, 81.4)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_per = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['iluminacion_per'] = iluminacion_per
  
    # Calefacción
    area_coordinates = (79.2, 82.2, 98.3, 86.6)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_kwh_m2 = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['calefaccion_kwh_m2'] = calefaccion_kwh_m2
   
    area_coordinates = (98.7, 82.2, 116.3, 86.6)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_kwh_per = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['calefaccion_kwh_per'] = calefaccion_kwh_per

    # Energía renovable no convencional
    area_coordinates = (79.2, 87.2, 98.3, 91.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ernc_kwh_m2 = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['energia_renovable_no_convencional_kwh_m2'] = ernc_kwh_m2
 
    area_coordinates = (98.7, 87.2, 116.3, 91.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ernc_per = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['energia_renovable_no_convencional_per'] = ernc_per
 
    # Consumo Total por m²
    area_coordinates = (118.0, 74.0, 148.0, 86.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumo_kwh_m2 = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['consumo_total_kwh_m2'] = consumo_kwh_m2
  
    # Emisiones de CO2e
    area_coordinates = (171.5, 69.0, 183.5, 74.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    emisiones_kgco2_m2_ano = float(extracted_text.replace(',', '.')) if extracted_text.replace(',', '.').replace('.', '', 1).isdigit() else None
    df['emisiones_kgco2_m2_ano'] = emisiones_kgco2_m2_ano
  
    # Calefacción
    area_coordinates = (76.6, 101.4, 155.5, 105.3)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_descripcion_proy = extracted_text.strip()
    df['calefaccion_descripcion_proy'] = calefaccion_descripcion_proy
 
    area_coordinates = (157.0, 101.4, 196.0, 105.3)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_consumo_proy_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['calefaccion_consumo_proy_kwh'] = float(calefaccion_consumo_proy_kwh.replace(',', '.')) if calefaccion_consumo_proy_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
  
    area_coordinates = (198.0, 101.4, 207.0, 105.3)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_consumo_proy_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['calefaccion_consumo_proy_per'] = float(calefaccion_consumo_proy_per) if calefaccion_consumo_proy_per.replace(',', '.').replace('.', '', 1).isdigit() else None
  
    # Iluminación
    area_coordinates = (76.6, 106.2, 155.5, 110.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_descripcion_proy = extracted_text.split('\n')[0].strip()
    df['iluminacion_descripcion_proy'] = iluminacion_descripcion_proy
  
    area_coordinates = (157.0, 106.2, 196.0, 110.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_consumo_proy_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['iluminacion_consumo_proy_kwh'] = float(iluminacion_consumo_proy_kwh) if iluminacion_consumo_proy_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
   
    area_coordinates = (198.0, 106.2, 207.0, 110.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_consumo_proy_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['iluminacion_consumo_proy_per'] = float(iluminacion_consumo_proy_per) if iluminacion_consumo_proy_per.replace(',', '.').replace('.', '', 1).isdigit() else None
    
    # Agua Caliente Sanitaria
    area_coordinates = (76.6, 111.2, 155.5, 115.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    acs_descripcion_proy = extracted_text
    df['agua_caliente_sanitaria_descripcion_proy'] = acs_descripcion_proy
    
    area_coordinates = (157.0, 111.2, 196.0, 115.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    acs_consumo_proy_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['agua_caliente_sanitaria_consumo_proy_kwh'] = float(acs_consumo_proy_kwh) if acs_consumo_proy_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
    
    area_coordinates = (198.0, 111.2, 207.0, 115.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    acs_consumo_proy_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['agua_caliente_sanitaria_consumo_proy_per'] = float(acs_consumo_proy_per) if acs_consumo_proy_per.replace(',', '.').replace('.', '', 1).isdigit() else None
    
    # Energía renovable no convencional
    area_coordinates = (76.6, 115.8, 155.5, 120.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    enrc_descripcion_proy = extracted_text.split('\n')[0].strip()
    df['energia_renovable_no_convencional_descripcion_proy'] = enrc_descripcion_proy
   
    area_coordinates = (157.0, 115.8, 196.0, 120.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ernc_consumo_proy_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['energia_renovable_no_convencional_consumo_proy_kwh'] = float(ernc_consumo_proy_kwh) if ernc_consumo_proy_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (198.0, 115.8, 207.0, 120.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ernc_consumo_proy_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['energia_renovable_no_convencional_consumo_proy_per'] = float(ernc_consumo_proy_per) if ernc_consumo_proy_per.replace(',', '.').replace('.', '', 1).isdigit() else None
   
    area_coordinates = (157.0, 121.0, 196.0, 125.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumo_total_proy_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['consumo_total_requerido_proy_kwh'] = float(consumo_total_proy_kwh) if consumo_total_proy_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    # ### Equipos de referencia

   # Calefacción
    area_coordinates = (76.6, 136.1, 155.5, 140.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_descripcion_ref = extracted_text.strip()
    df['calefaccion_descripcion_ref'] = calefaccion_descripcion_ref
 
    area_coordinates = (157.0, 136.1, 196.0, 140.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_consumo_ref_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['calefaccion_consumo_ref_kwh'] = float(calefaccion_consumo_ref_kwh) if calefaccion_consumo_ref_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (198.0, 136.1, 207.0, 140.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    calefaccion_consumo_ref_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['calefaccion_consumo_ref_per'] = float(calefaccion_consumo_ref_per) if calefaccion_consumo_ref_per.replace(',', '.').replace('.', '', 1).isdigit() else None
  
    # Iluminación
    area_coordinates = (76.6, 140.7, 155.5, 144.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_descripcion_ref = extracted_text.split('\n')[0].strip()
    df['iluminacion_descripcion_ref'] = iluminacion_descripcion_ref

    area_coordinates = (157.0, 140.7, 196.0, 144.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_consumo_ref_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['iluminacion_consumo_ref_kwh'] = float(iluminacion_consumo_ref_kwh) if iluminacion_consumo_ref_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (198.0, 140.7, 207.0, 144.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    iluminacion_consumo_ref_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['iluminacion_consumo_ref_per'] = float(iluminacion_consumo_ref_per) if iluminacion_consumo_ref_per.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    # Agua Caliente Sanitaria
    area_coordinates = (76.6, 145.2, 155.5, 149.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    acs_descripcion_ref = extracted_text
    df['agua_caliente_sanitaria_descripcion_ref'] = acs_descripcion_ref
  
    area_coordinates = (157.0, 145.2, 196.0, 149.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    acs_consumo_ref_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['agua_caliente_sanitaria_consumo_ref_kwh'] = float(acs_consumo_ref_kwh) if acs_consumo_ref_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (198.0, 145.2, 207.0, 149.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    acs_consumo_ref_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['agua_caliente_sanitaria_consumo_ref_per'] = float(acs_consumo_ref_per) if acs_consumo_ref_per.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    # Energía renovable no convencional
    area_coordinates = (76.6, 150.8, 155.5, 154.8)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    enrc_descripcion_ref = extracted_text.split('\n')[0].strip()
    df['energia_renovable_no_convencional_descripcion_ref'] = enrc_descripcion_ref
  
    area_coordinates = (157.0, 150.8, 196.0, 154.8)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ernc_consumo_ref_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['energia_renovable_no_convencional_consumo_ref_kwh'] = float(ernc_consumo_ref_kwh) if ernc_consumo_ref_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (198.0, 150.8, 207.0, 154.8)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    ernc_consumo_ref_per = extracted_text.split('\n')[-1].replace(',', '.')
    df['energia_renovable_no_convencional_consumo_ref_per'] = float(ernc_consumo_ref_per) if ernc_consumo_ref_per.replace(',', '.').replace('.', '', 1).isdigit() else None
   
    area_coordinates = (157.0, 156.0, 196.0, 160.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumo_total_ref_kwh = extracted_text.split('\n')[-1].replace(',', '.')
    df['consumo_total_requerido_ref_kwh'] = float(consumo_total_ref_kwh) if consumo_total_ref_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None
  
    # ### REQUERIMIENTOS DE ENERGÍA (kWh/año)
    # #### CONSUMOS SIN INCLUIR ERNC

    area_coordinates = (87.0, 176.0, 104.0, 179.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumos_sin_incluir_ernc_calef = extracted_text.replace(',', '.')
    df['consumo_ep_calefaccion_kwh'] = float(consumos_sin_incluir_ernc_calef) if consumos_sin_incluir_ernc_calef.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (87.0, 180.0, 104.0, 183.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumos_sin_incluir_ernc_acs = extracted_text.replace(',', '.')
    df['consumo_ep_agua_caliente_sanitaria_kwh'] = float(consumos_sin_incluir_ernc_acs) if consumos_sin_incluir_ernc_acs.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (87.0, 184.0, 104.0, 187.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumos_sin_incluir_ernc_ilum = extracted_text.replace(',', '.')
    df['consumo_ep_iluminacion_kwh'] = float(consumos_sin_incluir_ernc_ilum) if consumos_sin_incluir_ernc_ilum.replace(',', '.').replace('.', '', 1).isdigit() else None

    area_coordinates = (87.0, 188.0, 104.0, 191.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumos_sin_incluir_ernc_vent = extracted_text.replace(',', '.')
    df['consumo_ep_ventiladores_kwh'] = float(consumos_sin_incluir_ernc_vent) if consumos_sin_incluir_ernc_vent.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    # #### GENERACIÓN FOTOVOLTAICA EN LA VIVIENDA
    area_coordinates = (87.0, 199.0, 104.0, 202.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    generacion_fotovoltaica_ep = extracted_text.replace(',', '.')
    df['generacion_ep_fotovoltaicos_kwh'] = float(generacion_fotovoltaica_ep) if generacion_fotovoltaica_ep.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (87.0, 203.2, 104.0, 206.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    generacion_fotovoltaica_aporte = extracted_text.replace(',', '.')
    df['aporte_fotovoltaicos_consumos_basicos_kwh'] = float(generacion_fotovoltaica_aporte) if generacion_fotovoltaica_aporte.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (87.0, 206.9, 104.0, 210.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    generacion_fotovoltaica_consumo = extracted_text.replace(',', '.')
    df['diferencia_fotovoltaica_para_consumo_kwh'] = float(generacion_fotovoltaica_consumo) if generacion_fotovoltaica_consumo.replace(',', '.').replace('.', '', 1).isdigit() else None
   
    # #### DISTRIBUCIÓN DEL APORTE DE SOLAR TÉRMICA

    area_coordinates = (87.0, 218.0, 104.0, 221.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    aporte_solar_termica_calef = extracted_text.replace(',', '.')
    df['aporte_solar_termica_consumos_basicos_kwh'] = float(aporte_solar_termica_calef) if aporte_solar_termica_calef.replace(',', '.').replace('.', '', 1).isdigit() else None
   
    area_coordinates = (87.0, 222.5, 104.0, 225.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    aporte_solar_termica_acs = extracted_text.replace(',', '.')
    df['aporte_solar_termica_agua_caliente_sanitaria_kwh'] = float(aporte_solar_termica_acs) if aporte_solar_termica_acs.replace(',', '.').replace('.', '', 1).isdigit() else None

    # #### BALANCE GENERAL DE ENERGÍA
    area_coordinates = (192.0, 176.0, 208.0, 179.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    balance_general_energia_antes = extracted_text.replace(',', '.')
    df['total_consumo_ep_antes_fotovoltaica_kwh'] = float(balance_general_energia_antes) if balance_general_energia_antes.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (192.0, 180.0, 208.0, 183.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    balance_general_energia_aporte_fv = extracted_text.replace(',', '.')
    df['aporte_fotovoltaicos_consumos_basicos_kwh_bis'] = float(balance_general_energia_aporte_fv) if balance_general_energia_aporte_fv.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    area_coordinates = (192.0, 184.3, 208.0, 187.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    balance_general_energia_suplir = extracted_text.replace(',', '.')
    df['consumos_basicos_a_suplir_kwh'] = float(balance_general_energia_suplir) if balance_general_energia_suplir.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    # #### RESUMEN DE CONSUMOS FINALES DE REFERENCIA Y OBJETO
    area_coordinates = (192.0, 199.0, 208.0, 202.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumo_total_ep_obj_kwh = extracted_text.replace(',', '.')
    df['consumo_total_ep_obj_kwh'] = float(consumo_total_ep_obj_kwh) if consumo_total_ep_obj_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None

    area_coordinates = (192.0, 202.8, 208.0, 206.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    consumo_total_ep_ref_kwh = extracted_text.replace(',', '.')
    df['consumo_total_ep_ref_kwh'] = float(consumo_total_ep_ref_kwh) if consumo_total_ep_ref_kwh.replace(',', '.').replace('.', '', 1).isdigit() else None

    area_coordinates = (192.0, 207.0, 208.0, 210.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    coeficiente_energetico_c = extracted_text.replace(',', '.')
    df['coeficiente_energetico_c'] = float(coeficiente_energetico_c) if coeficiente_energetico_c.replace(',', '.').replace('.', '', 1).isdigit() else None
 
    # Close the PDF document
    pdf_report.close()
    return df

def scrape_informe_cev_v2_pagina3_envolvente(pdf_file_path):
    # ### Load the PDF
    pdf_report = fitz.open(pdf_file_path)
    page_number = 2  # Page number (starting from 0)
    page = pdf_report[page_number]

    # ## Pagina 3
    # Código evaluación energética
    area_coordinates = (62.3, 30.7, 88.1, 35.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    codigo_evaluacion = extracted_text
    df = pd.DataFrame(data=[codigo_evaluacion] * 10, columns=['codigo_evaluacion'])

    # ### Seccion: Resumen Envolvente

    orientacion = ['Horiz', 'N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO', 'Pisos']
    df['orientacion'] = orientacion

    # ### Elementos Opacos
    area_coordinates = (19.5, 245.0, 47.0, 287.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    elementos_opacos_area_m2 = extracted_text.splitlines()[-10:]
    elementos_opacos_area_m2 = [float(item.replace(',', '.')) for item in elementos_opacos_area_m2]
    df['elementos_opacos_area_m2'] = elementos_opacos_area_m2
    
    area_coordinates = (47.8, 245.0, 60.5, 287.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    elementos_opacos_U_W_m2_K = extracted_text.splitlines()[-10:]
    elementos_opacos_U_W_m2_K = [float(item.replace(',', '.')) for item in elementos_opacos_U_W_m2_K]
    df['elementos_opacos_U_W_m2_K'] = elementos_opacos_U_W_m2_K
    df


    # ### Elementos Traslucidos
    area_coordinates = (68.2, 245.0, 89.5, 287.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    elementos_traslucidos_area_m2 = extracted_text.splitlines()[-9:]
    elementos_traslucidos_area_m2 = [float(item.replace(',', '.')) for item in elementos_traslucidos_area_m2]
    elementos_traslucidos_area_m2.append(0)
    df['elementos_traslucidos_area_m2'] = elementos_traslucidos_area_m2

    area_coordinates = (90.4, 245.0, 103.1, 287.5)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    elementos_traslucidos_U_W_m2_K = extracted_text.splitlines()[-9:]
    elementos_traslucidos_U_W_m2_K = [float(item.replace(',', '.')) for item in elementos_traslucidos_U_W_m2_K]
    elementos_traslucidos_U_W_m2_K.append(0)
    df['elementos_traslucidos_U_W_m2_K'] = elementos_traslucidos_U_W_m2_K
   
    # ### Perdidas Puentes Termicos

    # ### P01
    p01_W_K = []
    dy = 3.5
    for n in range(0, 9):
        area_coordinates = (114.1, 250.0+n*dy, 125.5, 253.5+n*dy)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
        extracted_text = extract_text_from_area(page, area_coordinates)
        p01_W_K_i = extracted_text.splitlines()[-1]
        p01_W_K_i = float(p01_W_K_i.replace(',', '.'))
        p01_W_K.append(p01_W_K_i)

    p01_W_K.pop(4)
    p01_W_K.insert(0, 0)
    p01_W_K.append(0)
    df['P01_W_K'] = p01_W_K

    # ### P02
    p02_W_K = []
    dy = 3.5
    for n in range(0, 9):
        area_coordinates = (126.2, 250.0+n*dy, 136.9, 253.5+n*dy)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
        extracted_text = extract_text_from_area(page, area_coordinates)
        p02_W_K_i = extracted_text.splitlines()[-1]
        p02_W_K_i = float(p02_W_K_i.replace(',', '.'))
        p02_W_K.append(p02_W_K_i)

    p02_W_K.pop(4)
    p02_W_K.insert(0, 0)
    p02_W_K.append(0)
    df['P02_W_K'] = p02_W_K

    # ### P03
    p03_W_K = []
    dy = 3.5
    for n in range(0, 9):
        #print(n)
        area_coordinates = (137.0, 250.0+n*dy, 148.2, 253.5+n*dy)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
        extracted_text = extract_text_from_area(page, area_coordinates)
        p03_W_K_i = extracted_text.splitlines()[-1]
        p03_W_K_i = float(p03_W_K_i.replace(',', '.'))
        p03_W_K.append(p03_W_K_i)

    p03_W_K.pop(4)
    p03_W_K.insert(0, 0)
    p03_W_K.append(0)
    df['P03_W_K'] = p03_W_K
   
    # ### P04
    p04_W_K = []
    dy = 3.5
    for n in range(0, 9):
        #print(n)
        area_coordinates = (149.0, 250.0+n*dy, 160.0, 253.5+n*dy)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
        extracted_text = extract_text_from_area(page, area_coordinates)
        p04_W_K_i = extracted_text.splitlines()[-1]
        p04_W_K_i = float(p04_W_K_i.replace(',', '.'))
        p04_W_K.append(p04_W_K_i)

    p04_W_K.pop(4)  
    p04_W_K.insert(0, 0)
    p04_W_K.append(0)
    df['P04_W_K'] = p04_W_K
  
    # ### P05
    p05_W_K = []
    dy = 3.5
    for n in range(0, 9):
        #print(n)
        area_coordinates = (161.3, 250.0+n*dy, 171.2, 253.5+n*dy)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
        extracted_text = extract_text_from_area(page, area_coordinates)
        p05_W_K_i = extracted_text.splitlines()[-1]
        p05_W_K_i = float(p05_W_K_i.replace(',', '.'))
        p05_W_K.append(p05_W_K_i)

    p05_W_K.pop(4) 
    p05_W_K.insert(0, 0)
    p05_W_K.append(0)
    df['P05_W_K'] = p05_W_K
    
    Ht_W_K = []
    dy = 3.5
    for n in range(0, 12):
        #print(n)
        area_coordinates = (189.2, 245.5+n*dy, 201.9, 249.0+n*dy)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
        extracted_text = extract_text_from_area(page, area_coordinates)
        Ht_W_K_i = extracted_text.splitlines()[-1]
        Ht_W_K_i = float(Ht_W_K_i.replace(',', '.'))
        Ht_W_K.append(Ht_W_K_i)
    Ht_W_K.pop(4) 
    Ht_W_K.pop(9) 
    df['UA_phiL'] = Ht_W_K
 
    # df['elementos_opacos_area_m2'] * df['elementos_opacos_U_W_m2_K'] + df['elementos_traslucidos_area_m2'] * df['elementos_traslucidos_U_W_m2_K'] + df['P01_W_K'] + df['P02_W_K'] + df['P03_W_K'] + df['P04_W_K'] + df['P05_W_K']
   
    # Close the PDF document
    pdf_report.close()
    return df



def scrape_informe_cev_v2_pagina4(pdf_file_path):
    # # Informe CEV (v.2) - Page 4
    pdf_report = fitz.open(pdf_file_path)
    page_number = 3  # Page number (starting from 0)
    page = pdf_report[page_number]


    # ## Pagina 4
    area_coordinates = (62.3, 30.7, 88.1, 35.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    codigo_evaluacion = extracted_text

    # Create DataFrame
    df = pd.DataFrame(data=[codigo_evaluacion] * 12, columns=['codigo_evaluacion'])
    df['mes_id'] = range(1, 13)

    # ### Seccion: Demanda Calefaccion
    # #### Vivienda evaluada
    area_coordinates = (41.7, 139.1, 203.4, 143.9)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_calef_viv_eval_kwh = extracted_text.splitlines()
    demanda_calef_viv_eval_kwh = [float(item.replace(',', '.')) for item in demanda_calef_viv_eval_kwh]
    
    # Store a comment column based on length of demanda_calef_viv_eval_kwh
    if len(demanda_calef_viv_eval_kwh) == 12:
        demanda_calef_viv_eval_comment = 'OK'
    else:
        demanda_calef_viv_eval_comment = 'Check!'

    while len(demanda_calef_viv_eval_kwh) < 12:
        demanda_calef_viv_eval_kwh.append(0)
    df['demanda_calef_viv_eval_kwh'] = demanda_calef_viv_eval_kwh
    df['demanda_calef_viv_eval_comment'] = demanda_calef_viv_eval_comment

    # #### Vivienda de referencia
    area_coordinates = (41.7, 144.1, 203.4, 148.2)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_calef_viv_ref_kwh = extracted_text.splitlines()
    demanda_calef_viv_ref_kwh = [float(item.replace(',', '.')) for item in demanda_calef_viv_ref_kwh]

    # Store a comment column based on length of demanda_calef_viv_ref_kwh
    if len(demanda_calef_viv_ref_kwh) == 12:
        demanda_calef_viv_ref_comment = 'OK'
    else:
        demanda_calef_viv_ref_comment = 'Check!'

    while len(demanda_calef_viv_ref_kwh) < 12:
        demanda_calef_viv_ref_kwh.append(0)
    df['demanda_calef_viv_ref_kwh'] = demanda_calef_viv_ref_kwh
    df['demanda_calef_viv_ref_comment'] = demanda_calef_viv_ref_comment

    # ### Seccion: Demanda Enfriamiento
    # Vivienda Evaluada
    area_coordinates = (41.7, 161.1, 203.4, 165.9)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_enfri_viv_eval_kwh = extracted_text.splitlines()
    demanda_enfri_viv_eval_kwh = [float(item.replace(',', '.')) for item in demanda_enfri_viv_eval_kwh]
    
    # Store a comment column based on length of demanda_enfri_viv_eval_kwh
    if len(demanda_enfri_viv_eval_kwh) == 12:
        demanda_enfri_viv_eval_comment = 'OK'
    else:
        demanda_enfri_viv_eval_comment = 'Check!'

    while len(demanda_enfri_viv_eval_kwh) < 12:
        demanda_enfri_viv_eval_kwh.append(0)
    df['demanda_enfri_viv_eval_kwh'] = demanda_enfri_viv_eval_kwh
    df['demanda_enfri_viv_eval_comment'] = demanda_enfri_viv_eval_comment
    
    # Vivienda Referencia
    area_coordinates = (41.7, 166.2, 203.4, 170.3)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    demanda_enfri_viv_ref_kwh = extracted_text.splitlines()
    demanda_enfri_viv_ref_kwh = [float(item.replace(',', '.')) for item in demanda_enfri_viv_ref_kwh]

    # Store a comment column based on length of demanda_enfri_viv_ref_kwh
    if len(demanda_enfri_viv_ref_kwh) == 12:
        demanda_enfri_viv_ref_comment = 'OK'
    else:
        demanda_enfri_viv_ref_comment = 'Check!'

    while len(demanda_enfri_viv_ref_kwh) < 12:
        demanda_enfri_viv_ref_kwh.append(0)
    df['demanda_enfri_viv_ref_kwh'] = demanda_enfri_viv_ref_kwh
    df['demanda_enfri_viv_ref_comment'] = demanda_enfri_viv_ref_comment

    # ### Seccion: Sobrecalentamiento
    # Vivienda Evaluada
    area_coordinates = (41.7, 254.9, 203.4, 258.9)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    sobrecalentamiento_viv_eval_hr = extracted_text.splitlines()
    sobrecalentamiento_viv_eval_hr = [float(item.replace(',', '.')) for item in sobrecalentamiento_viv_eval_hr]

    # Store a comment column based on length of sobrecalentamiento_viv_eval_hr
    if len(sobrecalentamiento_viv_eval_hr) == 12:
        sobrecalentamiento_viv_eval_comment = 'OK'
    else:
        sobrecalentamiento_viv_eval_comment = 'Check!'

    while len(sobrecalentamiento_viv_eval_hr) < 12:
        sobrecalentamiento_viv_eval_hr.append(0)
    df['sobrecalentamiento_viv_eval_hr'] = sobrecalentamiento_viv_eval_hr
    df['sobrecalentamiento_viv_eval_comment'] = sobrecalentamiento_viv_eval_comment


    # Vivienda Referencia
    area_coordinates = (41.7, 259.0, 203.4, 262.9)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    sobrecalentamiento_viv_ref_hr = extracted_text.splitlines()
    sobrecalentamiento_viv_ref_hr = [float(item.replace(',', '.')) for item in sobrecalentamiento_viv_ref_hr]

    # Store a comment column based on length of sobrecalentamiento_viv_ref_hr
    if len(sobrecalentamiento_viv_ref_hr) == 12:
        sobrecalentamiento_viv_ref_comment = 'OK'
    else:
        sobrecalentamiento_viv_ref_comment = 'Check!'

    while len(sobrecalentamiento_viv_ref_hr) < 12:
        sobrecalentamiento_viv_ref_hr.append(0)
    df['sobrecalentamiento_viv_ref_hr'] = sobrecalentamiento_viv_ref_hr
    df['sobrecalentamiento_viv_ref_comment'] = sobrecalentamiento_viv_ref_comment


    # ### Seccion: Sobreenfriamiento
    # Vivienda Evaluada
    area_coordinates = (41.7, 275.0, 203.4, 278.6)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    sobreenfriamiento_viv_eval_hr = extracted_text.splitlines()
    sobreenfriamiento_viv_eval_hr = [float(item.replace(',', '.')) for item in sobreenfriamiento_viv_eval_hr]

    # Store a comment column based on length of sobreenfriamiento_viv_eval_hr
    if len(sobreenfriamiento_viv_eval_hr) == 12:
        sobreenfriamiento_viv_eval_comment = 'OK'
    else:
        sobreenfriamiento_viv_eval_comment = 'Check!'

    while len(sobreenfriamiento_viv_eval_hr) < 12:
        sobreenfriamiento_viv_eval_hr.append(0)
    df['sobreenfriamiento_viv_eval_hr'] = sobreenfriamiento_viv_eval_hr
    df['sobreenfriamiento_viv_eval_comment'] = sobreenfriamiento_viv_eval_comment
 
    # Vivienda Referencia
    area_coordinates = (41.7, 279.0, 203.4, 282.9)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    sobreenfriamiento_viv_ref_hr = extracted_text.splitlines()
    sobreenfriamiento_viv_ref_hr = [float(item.replace(',', '.')) for item in sobreenfriamiento_viv_ref_hr]

    # Store a comment column based on length of sobreenfriamiento_viv_ref_hr
    if len(sobreenfriamiento_viv_ref_hr) == 12:
        sobreenfriamiento_viv_ref_comment = 'OK'
    else:
        sobreenfriamiento_viv_ref_comment = 'Check!'

    while len(sobreenfriamiento_viv_ref_hr) < 12:
        sobreenfriamiento_viv_ref_hr.append(0)
    df['sobreenfriamiento_viv_ref_hr'] = sobreenfriamiento_viv_ref_hr
    df['sobreenfriamiento_viv_ref_comment'] = sobreenfriamiento_viv_ref_comment
    return df


def scrape_informe_cev_v2_pagina5(pdf_file_path):    
    pdf_report = fitz.open(pdf_file_path)
    page_number = 4  # Page number (starting from 0)
    page = pdf_report[page_number]

    # ## Pagina 5
    # Código evaluación energética
    area_coordinates = (62.3, 30.7, 88.1, 35.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    codigo_evaluacion = extracted_text
    codigo_evaluacion

    df = pd.DataFrame(data=[codigo_evaluacion], columns=['codigo_evaluacion'])
    df['content'] = None

    # Close the PDF document
    pdf_report.close()
    return df

def scrape_informe_cev_v2_pagina6(pdf_file_path):
    pdf_report = fitz.open(pdf_file_path)
    page_number = 5  # Page number (starting from 0)
    page = pdf_report[page_number]

    # ## Pagina 6
    # Código evaluación energética
    area_coordinates = (62.3, 30.7, 88.1, 35.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    codigo_evaluacion = extracted_text
    codigo_evaluacion

    df = pd.DataFrame(data=[codigo_evaluacion], columns=['codigo_evaluacion'])
    df['content'] = None

    # Close the PDF document
    pdf_report.close()
    return df

def scrape_informe_cev_v2_pagina7(pdf_file_path):

    pdf_report = fitz.open(pdf_file_path)
    page_number = 6  # Page number (starting from 0)
    page = pdf_report[page_number]


    # ## Pagina 7
    # Código evaluación energética
    area_coordinates = (62.3, 30.7, 88.1, 35.1)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    codigo_evaluacion = extracted_text

    df = pd.DataFrame(data=[codigo_evaluacion], columns=['codigo_evaluacion'])

    # Mandante
    area_coordinates = (27.3, 90.0, 97.0, 98.0)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    extracted_text = extracted_text.split('\n')
    df['mandante_nombre']  = extracted_text[0]
    df['mandante_rut']  = extracted_text[1]

    # Evaluador Energético
    area_coordinates = (130.4, 90.0, 208.7, 103.7)  # Coordinates of the area to extract text from: (x1, y1, x2, y2)
    extracted_text = extract_text_from_area(page, area_coordinates)
    extracted_text = extracted_text.split('\n')
    df['evaluador_nombre']  = extracted_text[-3]
    df['evaluador_rut']  = extracted_text[-2]
    df['evaluador_rol_minvu']  = extracted_text[-1]
    # Close the PDF document
    pdf_report.close()
    return df

