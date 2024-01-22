import pandas as pd
from collections import defaultdict
from decimal import Decimal, getcontext
import math

class data_to_DCC():

    def convert_to_SI(SQL_DATA, unit, SI, prefix, temp_spec, requirements_foot):

        data_corelation = data_to_DCC.data_relation(unit) #result_dict skal bruges igen til usikkerheder

        units, modified_data = data_to_DCC.group_units(SQL_DATA, data_corelation)

        unit_specific = data_to_DCC.DCC_organize_data(SQL_DATA, modified_data, units, requirements_foot)

        groups = defaultdict(dict)
        correct = defaultdict(dict)
        for value_type in unit_specific:
            booltemp_spec = any(a == value_type for a in temp_spec.additional_special_case)
            groups[value_type] = defaultdict(dict)
            correct[value_type] = defaultdict(dict)
            for unit in unit_specific[value_type].keys():
                correct[value_type][unit], groups[value_type][unit] = data_to_DCC.get_SI(SQL_DATA, SI, unit, unit_specific[value_type][unit], prefix, booltemp_spec, correct, value_type, unit_specific)

        return correct, groups

    def data_relation(unit):

        data_corelation = {}

        # Iterate through the unique types in the DataFrame and create the dictionary
        for type_name in unit['type'].unique():
            values_list = unit[unit['type'] == type_name]['values'].tolist()
            data_corelation[type_name] = values_list
        
        return data_corelation
    
    def group_units(data, res_dic):

        drop_cols = []

        for a in data.columns:
            if all(pd.isna(data[a])) or all(data[a] == ''):
                drop_cols.append(a)

        data.drop(drop_cols, axis = 1, inplace=True)

        filtered_res_dic = {}

        for key, value_list in res_dic.items():
            # Filter out values that are not present in data.columns
            filtered_values = [value for value in value_list if value in data.columns]
            
            # Add the filtered values to the new dictionary
            if filtered_values != []:
                filtered_res_dic[key] = filtered_values

        return [filtered_res_dic, data]
    
    def DCC_organize_data(SQL_DATA, modified_data, units, requirements_foot):
        # Initialize the dictionary to store unit-specific data
        unit_specific = {}

        # Iterate through the rows of modified_data
        for index, row in modified_data.iterrows():
            for unit_key in units.keys():

                ## skal gøres noget ved data uden enhed
                unit = row[unit_key]
                ## skal gøres noget ved data uden enhed

                # Iterate through columns (unit_key's) and extract values based on the unit
                for column in units[unit_key]:
                    if column not in unit_specific:
                        unit_specific[column] = {}

                    if unit not in unit_specific[column] and not pd.isna(unit):
                        unit_specific[column][unit] = []

                    values = modified_data.at[index, column]
                    if not (pd.isna(unit) and pd.isna(values)): 
                        unit_specific[column][unit].append(values)

        return unit_specific

