import sqlite3


class CajerosDatabase:
    query_select_atms = 'select * from cajeros where ubicacion in ({}) and prob_disponibilidad > 0'
    query_update_atms = 'update cajeros set prob_disponibilidad = {} where ubicacion = {}'

    def __init__(self, db_dir):
        self.connection = sqlite3.connect(db_dir, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_and_extract(self, atm_list):
        aux_list = list(map(lambda x: '\'{}\''.format(x[1]), atm_list.tolist()))

        query = CajerosDatabase.query_select_atms.format(', '.join(aux_list))

        query_result = self.cursor.execute(query).fetchall()
        query_result = list(map(lambda x: (x[4], x[6], x[18]), query_result))
        final_result = self.format_atm_tuples(query_result)

        for i in range(0, len(query_result)):
            ubicacion = '\'{}\''.format(query_result[i][1])
            disp = query_result[i][2]

            if i == 0:
                disp -= 0.7

            if i == 1:
                disp -= 0.2

            if i == 2:
                disp -= 0.1

            self.cursor.execute(CajerosDatabase.query_update_atms.format(disp, ubicacion))

        self.connection.commit()

        return final_result

    def close_connection(self):
        self.connection.close()

    def format_atm_tuples(self, tuples):
        new_tuples = []
        for t in tuples:
            result = '{} @ {}'.format(t[0], t[1])

            if t[2] < 100:
                result += ' (prob. de baja disponibilidad)'

            new_tuples.append(result)

        return new_tuples
