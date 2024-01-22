import xml.etree.ElementTree as ET
import platform
from collections import defaultdict

from SQL_functions import Read_SQL
from handle_DCC_data import data_to_DCC


class write_DCC():

    def __init__(self, want, table, requirements_head, requirements_foot, name, certifikatnummer, unit, SI, prefix, temp_spec, real_DCC_names):

        #get requested data
        self.SQL_DATA = self.get_SQL(want, table, requirements_head, requirements_foot)

        DCC_measurements, group = data_to_DCC.convert_to_SI(self.SQL_DATA, unit, SI, prefix, temp_spec, requirements_foot)

        all_trues = [group['sand_værdi'][a] for a in group['sand_værdi']]

        self.make_xml(name, DCC_measurements, certifikatnummer, all_trues, real_DCC_names, number_of_measurements = 2)

    def get_SQL(self, want, table, requirements_head, requirements_foot):

        conditions = " and ".join(f"{a} = {b}" for a, b in zip(requirements_head, requirements_foot))
        condition_clause = f"{conditions}" if conditions else ""
        return Read_SQL.get_SQL(want, table, condition_clause)
    
    def make_xml(self, name, unit_specific, certifikatnummer, list_refType, real_DCC_names, number_of_measurements):

        debug_name = r'c:\Users\AY\Desktop\debug_skabelon\første_test.xml'

        #mangler muligvis xml-version
        DCC = ET.Element('dcc:digitalCalibrationCertificate', attrib = { 
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xs': 'http://www.w3.org/2001/XMLSchema',
            'xmlns:dcc': 'https://ptb.de/dcc',
            'xmlns:si': 'https://ptb.de/si',
            'xsi:schemaLocation': 'https://ptb.de/dcc https://ptb.de/dcc/v3.2.1/dcc.xsd',
            'schemaVersion': '3.2.1'
        })
        administrativeData = ET.SubElement(DCC, 'dcc:administrativeData')
        dccSoftware = ET.SubElement(administrativeData, 'dcc:dccSoftware')
        software = ET.SubElement(dccSoftware, 'dcc:software')
        data_name = ET.SubElement(software, 'dcc:name')
        software_name = ET.SubElement(data_name, 'dcc:content')
        software_name.text = 'Python'
        software_release = ET.SubElement(software, 'dcc:release')
        software_release.text = f'{platform.python_version()}'

        coredata = ET.SubElement(administrativeData, 'dcc:coreData')

        ## mangler i database (der er hardkodet til 'DK') ((det er landet der er kalibreret i))
        countryCode = ET.SubElement(coredata, 'dcc:countryCodeISO3166_1')
        countryCode.text = 'DK'
        ## mangler i database (der er hardkodet til 'DK') ((det er landet der er kalibreret i))

        langcode_en = ET.SubElement(coredata, 'dcc:usedLangCodeISO639_1')
        langcode_en.text = 'en'
        langcode_da = ET.SubElement(coredata, 'dcc:usedLangCodeISO639_1')
        langcode_da.text = 'da'
        mandatory_lang = ET.SubElement(coredata, 'dcc:mandatoryLangCodeISO639')
        mandatory_lang.text = 'en'

        unique_identifier = ET.SubElement(coredata, 'dcc:uniqueIdentifier')
        unique_identifier.text = certifikatnummer

        identifications = ET.SubElement(coredata, 'dcc:identifications')

        identification_1 = ET.SubElement(identifications, 'dcc:identification')

        ## mangler I database der kan stå [manufacturer, calibrationLaboratory, customer, owner, other]
        identification_issuer = ET.SubElement(identification_1, 'dcc:issuer')
        identification_issuer.text = 'customer'
        ## mangler I database hardkodet til at det er Novo Nordisk der skal have certifikatet

        ## mangler I database tror det er PO-Nummer
        issuer_value = ET.SubElement(identification_1, 'dcc:value')
        issuer_value.text = '??tror det er PO-nummer??'
        ## mangler I database tror det er PO-Nummer

        ## Vi har kun dato vi har ikke dato start og dato slut
        coredata_start_time = ET.SubElement(coredata, 'dcc:beginPerformanceDate')
        coredata_start_time.text = self.SQL_DATA.dato[0]
        coredata_end_time = ET.SubElement(coredata, 'dcc:endPerformanceDate')
        coredata_end_time.text = self.SQL_DATA.dato[0]
        ## Vi har kun dato vi har ikke dato start og dato slut

        ### for other date self.SQL_DATA.tidsstempel[0].strftime('%y-%m-%d')

        #skal tilføjes hvilket sted er kalibreringen udført CHOICES [laboratory, customer, laboratoryBranch, customerBranch, other]
        coredata_place_type = ET.SubElement(coredata, 'dcc:performanceLocation')
        coredata_place_type.text = 'laboratory'
        #skal tilføjes hvilket sted er kalibreringen udført CHOICES [laboratory, customer, laboratoryBranch, customerBranch, other]


        ##### KÆMPE MANGLER #####


        measurements = ET.SubElement(DCC, 'dcc:measurementResults')
        measurement_1 = ET.SubElement(measurements, 'dcc:measurementResult')


        ##### KÆMPE MANGLER #####


        results = ET.SubElement(measurement_1, 'dcc:results')
        result_1 = ET.SubElement(results, 'dcc:result')
        result_1_name = ET.SubElement(result_1, 'dcc:name')
        result_1_name_content = ET.SubElement(result_1_name, 'dcc:content', attrib = {'lang': 'en'})
        result_1_name_content.text = 'Calibration results'
        result_1_desciption = ET.SubElement(result_1, 'dcc:description')

        #skal tilføjes i dataopsamlingen hvor mange målepunkter dataen kommer fra (muligvis også databehandling)
        result_1_desciption_content = ET.SubElement(result_1_desciption, 'dcc:content', attrib = {'lang': 'en'})
        result_1_desciption_content.text = f'The values given are mean values from {number_of_measurements} measuring cycles each'
        #skal tilføjes i dataopsamlingen hvor mange målepunkter dataen kommer fra (muligvis også databehandling)

        result_1_data = ET.SubElement(result_1, 'dcc:data')

        #databasen skal have "list_reftype" med
        result_1_data_list = ET.SubElement(result_1_data, 'dcc:list', attrib = {'refType': f'{" ".join(list_refType)}'})
        #databasen skal have "list_reftype" med

        #for start

        result_1_data_list_quantity = defaultdict()

        for count, måletype in enumerate(unit_specific):

            result_1_data_list_quantity[count] = ET.SubElement(result_1_data_list, 'dcc:quantity', attrib = {'refType': f'{real_DCC_names[real_DCC_names.column == måletype].DCC.values[0]}'})

            result_1_data_list_quantity_name = ET.SubElement(result_1_data_list_quantity[count], 'dcc:name')

            #databasen skal have kalibreringstype
            result_1_data_list_quantity_name_content = ET.SubElement(result_1_data_list_quantity_name, 'dcc:content', attrib = {'lang': 'en'})
            result_1_data_list_quantity_name_content.text = f'{real_DCC_names[real_DCC_names.column == måletype].DCC.values[0]}' #kun skabelonting her
            #databasen skal have kalibreringstype

            result_1_data_list_quantity_hybrid = ET.SubElement(result_1_data_list_quantity[count], 'si:hybrid')

            #start for
            for a in unit_specific[måletype]:

                for b in reversed(unit_specific[måletype][a]):
                    if b != 'group':
                        ###debug ved ?
                        if '?' in b:
                            break
                        ###

                        result_1_data_list_quantity_hybrid_realListXMLList = ET.SubElement(result_1_data_list_quantity_hybrid, 'si:realListXMLList')

                        result_1_data_list_quantity_hybrid_valueXMLList = ET.SubElement(result_1_data_list_quantity_hybrid_realListXMLList, 'si:valueXMLList')
                        result_1_data_list_quantity_hybrid_valueXMLList.text = ' '.join(unit_specific[måletype][a][b])

                        result_1_data_list_quantity_hybrid_unitXMLList = ET.SubElement(result_1_data_list_quantity_hybrid_realListXMLList, 'si:unitXMLList')
                        result_1_data_list_quantity_hybrid_unitXMLList.text = b

            #end for

        #for end

        general_functions.end_xml(DCC, name) #debug_name)

