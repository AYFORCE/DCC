from SQL_functions import Read_SQL
from collections import defaultdict
from datetime import datetime
import pandas as pd

kal_programmer = ['SHOREKAL', 'EKSKAL', 'HASTKAL', 'PROKAL', 'MOMDINKAL', 'MOMKAL', 'MMKAL', 'DWTKAL', 'TRÅDKAL', 'KRAFTKAL', 'TRYKKAL', 'HARDKAL', 'TEMPKAL']
kal_programmer_numre = [64,65,66,67,68,69,70,71,72,73,74]

arbejdsnormaler = Read_SQL.get_data_from_table('w_polynomie')

arbnorm = defaultdict()

for a in arbejdsnormaler:
    arbnorm[a[2]] = set()
    for b in kal_programmer_numre:
        if a[b] == 1:
            arbnorm[a[2]].add(kal_programmer[b-64])

unikke=set()
brug_af = Read_SQL.read_specific("select arbejdsnormal, certifikatnummer from w_kal_data", 'arbejdsnormal, certifikatnummer')
for a in brug_af['certifikatnummer']:
    unikke.add(a)
sdf=2
#arb_norm=[arbejdsnormaler[2], kal_programmer[a] for a in kal_programmer_numre]
testes = defaultdict(list)

for a in unikke:
    testes[a] = list(set(brug_af[brug_af['certifikatnummer'] == a]['arbejdsnormal']))

testess=[]
for a in testes.values():
    testess.append(a)

resultat = defaultdict()
nu = datetime.now()
for a in arbejdsnormaler:
    boole = True
    try:
        dage = nu - datetime.strptime(a[1], '%Y-%m-%d')
    except:
        boole = False
    counter = sum(1 for b in testess if a[2] in b)
    if boole: resultat[a[2]] = [counter, dage.days]
    else: resultat[a[2]] = [counter, '?']

df = pd.DataFrame([[a[0],a[1][0],a[1][1]] for a in resultat.items()], columns=['arbejdsnormal', 'antal gange brugt', "dage arbejdsnormalen har været brugbar"])

df.sort_values(by='arbejdsnormal', inplace=True)

df.to_excel('output.xlsx', index=False)