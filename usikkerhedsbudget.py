import numpy as np
from collections import defaultdict

class usikkerhedsbudget():

    @staticmethod
    def standart_afvigelse(data):
        std_dev_dict = {}
        groups = data.groupby('analytical_value')
        for analytical_value, group in groups:
            analytical_values = group['analytical_value'].astype(float)
            dut_values = group['measured_value'].astype(float)
            ref_values = group['attempted_value'].astype(float)
            normalized_values = dut_values / ref_values*analytical_values
            std_dev = np.std(normalized_values)
            std_dev_dict[analytical_value] = std_dev
        return std_dev_dict

    @staticmethod
    def get_N_L_M_J(data, direction):

        directional_data = data.loc[(data["direction"] == direction) & (data["rising_or_falling"].str.strip() != 'None') & (data["rising_or_falling"].isna() == False)]

        N_values = directional_data['udgangspunkt'].unique()
        N = len(N_values)
        
        L_values = directional_data.groupby('udgangspunkt')['measurement_number'].unique()
        L = {udgangspunkt: len(L_values[udgangspunkt]) for udgangspunkt in N_values}

        J_values = directional_data.groupby(['udgangspunkt', 'measurement_number'])['analytical_value'].unique()
        J = {udgangspunkt: {måling: len(J_values[udgangspunkt, måling]) for måling in L_values[udgangspunkt]} for udgangspunkt in N_values}

        M_values = {udgangspunkt: {måling: {analytisk: len(J_values[udgangspunkt, måling]) for analytisk in J_values[udgangspunkt, måling]} for måling in L_values[udgangspunkt]} for udgangspunkt in N_values}
        M=1

        return [N, L, M, J, N_values, L_values, M_values, J_values]
    
    @staticmethod
    def get_res_uncertainty(res):

        return res/(2 * 3 ** 0.5)
    
    def usikkerheder(måleserier, måleserie_længde, new, udgangspunkter, J, direction, data):
        
        directional_data = data.loc[(data["direction"] == direction) & (data["rising_or_falling"].str.strip() != 'None')]

        delta_a_n = defaultdict(dict)
        std_delta_a_n = defaultdict(dict)

        for udgangspunkt in udgangspunkter:
            delta_a_n[udgangspunkt]=0
            std_delta_a_n[udgangspunkt]=0
            for måleserie in måleserier[udgangspunkt]:
                for måling_værdi in new[udgangspunkt][måleserie]:

                    delta_a_n[udgangspunkt] += usikkerhedsbudget.re_pos_error(directional_data.loc[(directional_data['udgangspunkt'] == udgangspunkt) & (directional_data['measurement_number'] == måleserie) & (directional_data['analytical_value'] == måling_værdi)],
                                                                                len(new[udgangspunkt][måleserie]),
                                                                                len(måleserier[udgangspunkt])
                                                                             )

            for måleserie in måleserier[udgangspunkt]:
                for måling_værdi in new[udgangspunkt][måleserie]:

                    std_delta_a_n[udgangspunkt] += usikkerhedsbudget.re_pos_sd(directional_data.loc[(directional_data['udgangspunkt'] == udgangspunkt) & (directional_data['measurement_number'] == måleserie) & (directional_data['analytical_value'] == måling_værdi)],
                                                                                len(new[udgangspunkt][måleserie]),
                                                                                len(måleserier[udgangspunkt]),
                                                                                delta_a_n[udgangspunkt]
                                                                              )

        delta_a = usikkerhedsbudget.delta_a(delta_a_n)

        try:
            delta_a_dev = usikkerhedsbudget.delta_a_dev(delta_a_n, delta_a)
        except:
            delta_a_dev = 'None'

        ANOVA1 = 0
        for udgangspunkt in udgangspunkter:
            try:
                ANOVA1 += usikkerhedsbudget.ANOVA(måleserie_længde[udgangspunkt], udgangspunkter, delta_a, delta_a_n)
            except:
                ANOVA1 = 'None'

        ANOVA2 = 0
        for udgangspunkt in udgangspunkter:
            for måleserie in måleserier[udgangspunkt]:
                for måling_værdi in new[udgangspunkt][måleserie]:

                    ANOVA2 += usikkerhedsbudget.ANOVA2(directional_data.loc[(directional_data['udgangspunkt'] == udgangspunkt) & (directional_data['measurement_number'] == måleserie) & (directional_data['analytical_value'] == måling_værdi)],
                                                        len(new[udgangspunkt][måleserie]),
                                                        len(måleserier[udgangspunkt]),
                                                        delta_a_n[udgangspunkt],
                                                        len(udgangspunkter)
                                                      )

        v_a = len(udgangspunkter) - 1
        V_b = sum(måleserie_længde[udgangspunkt].values()) - 1

        interseries = False #skal styres af "F" (læs https://www.euramet.org/securedl/sdl-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2ODk2NDY4NTYsImV4cCI6MTY4OTczNjg1NiwidXNlciI6MCwiZ3JvdXBzIjpbMCwtMV0sImZpbGUiOiJNZWRpYVwvZG9jc1wvUHVibGljYXRpb25zXC9jYWxndWlkZXNcL0ktQ0FMLUdVSS0wMjNfQ2FsaWJyYXRpb25fR3VpZGVfTm8uXzIzX3dlYi5wZGYiLCJwYWdlIjo0NDZ9.VEmkxNOYz2lqQEq_Tkpi9GSdEHMdrQ5l8KfHGYJY_D4/I-CAL-GUI-023_Calibration_Guide_No._23_web.pdf
                                                # og onenote_vinkeldrej_"udregning 18-07-2023" hvor der er en chatGPT-forklaring)

        if not interseries:
            try:
                u_j = (len(udgangspunkter) * ANOVA1 * delta_a + V_b * ANOVA2) / sum(sum(måleserie_længde[udgangspunkt].values()) * V_b for udgangspunkt in udgangspunkter)
            except:
                pass
        else:
            try:
                u_j = delta_a_dev / len(udgangspunkter)
            except:
                pass

    @staticmethod
    def re_pos_error(current_data, current_L, current_M):
        Ref_val = float(current_data['attempted_value'].iloc[0])
        cal_val = float(current_data['measured_value'].iloc[0])

        return (cal_val - Ref_val) / (current_M * current_L)
    
    @staticmethod
    def re_pos_sd(current_data, current_L, current_M, delta_a_n):
        Ref_val = float(current_data['attempted_value'].iloc[0])
        cal_val = float(current_data['measured_value'].iloc[0])

        return ((delta_a_n - (cal_val - Ref_val)) ** 2) / (current_M * current_L - 1)
    
    @staticmethod
    def delta_a(an_re_error):
        return sum(an_re_error.values()) / len(an_re_error.values())
    
    @staticmethod
    def delta_a_dev(delta_a_n_error, delta_a):
        for error in delta_a_n_error.values(): 
            std_dev_all += (delta_a - error) ** 2 / (len(delta_a_n_error.values()) - 1)

        return std_dev_all
    
    @staticmethod
    def ANOVA(målinger, udgangspunkter, delta_a, delta_a_n):

        return sum(målinger.values()) / (len(udgangspunkter) - 1) * sum((del_a_n - delta_a) ** 2 for del_a_n in delta_a_n.values())
    
    @staticmethod
    def ANOVA2(current_data, current_L, current_M, delta_a_n, udgangspunkter):
        Ref_val = float(current_data['attempted_value'].iloc[0])
        cal_val = float(current_data['measured_value'].iloc[0])

        return (1 / (udgangspunkter * (current_M * current_L - 1))) * ((delta_a_n - (cal_val - Ref_val)) ** 2)