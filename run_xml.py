#from make_xml import write_DCC
#
#want = "analytical_value, attempted_value, measured_value, direction, measurement_number"
#
#table = 'w_vinkeldrej_test'
#
#requirements_head = ['direction', 'measurement_number']
#
#requirements_foot = ["'ccw'", 2]
#
#write_DCC(want, table, requirements_head, requirements_foot)

import pandas as pd
from tqdm import tqdm

from make_xml import write_DCC
from SQL_functions import Read_SQL


unit = pd.read_csv(r'Z:\BDU006\Dep271\Akkreditering 9\Teknik\Udvikling\Database\SQL_unit_value_list.txt')
SI = pd.read_csv(r'Z:\BDU006\Dep271\Akkreditering 9\Teknik\Udvikling\Database\SI_new.txt', sep = '; ', engine = 'python')
prefix = pd.read_csv(r'Z:\BDU006\Dep271\Akkreditering 9\Teknik\Udvikling\Database\prefix.txt', sep = ',')
temp_spec = pd.read_csv(r'Z:\BDU006\Dep271\Akkreditering 9\Teknik\Udvikling\Database\Temperature_specific.txt', sep = ',')
real_DCC_names = pd.read_csv(r'Z:\BDU006\Dep271\Akkreditering 9\Teknik\Udvikling\Database\database_til_DCC_navne.txt')

unikke_certs = set()

certifikatnummre = Read_SQL.read_specific("select certifikatnummer from w_kal_data where enhed_sand is not NULL and enhed_aflæst is not NULL", 'certifikatnummer')# and certifikatnummer = '9.1P-14-4054C'", 'certifikatnummer') # "where enhed_sand is not NULL" has been added

for certifikatnummer in certifikatnummre.values:
    if certifikatnummer != '':
        unikke_certs.add(certifikatnummer[0])

for certifikatnummer in tqdm(unikke_certs, total = len(unikke_certs)):

    want = "*"

    table = 'w_kal_data'

    certifikatnummer = certifikatnummer#123-20979.001.079.02 Rev. A, 9.10P-15459, 9.10T-14650, 9.10P-15441, 9.10P-15440

    requirements_head = ['certifikatnummer']

    requirements_foot = [f"'{certifikatnummer}'"] 

    name = f"C:\\Users\\AY\\Desktop\\test_DCC\\DCC_{requirements_head[0]}_{requirements_foot[0]}.xml"

    write_DCC(want, table, requirements_head, requirements_foot, name, certifikatnummer, unit, SI, prefix, temp_spec, real_DCC_names)