from utils.pdf_utils import scrap_pdf

def test():
    pdf_paths = [
        "./horarios/Horario 01-07.24.pdf",
        "./horarios/Horario 04 al 10.pdf",
        "./horarios/Horario 11-18.pdf",
        "./horarios/Horario 25-31.pdf",
        "./horarios/Horario del 18 - 24 .pdf",
    ]
    
    for pdf_path in pdf_paths:
        print(f"Testing {pdf_path}")
        employees_list = scrap_pdf(pdf_path)
        for employee in employees_list:
            print(employee)
        print("\n\n")

if __name__ == "__main__":
    test()