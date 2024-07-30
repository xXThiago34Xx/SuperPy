import pandas as pd
from PyPDF2 import PdfReader
import os
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

def read_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        index = page_text.find("Horario por centro de costo: Semanal (Excel)")
        full_text += page_text[:index]
    return full_text

def format_schedule(schedule: str):
    entrada = schedule.split("-")[0]
    salida = schedule.split("-")[1]

    am_format = "AM"
    pm_format = "PM"

    hora = int(entrada.split(":")[0])
    if (int(hora) >= 12):
        hora = "12"
        entrada = f"{hora}:{entrada.split(':')[1]}"
    
    if (entrada[-1] == "a"):
        entrada = entrada[:-1] + am_format
    else:
        entrada = entrada[:-1] + pm_format

    hora = int(salida.split(":")[0])
    if (int(hora) >= 12):
        hora = "12"
        salida = f"{hora}:{salida.split(':')[1]}"
    if (salida[-1] == "a"):
        salida = salida[:-1] + am_format
    else:
        salida = salida[:-1] + pm_format

    return f"{entrada} - {salida}"

def format_cell(cellString: str):
    if cellString == "0[":
        return "DIA DE DESCANSO"
    if cellString == "0]":
        return "VACACIONES"
    if cellString == "0/":
        return "PAGO HORAS FERIADO"
    return format_schedule(cellString)

