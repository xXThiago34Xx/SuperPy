import pandas as pd
from PyPDF2 import PdfReader

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
            # Eliminar tiempo de PAGO HORAS FERIADO
            id = pdf_list[i+1].find(":") + 3
            pdf_list[i+1] = pdf_list[i+1][id:]
            if pdf_list[i+1] == "":
                pdf_list.pop(i+1)
                n-=1
        if not pdf_list[i][0].isdigit():
            # Unir celdas que no son horas
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



# pdf_path = "./horarios/Horario 04 al 10.pdf"
# first_cajero = "BARRIENTOS JERI, MILAGROS NICOL"
# first_rs = "ANTIALON MONDRAGON, JHEREMY"

# pdf_path = "./horarios/Horario 11-18.pdf"
# first_cajero = "BARRIENTOS JERI, MILAGROS NICOL"
# first_rs = "GUERRERO CALSINA, SANDRA"

# pdf_path = "./horarios/Horario 25-31.pdf"
# first_cajero = "BARRIENTOS JERI, MILAGROS NICOL"
# first_rs = "ANTIALON MONDRAGON, JHEREMY"

# pdf_path = "./horarios/Horario del 18 - 24 .pdf"
# first_cajero = "BARRIENTOS JERI, MILAGROS NICOL"
# first_rs = "GUERRERO CALSINA, SANDRA"

pdf_path = "./horarios/Horario 01-07.24.pdf"
first_cajero = "BARRIENTOS JERI, MILAGROS NICOL"
first_rs = "ANTIALON MONDRAGON, JHEREMY"

get_schedule(pdf_path, first_cajero, first_rs)