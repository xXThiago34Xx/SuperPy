import pandas as pd
import os

from utils.employee_utils import *
from utils.pdf_utils import scrap_pdf
from utils.time_utils import strfdelta
from datetime import timedelta, datetime


def get_day_dict(day: Day) -> dict:
    return {
        "Entrada": day.interval.start if day.day_type == "REGULAR" else day.day_type,
        "Salida": day.interval.end if day.day_type == "REGULAR" else day.day_type,
    }


def get_cajeros_dataframe(cajeros_list: list[Employee]) -> pd.DataFrame:
    days_of_week_names = ["Lunes", "Martes", "Miércoles",
                          "Jueves", "Viernes", "Sábado", "Domingo"]
    days_of_week_atr_name = [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # Collect dictionaries first
    dict_list = []
    for cajero in cajeros_list:
        cajero_dict = {("Nombre", ""): cajero.name}
        for day_name, day_attr in zip(days_of_week_names, days_of_week_atr_name):
            day_dict = get_day_dict(getattr(cajero.schedule, day_attr))
            for key, value in day_dict.items():
                cajero_dict[(day_name, key)] = value
        dict_list.append(cajero_dict)

    # Create the DataFrame from the list of dictionaries
    cajeros_df = pd.DataFrame(dict_list)

    # Set MultiIndex columns
    cajeros_df.columns = pd.MultiIndex.from_tuples(cajeros_df.columns)

    return cajeros_df

# Función para formatear las columnas de "Entrada" y "Salida"


def format_schedule(df):
    days_of_week_names = ["Lunes", "Martes", "Miércoles",
                          "Jueves", "Viernes", "Sábado", "Domingo"]
    # Aplanar temporalmente el MultiIndex
    df_flat = df.copy()
    df_flat.columns = ['_'.join(col).strip() for col in df_flat.columns.values]

    # Formatear las columnas de "Entrada" y "Salida"
    for day in days_of_week_names:
        for period in ["Entrada", "Salida"]:
            col_name = f"{day}_{period}"
            if col_name in df_flat.columns:
                df_flat[col_name] = df_flat[col_name].apply(
                    lambda x: pd.to_datetime(x).strftime(
                        '%I:%M%p') if not isinstance(x, str) else x
                )

    # Restaurar el MultiIndex
    new_columns = [tuple(col.split('_')) if '_' in col else (col, '')
                   for col in df_flat.columns]
    df_flat.columns = pd.MultiIndex.from_tuples(new_columns)

    return df_flat


def get_day_schedule(df, day):
    output_df = df[["Nombre", day]].xs(day, axis=1, level=0)
    output_df["Nombre"] = df["Nombre"]
    return output_df[["Nombre", "Entrada", "Salida"]]


def format_schedule(df):
    formated_df = df.copy()
    formated_df["Entrada"] = formated_df["Entrada"].apply(
        lambda x: pd.to_datetime(x).strftime(
            '%I:%M%p') if not isinstance(x, str) else x
    )
    formated_df["Salida"] = formated_df["Salida"].apply(
        lambda x: pd.to_datetime(x).strftime(
            '%I:%M%p') if not isinstance(x, str) else x
    )
    return formated_df


class DaySchedule():
    def __init__(self, cajeros_df: pd.DataFrame, day: str):
        self.day = day
        self.cajeros_df = cajeros_df
        self.day_schedule_df = self.get_day_schedule()

    def get_day_schedule(self):
        return get_day_schedule(self.cajeros_df, self.day)

    def format_schedule(self):
        return format_schedule(self.day_schedule_df)

    def get_available_employees(self) -> pd.DataFrame:
        out_df = self.day_schedule_df.copy()
        out_df = out_df[out_df["Entrada"] != "DIA DE DESCANSO"]
        out_df = out_df[out_df["Entrada"] != "VACACIONES"]
        out_df = out_df[out_df["Entrada"] != "PAGO HORAS FERIADO"]

        return out_df


def get_cajeros_df(pdf_path: str, self_amount: int = 6) -> pd.DataFrame:
    employee_list = scrap_pdf(pdf_path, self_amount)
    cajeros_list: list[Employee] = [
        employee for employee in employee_list if employee.category == "CAJERO"]
    return get_cajeros_dataframe(cajeros_list)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_path_exists(path):
    return os.path.exists(path)


def get_ean13(cod):
    if len(cod) < 12:
        return None
    if len(cod) > 12:
        cod = cod[:12]
    cod = cod[::-1]
    sum = 0
    for i in range(0, len(cod)):
        if i % 2 == 0:
            sum += int(cod[i])
        else:
            sum += int(cod[i]) * 3
    check_digit = 10 - (sum % 10)
    if check_digit == 10:
        check_digit = 0
    return cod[::-1] + str(check_digit)


def print_menu():
    print('''1. Cargar Archivo (Input ruta)
2. Establecer cantidad de Self
3. Seleccionar Dia (L-D)
4. Mostrar Entradas
5. Mostrar Salidas
6. Mostrar Entradas de la Semana
7. Tools (Completar EAN)
8. Salir
''')


def print_error():
    clear()
    input('Opción no válida. Presione Enter para continuar...')


def print_header(pdf_path, amount_self, day):
    print(
        f"Menú Principal\t\tArchivo: {pdf_path}\t\t|Self: {amount_self}\t\t|Día: {day}\n")


pdf_path = r"./horarios/Horario 01-07.24.pdf"
amount_self = 6
cajeros_df = get_cajeros_df(pdf_path, amount_self)
day = "Lunes"
day_schedule = DaySchedule(cajeros_df, day)
day_list = ["Lunes", "Martes", "Miércoles",
            "Jueves", "Viernes", "Sábado", "Domingo"]


def main():

    global pdf_path
    global amount_self
    global cajeros_df
    global day
    global day_schedule
    global day_list

    while True:
        clear()
        print_header(pdf_path, amount_self, day)
        print_menu()
        option = input('Ingrese una opción: ')

        if option == '1':
            clear()
            print_header(pdf_path, amount_self, day)
            pdf_path = input(f'Ingrese la ruta del archivo PDF [{pdf_path}]: ')
            if check_path_exists(pdf_path):
                cajeros_df = get_cajeros_df(pdf_path, amount_self)
                input('Archivo cargado correctamente. Presione Enter para continuar...')
            else:
                print('El archivo no existe')

        elif option == '2':
            clear()
            print_header(pdf_path, amount_self, day)
            amount_self = int(
                input(f'Ingrese la cantidad de Self [{amount_self}]: '))
            cajeros_df = get_cajeros_df(pdf_path, amount_self)
            input(
                'Cantidad de Self actualizada correctamente. Presione Enter para continuar...')

        elif option == '3':
            clear()
            print_header(pdf_path, amount_self, day)
            for i, day in enumerate(day_list):
                print(f"{i+1}. {day}")
            day = day_list[int(input('Ingrese el día (1-7): ')) % 7 - 1]
            day_schedule = DaySchedule(cajeros_df, day)
            input(
                f'Día {day} seleccionado correctamente. Presione Enter para continuar...')

        elif option == '4':
            clear()
            print_header(pdf_path, amount_self, day)
            print(format_schedule(day_schedule.get_available_employees(
            ).sort_values(by="Entrada")[["Nombre", "Entrada", "Salida"]]).to_string(
                index=False
            ))
            input('Presione Enter para continuar...')

        elif option == '5':
            clear()
            print_header(pdf_path, amount_self, day)
            print(format_schedule(day_schedule.get_available_employees(
            ).sort_values(by="Salida")[["Nombre", "Salida", "Entrada"]]).to_string(
                index=False
            ))
            input('Presione Enter para continuar...')

        elif option == '6':
            clear()
            print_header(pdf_path, amount_self, day)
            for _day in day_list:
                print(f"-------------------------------{_day}-------------------------------")
                _day_schedule = DaySchedule(cajeros_df, _day)
                _sorted_schedule = _day_schedule.get_available_employees().sort_values(by="Entrada")[["Nombre", "Entrada", "Salida"]]
                if (_sorted_schedule.empty):
                    print("No hay empleados disponibles")
                else:
                    print(format_schedule(_sorted_schedule).to_string(index=False))
                print("\n\n")
            input('Presione Enter para continuar...')

        elif option == '7':
            clear()
            print_header(pdf_path, amount_self, day)
            cod = input("Ingrese el código EAN-12: ")
            ean13 = get_ean13(cod)
            print(f"El código EAN-13 es: {ean13}")
            input("Presione cualquier tecla para continuar...")

        elif option == '8':
            break

        else:
            pass
            input('Presione Enter para continuar...')


if __name__ == "__main__":
    main()