def get_schedule(pdf_path, first_cajero, first_rs, data_path="schedule.csv"):
    pdf_text = read_pdf(pdf_path)

    # Find the first occurrence of the word "CAJEROS"
    start_index = pdf_text.find(first_cajero)
    end_index = pdf_text.find(first_rs)

    pdf = pdf_text[start_index:end_index]

    pdf = pdf.replace("RS", " ")
    pdf = pdf.replace("SELF", " ")
    pdf = pdf.replace("CAJEROS", " ")
    pdf = pdf.replace(" x", " ")
    pdf = pdf.replace("DIA DE\nDESCANSO 0:00", " 0[ ")
    pdf = pdf.replace("DIA DE \nDESCANSO 0:00", " 0[ ")
    pdf = pdf.replace("VACACIONES 0:00", " 0] ")
    pdf = pdf.replace("PAGO HORAS\nFERIADO", " 0/ ")
    pdf = pdf.replace("PAGO HORAS \nFERIADO", " 0/ ")

    pdf_list = pdf.split()

    i=0
    n = len(pdf_list)

    while (i<n):
        if pdf_list[i] == "0/" and pdf_list[i+1][0].isdigit():
            id = pdf_list[i+1].find(":") + 3
            pdf_list[i+1] = pdf_list[i+1][id:]
            if pdf_list[i+1] == "":
                pdf_list.pop(i+1)
                n-=1
        if not pdf_list[i][0].isdigit():
            if not (i==0 or pdf_list[i-1][0].isdigit()):
                pdf_list[i-1] += f" {pdf_list[i]}"
                pdf_list.pop(i)
                n-=1
                if pdf_list[i-1][-2].isdigit():
                    pdf_list.insert(i, pdf_list[i-1][-13:])
                    pdf_list[i-1] = pdf_list[i-1][:-13]
                    n+=1
                continue
        i+=1

    # Create a DataFrame
    df = pd.DataFrame([pdf_list[i:i+8] for i in range(0, n, 8)])

    df = df.rename(columns={0: "Nombres", 1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado", 7: "Domingo"})

    df["Lunes"] = df["Lunes"].apply(format_cell)
    df["Martes"] = df["Martes"].apply(format_cell)
    df["Miércoles"] = df["Miércoles"].apply(format_cell)
    df["Jueves"] = df["Jueves"].apply(format_cell)
    df["Viernes"] = df["Viernes"].apply(format_cell)
    df["Sábado"] = df["Sábado"].apply(format_cell)
    df["Domingo"] = df["Domingo"].apply(format_cell)

    # export to csv with separtor ;
    df.to_csv(data_path, sep=";", index=False)

def get_day_schedule(data_path, day):
    df = pd.read_csv(data_path, sep=";")
    day_schedule_df = df[["Nombres", day]]
    # where sea diferente de DIA DE DESCANSO o VACACIONES
    day_schedule_df = day_schedule_df[day_schedule_df[day] != "DIA DE DESCANSO"]
    day_schedule_df = day_schedule_df[day_schedule_df[day] != "VACACIONES"]
    day_schedule_df = day_schedule_df[day_schedule_df[day] != "PAGO HORAS FERIADO"]

    if (day_schedule_df.empty):
        day_schedule_df["Nombre"] = []
        day_schedule_df["Entrada"] = []
        day_schedule_df["Salida"] = []
        return day_schedule_df

    # use threat_cell function to threat the cell
    day_schedule_df["Entrada"], day_schedule_df["Salida"] = zip(*day_schedule_df[day].map(threat_cell))

    # drop sabado
    day_schedule_df = day_schedule_df.drop(columns=[day])

    day_schedule_df["Entrada"] = pd.to_datetime(day_schedule_df["Entrada"])
    day_schedule_df["Salida"] = pd.to_datetime(day_schedule_df["Salida"])

    day_schedule_df.sort_values(by=["Entrada"], inplace=True)
    return day_schedule_df

def threat_cell(cell):
    if cell in ["DIA DE DESCANSO", "VACACIONES", "PAGO HORAS FERIADO"]:
        return cell, cell
    else:
        sp = cell.split(" - ")
        entrada = sp[0]
        salida = sp[1]
        return entrada, salida

#Entrada
def print_entrada(day_schedule_df):
    print(day_schedule_df.sort_values(by=["Entrada"])["Nombre", "Entrada"])

#Salida
def print_salida(day_schedule_df):
    print(day_schedule_df.sort_values(by=["Salida"])["Nombre", "Salida"])

#To Excel

def get_caja_matrix(nCjas, day_schedule_df):
    nrCajas = nCjas - 1
    caja_matrix = [[] for _ in range(0, nrCajas+1)]
    cajeros_no_asignados = []
    cajas = [None for i in range(0, nrCajas+1)]
    asignados = []

    for i, (id, row) in enumerate(day_schedule_df.iterrows()):
        if (i == 0):
            cajas[1] = row
            asignados.append((row["Entrada"], row["Salida"], 1, id))
            caja_matrix[1].append(f"{row['Nombres']} - {row['Entrada'].strftime('%I:%M%p')} - {row['Salida'].strftime('%I:%M%p')}")
            continue
        for j, asignado in enumerate(asignados):
            if (asignado is None):
                continue
            if (row["Entrada"] >= asignado[1]):
                cajas[asignado[2]] = row
                asignados.append((row["Entrada"], row["Salida"], asignado[2], id))
                caja_matrix[asignado[2]].append(f"{row['Nombres']} - {row['Entrada'].strftime('%I:%M%p')} - {row['Salida'].strftime('%I:%M%p')}")
                asignados.pop(j)
                break
        else:
            for j, caja in enumerate(cajas):
                if (caja is None):
                    cajas[j] = row
                    asignados.append((row["Entrada"], row["Salida"], j, id))
                    caja_matrix[j].append(f"{row['Nombres']} - {row['Entrada'].strftime('%I:%M%p')} - {row['Salida'].strftime('%I:%M%p')}")
                    break
            else:
                cajeros_no_asignados.append(row)

    return caja_matrix, cajeros_no_asignados

def matriz_to_excel(matriz, nombre_archivo):
    # Crear un DataFrame a partir de la matriz
    df = pd.DataFrame(matriz)
    
    # Guardar el DataFrame en un archivo Excel
    df.to_excel(nombre_archivo, index=False, header=False)

def calcular_suma_tiempos_muertos_caja(caja):
    initial_time = pd.to_datetime("00:00AM")
    sum_tiempos_muertos = initial_time
    for i in range(1, len(caja)):
        entrada = caja[i-1].split(" - ")[2]
        salida = caja[i].split(" - ")[1]
        tiempo_muerto = pd.to_datetime(salida) - pd.to_datetime(entrada)
        sum_tiempos_muertos += tiempo_muerto
        
    return sum_tiempos_muertos - initial_time

def calcular_promedio_tiempos_muertos_matrix(caja_matrix):
    initial_time = pd.to_datetime("00:00AM")
    sum_tiempos_muertos = initial_time
    for caja in caja_matrix:
        caja_tiempo_muerto = calcular_suma_tiempos_muertos_caja(caja)
        sum_tiempos_muertos += caja_tiempo_muerto

    return (sum_tiempos_muertos - initial_time) / len(caja_matrix)

def sort_by_n_cajeros(caja_matrix):
    caja_matrix.sort(key=lambda x: len(x), reverse=True)
    return caja_matrix

def get_caja_tiempo_atencion(caja):
    initial_time = pd.to_datetime("00:00AM")
    sum_tiempos_atencion = initial_time
    for i in range(0, len(caja)):
        if (i == 0) and caja[i].startswith("Caja"):
            continue
        entrada = caja[i].split(" - ")[1]
        salida = caja[i].split(" - ")[2]
        tiempo_atencion = pd.to_datetime(salida) - pd.to_datetime(entrada)
        sum_tiempos_atencion += tiempo_atencion

    return sum_tiempos_atencion - initial_time

def sort_by_tiempo_atencion(caja_matrix):
    caja_matrix.sort(key=lambda x: get_caja_tiempo_atencion(x), reverse=True)
    return caja_matrix

def name_final_matrix(final_matrix):
    named_matrix = [row[:] for row in final_matrix]
    for i, caja in enumerate(named_matrix):
        if (i<3):
            caja.insert(0, f"Caja Rápida {i+1}")
        elif (i==3):
            caja.insert(0, f"Caja 1 Preferencial")
        else:
            caja.insert(0, f"Caja {i-2}")
    return named_matrix

def get_final_matrix(day_schedule_df, min_cajas, max_cajas):
    if (max_cajas > len(day_schedule_df)):
        max_cajas = len(day_schedule_df)

    n_cajas_optimo = 0
    min_caja_matrix = []
    min_cajeros_no_asignados = []

    min_tm = pd.to_datetime("00:00AM") - pd.to_datetime("00:00AM")

    for nro_cajas in range(min_cajas, max_cajas+1):
        res = get_caja_matrix(nro_cajas, day_schedule_df)
        tm = calcular_promedio_tiempos_muertos_matrix(res[0])

        if (nro_cajas == min_cajas):
            min_tm = tm
            n_cajas_optimo = nro_cajas
            min_caja_matrix = res[0]
            min_cajeros_no_asignados = res[1]
        else:
            if (tm < min_tm):
                min_tm = tm
                n_cajas_optimo = nro_cajas
                min_caja_matrix = res[0]
                min_cajeros_no_asignados = res[1]

    segmento1_matrix = sort_by_n_cajeros(min_caja_matrix)

    nro_cajas_restantes = max_cajas - n_cajas_optimo

    seg2_df = pd.DataFrame(min_cajeros_no_asignados, columns=['Nombres', 'Entrada', 'Salida'])
    seg2_df.sort_values(by=["Entrada"], inplace=True)
    res = get_caja_matrix(nro_cajas_restantes, seg2_df)
    segmento2_matrix = res[0]
    no_asignados = res[1]

    segmento2_matrix = sort_by_n_cajeros(segmento2_matrix)
    seg3_df = pd.DataFrame(no_asignados, columns=['Nombres', 'Entrada', 'Salida'])
    seg3_df.sort_values(by=["Entrada"], inplace=True)

    seg3_df["Entrada"] = seg3_df["Entrada"].dt.strftime('%I:%M%p')
    seg3_df["Salida"] = seg3_df["Salida"].dt.strftime('%I:%M%p')

    seg1_assig = sort_by_tiempo_atencion(segmento1_matrix)
    seg2_assig = sort_by_tiempo_atencion(segmento2_matrix)

    final_matrix = []
    final_matrix.append(seg1_assig[1])
    final_matrix.append(seg1_assig[2])
    final_matrix.append(seg2_assig[0])
    final_matrix.append(seg1_assig[0])
    for caja in seg1_assig[3:]:
        final_matrix.append(caja)
    for caja in seg2_assig[1:]:
        final_matrix.append(caja)

    return final_matrix    

def generar_excel_final_matrix(final_matrix, nombre_archivo="final_matrix.xlsx"):
    named_matrix = name_final_matrix(final_matrix)
    matriz_to_excel(named_matrix, nombre_archivo)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_path_exists(path):
    return os.path.exists(path)

def print_menu():
    print('''
1. Cargar Archivo (Input ruta)
2. Seleccionar Dia (L-D)
3. Mostrar Entradas
4. Mostrar Salidas
5. Generar Pronóstico
6. Configurar Min-Max de Cajas
7. Tools (Completar EAN)
8. Salir
''')
    
def print_day_selection_menu():
    print('''1. Lunes
2. Martes
3. Miércoles
4. Jueves
5. Viernes
6. Sábado
7. Domingo''')
    
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

data_path = "schedule.csv"
day = "Lunes"
min_cajas = 5
max_cajas = 15
pdf_path = "./horarios/Horario 01-07.24.pdf"
first_cajero = "BARRIENTOS JERI, MILAGROS NICOL"
first_rs = "ANTIALON MONDRAGON, JHEREMY"

get_schedule(pdf_path, first_cajero, first_rs)
day_schedule_df = get_day_schedule(data_path, day)

def main():
    global data_path
    global day
    global min_cajas
    global max_cajas
    global day_schedule_df
    global pdf_path
    global first_cajero
    global first_rs

    while True:
        clear()
        print(f"SuperPy v1 - Día: {day}")
        print_menu()
        try:
            option = int(input("Seleccione una opción: "))
        except:
            input("Opción inválida. Presione cualquier tecla para continuar...")
            continue
        match option:
            case 1:
                clear()
                pdf_path_op = input(f"Ingrese la ruta del archivo pdf {pdf_path}: ")
                if not check_path_exists(pdf_path):
                    pdf_path = pdf_path_op
                    input("Ruta seleccionada exitosamente. Presione cualquier tecla para continuar...")
                else:
                    op = input("El archivo ya existe. Desea sobreescribirlo? y/n: ")
                    if op == "y":
                        pdf_path = pdf_path_op
                        input("Ruta seleccionada exitosamente. Presione cualquier tecla para continuar...")
                    else:
                        input("Ruta no seleccionada. Presione cualquier tecla para continuar...")
                        continue
                clear()
                print("Ingrese el nombre del primer cajero y el primer RS")
                first_cajero_op = input(f"Primer cajero: [{first_cajero}]")
                if first_cajero_op != "":
                    first_cajero = first_cajero_op
                first_rs_op = input(f"Primer RS: [{first_rs}]")
                if first_rs_op != "":
                    first_rs = first_rs_op
                get_schedule(pdf_path, first_cajero, first_rs)
                day_schedule_df = get_day_schedule(data_path, day)
            case 2:
                clear()
                print_day_selection_menu()
                try:
                    day_index = int(input(f"Ingrese el día a analizar [{day}]: "))
                except:
                    input("El día debe ser un número. Presione cualquier tecla para continuar...")
                    continue
                match day_index:
                    case 1:
                        day = "Lunes"
                    case 2:
                        day = "Martes"
                    case 3:
                        day = "Miércoles"
                    case 4:
                        day = "Jueves"
                    case 5:
                        day = "Viernes"
                    case 6:
                        day = "Sábado"
                    case 7:
                        day = "Domingo"
                    case default:
                        input("Día inválido. Presione cualquier tecla para continuar...")
                        continue
                day_schedule_df = get_day_schedule(data_path, day)
                input(f"Día {day} seleccionado exitosamente. Presione cualquier tecla para continuar...")
            case 3:
                clear()
                print_entrada(day_schedule_df)
                input("Presione cualquier tecla para continuar...")
            case 4:
                clear()
                print_salida(day_schedule_df)
                input("Presione cualquier tecla para continuar...")
            case 5:
                clear()
                final_matrix = get_final_matrix(day_schedule_df, min_cajas, max_cajas)
                named_matrix = name_final_matrix(final_matrix)
                generar_excel_final_matrix(final_matrix)
                named_matrix_df = pd.DataFrame(named_matrix)
                print(named_matrix_df)
                input("Presione cualquier tecla para continuar...")
            case 6:
                clear()
                min_cajas_op = input(f"Ingrese el número mínimo de cajas [{min_cajas}]: ")
                try:
                    int(min_cajas_op)
                except:
                    input("El número mínimo de cajas debe ser un número. Presione cualquier tecla para continuar...")
                    continue

                max_cajas_op = input(f"Ingrese el número máximo de cajas [{max_cajas}]: ")
                try:
                    int(max_cajas_op)
                except:
                    input("El número máximo de cajas debe ser un número. Presione cualquier tecla para continuar...")
                    continue
                
                min_cajas_op = int(min_cajas_op)
                max_cajas_op = int(max_cajas_op)

                if (min_cajas_op > max_cajas_op):
                    input("El número mínimo de cajas no puede ser mayor al número máximo de cajas. Presione cualquier tecla para continuar...")
                else:
                    min_cajas = min_cajas_op
                    max_cajas = max_cajas_op
                    input("Número de cajas actualizado exitosamente. Presione cualquier tecla para continuar...")
            case 7:
                clear()
                cod = input("Ingrese el código EAN-12: ")
                ean13 = get_ean13(cod)
                print(f"El código EAN-13 es: {ean13}")
                input("Presione cualquier tecla para continuar...")
            case 8:
                break
            case default:
                pass

if __name__ == "__main__":
    main()