#        measurementMetaData = ET.SubElement(DCC, 'dcc:measurementMetaData')
#        metaData = ET.SubElement(measurementMetaData, 'dcc:metaData', attrib = {'refType': 'basic_calibrationValue'})
#        declaration = ET.SubElement(metaData, 'dcc:declaration')
#        ET.SubElement(declaration, 'dcc:content', attrib = {'lang': 'de'}).text = 'Kalibrierpunkt'
#        ET.SubElement(declaration, 'dcc:content', attrib = {'lang': 'en'}).text = 'Calibration value'
#        data = ET.SubElement(metaData, 'dcc:data')
#
#        quantity = ET.SubElement(data, 'dcc:quantity')
#        realListXMLList = ET.SubElement(quantity, 'si:realListXMLList')
#
#        general_functions.vals_n_units(unit_specific, realListXMLList, 'sand_værdi')
#
###################################
#
#        for measuretype in unit_specific.keys():
#
#            readListXMLList = ET.SubElement(quantity, f'si:realListXMLList')
#            general_functions.vals_n_units(unit_specific, readListXMLList, measuretype)
#
###################################
#
#        general_functions.prettify(DCC)
#
#        tree = ET.ElementTree(DCC)
#        tree.write(name, encoding = 'UTF-8', xml_declaration=True)

class general_functions():

    def prettify(element, indent = '  '): 

        queue = [(0, element)]  # (level, element)
        while queue:
            level, element = queue.pop(0)
            children = [(level + 1, child) for child in list(element)]
            if children:
                element.text = '\n' + indent * (level+1)  # for child open
            if queue:
                element.tail = '\n' + indent * queue[0][0]  # for sibling open
            else:
                element.tail = '\n' + indent * (level-1)  # for parent close
            queue[0:0] = children  # prepend so children come before siblings

    def vals_n_units(unit_specific, realListXMLList, column_name):
        for a in unit_specific[column_name]:
            values = {}
            values[a] = unit_specific[column_name][a]

            valueXMLList = ET.SubElement(realListXMLList, 'si:valueXMLList')
            valueXMLList.text = ' '.join(values[a])

            unitXMLList = ET.SubElement(realListXMLList, 'si:unitXMLList')
            unitXMLList.text = a

        return realListXMLList
    
    def end_xml(DCC, name):
        general_functions.prettify(DCC)
        tree = ET.ElementTree(DCC)
        tree.write(name, encoding = 'UTF-8', xml_declaration=True)