#    def relative_fix(SQL_DATA):
#
#        to_return =defaultdict(list)
#        to_fix=[]
#
#        aflæst = [a.replace(" ","").replace("±","").replace(".","").replace(",",".") for a in SQL_DATA.objekt_aflæst]
#        reference = [a.replace(" ","").replace("±","").replace(".","").replace(",",".") for a in SQL_DATA.sand_værdi]
#
#        for count, (a,b) in enumerate(zip(aflæst, reference)):
#            try:
#                to_return[count] = float(a)-float(b)
#            except :
#                to_fix.append(count)
#
#        for a in to_fix:
#            absolute_values = [abs(to_return[idx]) for idx in to_return.keys()]
#            min_idx = min(range(len(absolute_values)), key=absolute_values.__getitem__)
#            to_return[a] = to_return[min_idx]

    def get_cur_unit(special_case):
        if special_case == 'relative':
            cur_unit = '% relative'
        if special_case == 'full_scale':
            cur_unit = '% FS'
        return cur_unit

    def get_cur_sand_and_fejl(SQL_DATA, unit_specific, val_type):
        slæbeviser = False
        if 'u_sl' in val_type:
            korrekt_aflæst = SQL_DATA.objekt_aflæst
            if 'sand_u_sl' in unit_specific:
                korrekt_sand = SQL_DATA.sand_u_sl
            else:
                korrekt_sand = SQL_DATA.sand_værdi
            if 'fejl_u_sl' in unit_specific:
                korrekt_fejl = SQL_DATA.fejl_u_sl
            else:
                korrekt_fejl = SQL_DATA.fejl
        elif 'm_sl' in val_type:
            slæbeviser = True
            if 'sand_m_sl' in unit_specific:
                korrekt_sand = SQL_DATA.sand_m_sl
            else:
                korrekt_sand = SQL_DATA.sand_værdi
            if 'Fejl_m_sl' in unit_specific:
                korrekt_fejl = SQL_DATA.Fejl_m_sl
            else:
                korrekt_fejl = SQL_DATA.fejl
            if 'objekt_aflæst_m_sl' in unit_specific:
                korrekt_aflæst = SQL_DATA.objekt_aflæst_m_sl
            else:
                korrekt_aflæst = SQL_DATA.objekt_aflæst
        else:
            if 'sand_værdi' not in unit_specific:
                korrekt_sand = SQL_DATA.sand_u_sl
            else:
                korrekt_sand = SQL_DATA.sand_værdi
            if 'fejl' not in unit_specific:
                korrekt_fejl = SQL_DATA.fejl_u_sl
            else:
                korrekt_fejl = SQL_DATA.fejl

            korrekt_aflæst = SQL_DATA.objekt_aflæst

        return korrekt_sand, korrekt_aflæst, korrekt_fejl, slæbeviser

    def get_SI(SQL_DATA, SI, target_unit, unit_specific_values, prefix, booltemp_spec, correct, val_type, unit_specific):

        prefactor, prefactor_string, plat_unit, plat_convert_value, cur_unit, temp_unit, group, special_case = data_to_DCC.find_SI_and_prefix(SQL_DATA, SI, prefix, target_unit)

        if special_case and special_case != 'abs':
            cur_unit = data_to_DCC.get_cur_unit(special_case)

        korrekt_sand, korrekt_aflæst, korrekt_fejl, slæbeviser = data_to_DCC.get_cur_sand_and_fejl(SQL_DATA, unit_specific, val_type)

        if special_case == 'relative':
            clean_ref_value = data_to_DCC.remove_useless_string(korrekt_sand, val_type)

        if (special_case == 'relative' and val_type == 'fejl'):
            clean_DUT_values = data_to_DCC.remove_useless_string(korrekt_aflæst, val_type)
            clean_percent_value = data_to_DCC.remove_useless_string(unit_specific_values, val_type)

        elif (special_case == 'relative' and 'eks' in val_type):
            clean_percent_value = data_to_DCC.remove_useless_string(unit_specific_values, val_type)

        else:
            clean_value_strings = data_to_DCC.remove_useless_string(unit_specific_values, val_type)

        temp_meas = False
        if temp_unit == '°C' or temp_unit == '°F' or temp_unit == 'K':
            temp_meas = temp_unit

        if (special_case == 'relative' and (val_type == 'fejl' or 'eks' in val_type)):
            post_comma = data_to_DCC.significants_for_percent(clean_ref_value)
            least = data_to_DCC.significant_values(clean_ref_value)
        else:
            least = data_to_DCC.significant_values(clean_value_strings)

        if (special_case == 'relative' and val_type == 'fejl'):
            read_number_values, read_number_strings = data_to_DCC.relative_error_formating(clean_DUT_values, clean_ref_value, post_comma)
        elif (special_case == 'relative' and 'eks' in val_type):
            read_number_values, read_number_strings = data_to_DCC.expanded_uncertanty_formating(clean_percent_value, clean_ref_value, post_comma)
        else:
            read_number_values, read_number_strings = data_to_DCC.strings_to_numbers(least, clean_value_strings, SQL_DATA)

        least_meaning = data_to_DCC.min_sig(read_number_values)

        perfect_SI = data_to_DCC.SI_conversion(least, read_number_values, prefactor, plat_convert_value, least_meaning, temp_meas, booltemp_spec, special_case, SQL_DATA, correct, val_type)

        if (special_case == 'relative' and (val_type == 'fejl' or 'eks' in val_type)):
            read_number_strings = data_to_DCC.original_percent_error(clean_percent_value)

        if cur_unit == '% relative' or cur_unit == '% FS':
            prefactor_string = ''

        return {f"{prefactor_string}{cur_unit}": read_number_strings, plat_unit: perfect_SI}, group
    
    def original_percent_error(unit_specific_values):
        listt = defaultdict(set)
        to_fix = []
        for count, a in enumerate(unit_specific_values):
            try:
                listt[count] = str(float(a))
            except:
                to_fix.append(count)
        for a in to_fix:
            listt[a] = str(0)
        return [listt[a] for a in sorted(listt.keys())]

    def expanded_uncertanty_formating(clean_percent_value, clean_ref_value, least):
        read_number_values = []
        for a, b, c in zip(clean_percent_value, clean_ref_value, least):
            still_going = True
            while still_going:
                try:
                    read_number_values.append(Decimal(float(b)*float(a)/100).quantize(Decimal('1e-{0}'.format(c))))
                    still_going = False
                except:
                    c-=1
        return read_number_values, [str(a) for a in read_number_values]

    def relative_error_formating(clean_DUT_values, clean_ref_value, least):
        read_number_values = []
        for a, b, c in zip(clean_DUT_values, clean_ref_value, least):
            still_going = True
            while still_going:
                try:
                    read_number_values.append(Decimal(float(b)-float(a)).quantize(Decimal('1e-{0}'.format(c))))
                    still_going = False
                except:
                    c-=1
        return read_number_values, [str(a) for a in read_number_values]

    def significants_for_percent(clean_ref_value):
        listt = defaultdict(set)
        for count, a in enumerate(clean_ref_value):
            if '.' in a:
                for count1, b in enumerate(a):
                    if b == '.':
                        listt[count] = len(a) - count1 - 1
                        break
            else:
                listt[count] = 0
        return [listt[a] for a in sorted(listt.keys())]

    def all_zeroes(cal_numbers, min_digits):
        for a in cal_numbers:
            found = False
            for count, b in enumerate(reversed(a)):
                if b == '.':
                    min_digits.append(count)
                    found = True
            if not found:
                min_digits.append(0)
        
        return min_digits
    
    def find_significants_for_each(cal_numbers):
        numbers = '123456789'

        significants = defaultdict(list)

        for count1, number_string in enumerate(cal_numbers):
            number_string_mod = number_string.replace('.','')
            if all(char == '0' for char in number_string_mod):
                pass
            else:
                for count2, char in enumerate(number_string_mod):
                    if char in numbers:
                        significants[count1] = len(number_string_mod) - count2
                        break
        return significants
    
    def take_care_of_zeroes(significants, cal_numbers, min_digits):
        for count, number in enumerate(cal_numbers):
            if count in significants.keys():
                min_digits.append(significants[count])
            else:
                min_digits.append(min(significants.values()))

        return min_digits

    def significant_values(cal_numbers):
        
        min_digits = []

        if all(all(b in ['0', '.'] for b in a) for a in cal_numbers):
            return data_to_DCC.all_zeroes(cal_numbers, min_digits)
        else:
            significants = data_to_DCC.find_significants_for_each(cal_numbers)
            return data_to_DCC.take_care_of_zeroes(significants, cal_numbers, min_digits)

    def remove_useless_string(unit_specific_values, val_type):

        numbers = defaultdict(list)
        to_fix = []
        to_return = [a.replace(" ","").replace("±","").replace(".","").replace(",",".") for a in unit_specific_values]
        for count, a in enumerate(to_return):
            try:
                numbers[count] = float(a)
            except:
                to_fix.append(count)
        for a in to_fix:
            numbers[a] = '0'

        return [str(numbers[a]) for a in sorted(numbers.keys())]
    
    def take_care_of_abs(start_unit):
        return start_unit.upper().replace('ABS.', '').lower().replace(' ','')
    
    def take_care_of_percent(SQL_DATA):
        if 'abs' in SQL_DATA.enhed_sand[0].lower():
            return data_to_DCC.take_care_of_abs(SQL_DATA.enhed_sand[0])
        return SQL_DATA.enhed_sand[0]
    
    def wierd_unit(SQL_DATA, start_unit):
        if 'ABS' in start_unit.upper():
            return 'abs', data_to_DCC.take_care_of_abs(start_unit)

        if '%' in start_unit and 'REL' in start_unit.upper():
            return 'relative', data_to_DCC.take_care_of_percent(SQL_DATA)

        if "FS" in start_unit.upper():
            print("Andreas skal tilføje kolonner i databasen")
            return 'full_scale', data_to_DCC.take_care_of_percent(SQL_DATA)
        
        return False, start_unit

    def seperate_prefix(SQL_DATA, start_unit, SI, prefix):

        lengths = sorted({len(a) for a in prefix.Symbol.values} | {0})

        special_case, start_unit = data_to_DCC.wierd_unit(SQL_DATA, start_unit) #tager ikke højde for hvad den skal gøre her

        # Find a known unit
        ### find solution for "% rel.", "FS", "abs.", "psi".
        matching_rows = SI[(SI['Symbol'] == start_unit)]

        for length in lengths:
            matching_rows = SI[(SI['Symbol'] == start_unit[length:])]
            if not matching_rows.empty:
                return matching_rows, length, special_case, start_unit
            
        return False
    
    def add_prefix(prefix_symbol, prefix, SI, unit):
        prefactor = prefix.Multiplier[prefix.Symbol == prefix_symbol].iloc[0]
        prefactor_string = prefix.Identifier[prefix.Symbol == prefix_symbol].iloc[0]
        if SI.Class[SI.Symbol == unit].iloc[0]>3:
            prefactor_string = prefix.Identifier[prefix.Symbol == prefix_symbol].iloc[0].replace('\\','|') # det kan være i eksemplet at de hellere vil have Symbol (se Gemmimeg-eksempel hvor mbar bliver til |mbar)
        
        return prefactor, prefactor_string
            

    def find_SI_and_prefix(SQL_DATA, SI, prefix, start_unit):

        matching_rows, length, special_case, start_unit = data_to_DCC.seperate_prefix(SQL_DATA, start_unit, SI, prefix)

        if not matching_rows.empty:

            unit = start_unit[length:]
            prefix_symbol = start_unit[0:length]

            # Add possible prefix
            if prefix_symbol != '':
                prefactor, prefactor_string = data_to_DCC.add_prefix(prefix_symbol, prefix, SI, unit)

            #Get "current class unit"
            current_unit = SI.Identifier[SI.Symbol == unit].iloc[0]

            # Get "Class == 1"-unit
            plat_unit = SI.SI[SI.Symbol == unit].iloc[0]
            plat_convert_value = float(SI.scale[SI.Symbol == unit].iloc[0])

        else: #kan ikke finde opgivet enhed
            testfejl=2

        if prefix_symbol == '':
            return (1, '', plat_unit, plat_convert_value, current_unit, unit, matching_rows.group.values[0], special_case)
        else:
            return (prefactor, prefactor_string, plat_unit, plat_convert_value, current_unit, unit, matching_rows.group.values[0], special_case)
        
    def strings_to_numbers(significants, unit_specific_values, SQL_DATA):

        real_numbers = []
        real_numbers_strings = []

        for significant, unit_specific_value in zip(significants, unit_specific_values):
            getcontext().prec = significant
            real_numbers.append(Decimal(unit_specific_value))
            real_numbers_strings.append(str(Decimal(unit_specific_value)))
        
        return [real_numbers, real_numbers_strings]
    
    def min_sig(unit_specific_values):

        least_list = []
        for a in unit_specific_values:
            for count, b in enumerate(reversed(str(a))):
                if b == '.':
                    least_list.append(count)
                    #ikke testet
                    break
                    #ikke testet
                if count == len(str(a))-1:
                    least_list.append(0)
        return least_list
    
    def SI_conversion(significants, read_number_values, prefactor, plat_convert_value, least_meaning, temp_meas, booltemp_spec, special_case, SQL_DATA, correct, val_type):

        ###debug for '?'
        if plat_convert_value == '?':
            test=2
        ###debug for '?'

        SI_measurements = []

        getcontext().prec = 12 #længste talrække i SI (mmHg (1.33322337415e2))
        plat_convert_value_dec = Decimal(str(plat_convert_value))
        getcontext().prec = 1 #alle prefixer er "runde"
        prefactor_dec = Decimal(str(prefactor))

        for number, decimals, least_significant in zip(read_number_values, significants, least_meaning):

            if not temp_meas:
                result = data_to_DCC.find_correct_number(decimals, number, prefactor_dec, plat_convert_value_dec, least_significant, prefactor, plat_convert_value)

            else:
                if not booltemp_spec:
                    result = data_to_DCC.temp_find_correct_number(decimals, number, prefactor_dec, plat_convert_value_dec, least_significant, prefactor, plat_convert_value)

                else:
                    result = data_to_DCC.temp_spec_find_correct_number(decimals, number, prefactor, temp_meas)

            if 'E' in str(result):
                result = data_to_DCC.remove_E(str(result))

            SI_measurements.append(str(result))

        return SI_measurements

    def find_correct_number(decimals, number, prefactor_dec, plat_convert_value_dec, least_significant, prefactor, plat_convert_value):
        getcontext().prec = decimals #håber decimalerne passere med
        result = Decimal(number * prefactor_dec * plat_convert_value_dec)

        if number == 0:
            if least_significant - int(math.log10(prefactor * plat_convert_value)) >= 0:
                result = Decimal(format(result, f".{least_significant - int(math.log10(prefactor * plat_convert_value))}f"))
            else:
                result = Decimal(format(result, f".{0}f"))

        return result
    
    def temp_find_correct_number(decimals, number, prefactor_dec, plat_convert_value_dec, least_significant, prefactor, plat_convert_value):
        
        getcontext().prec = decimals

        if number != 0:
            if math.ceil(math.log10(abs(number)))<3:
                getcontext().prec = decimals + 2-math.floor(math.log10(abs(number)))
        else:
            getcontext().prec = len(str(number))-2 + math.floor(math.log10(abs(prefactor + plat_convert_value)))

        result = Decimal(number * prefactor_dec + plat_convert_value_dec)

        if number == 0:
            if least_significant - int(math.log10(prefactor + plat_convert_value)) >= 0:
                result = Decimal(format(result, f".{least_significant - int(math.log10(prefactor))}f"))
            else:
                result = Decimal(format(result, f".{0}f"))

        return result
    
    def temp_spec_find_correct_number(decimals, number, prefactor, unit):

        getcontext().prec = 2

        if unit == '°F':
            result = number/Decimal('1.8')*Decimal(str(prefactor))

        else:
            result = number*Decimal(str(prefactor))

        return result
    
    def remove_E(result):
        for count, a in enumerate(result):
            if a == 'E':
                expo = int(result[count+1:])
                number = result[0:count].replace('.','')
                break
        special_case = False
        if '-' in number:
            special_case = True
            
        if special_case:
            return data_to_DCC.special_remove_E(number, expo)
        else:
            return data_to_DCC.normal_remove_E(number, expo)
    
    def normal_remove_E(number, expo):

        if expo > 0:
            for added_zeroes in range(expo-len(number)+1):
                number += '0'

        if expo < 0:
            add_to = '0.'
            for zeroes_added in range(-expo-1):
                add_to += '0'
            number = add_to + number

        return number

    def special_remove_E(number, expo):
        
        if expo > 0:
            for added_zeroes in range(expo-len(number)+2):
                number += '0'

        if expo < 0:
            number = number.replace('-','')
            add_to = '-0.'
            for zeroes_added in range(-expo-1):
                add_to += '0'
            number = add_to + number

        return number