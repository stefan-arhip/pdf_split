import PyPDF2
import re
import argparse
import os.path
import csv
import sys

def split_pdf_by_furnizor(input_pdf, output_dir):
    """
    Primul script creat în Python de stefan-arhip, 20240829-1530

    Împarte un PDF în fișiere separate bazat pe secțiunile "Furnizor:".
    Numele fișierelor sunt generate din valoarea "Index incarcare:".

    Args:
        input_pdf (str): Calea către fișierul PDF de intrare.
        output_dir (str): Directorul în care vor fi salvate fișierele PDF de ieșire.
    """
    with open(input_pdf, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        output_pdf = PyPDF2.PdfWriter()
        current_index = None
        start_page = None
        prefix_file = ""
        extracted_files = 0
        skiped_files = 0

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            file_counter = 0

            # Găsim textul "Furnizor:"
            if "Furnizor:" in text:
                # Dacă avem deja un fișier început, îl salvăm
                if len(output_pdf.pages) > 0:  
                    extracted_files = extracted_files + 1
                    with open(f"{output_dir}/{output_filename}", 'wb') as new_pdf:
                        output_pdf.write(new_pdf)
                    output_pdf = PyPDF2.PdfWriter()
                start_page = page_num

            # Găsim textul "Index incarcare:"
            match = re.search(r"Index incarcare: (.*)", text)
            if match:
                current_index = match.group(1).strip()
                output_filename = f"{prefix_file}{current_index}.pdf"
                skip_file = 0
                if os.path.isfile(f"{output_dir}/{output_filename}"):
                    #print('    Exista deja fisierul: ',output_filename)
                    skip_file = 1
                    skiped_files = skiped_files + 1
                
            # Adăugăm pagina la fișierul curent
            if skip_file == 0:
                output_pdf.add_page(page)

        # Salvăm ultimul fișier
        if len(output_pdf.pages) > 0:
            extracted_files = extracted_files + 1
            with open(f"{output_dir}/{output_filename}", 'wb') as new_pdf:
                output_pdf.write(new_pdf)
        if extracted_files != 0:
            print('   * s-au extras ',extracted_files,' fisiere din ',len(pdf_reader.pages),' pagini')
        if skiped_files != 0:
            print('   * nu s-au salvat ',skiped_files,' fisiere care existau deja')

def citire_fisier(fisier):
    with open(fisier, 'r') as f:
        reader = csv.reader(f, delimiter=' ')  # Delimiter=' ' variabilele sunt separate prin spații
        data = list(reader)
    return data

if __name__ == "__main__":
    param_count = len(sys.argv)
    script_path = os.path.abspath(__file__)
    script_name = os.path.basename(script_path)
    input_file, _ = os.path.splitext(script_name)
    input_file = os.path.join(os.path.dirname(script_path), input_file + ".txt")

    if param_count-1 == 0:
        print("Nu s-a specificat nici un fisier, se foloseste: ", input_file)
        if os.path.isfile(f"{input_file}"):
            date = citire_fisier(f"{input_file}")
        else:
            date = []
            print("Nu a fost gasit fisierul: ", input_file)
    elif param_count-1 == 1:
        parser = argparse.ArgumentParser(description="Imparte un PDF in fisiere separate bazat pe sectiunile \"Furnizor:\".")    
        parser.add_argument("file_list", help="Calea catre lista de fisiere de procesat")
        args = parser.parse_args()
        input_file = args.file_list
        date = citire_fisier(f"{input_file}")        
    elif param_count-1 == 2:
        parser = argparse.ArgumentParser(description="Imparte un PDF în fisiere separate bazat pe sectiunile \"Furnizor:\".")
        parser.add_argument("input_file", help="Calea catre fisierul PDF de intrare")
        parser.add_argument("output_folder", help="Directorul in care vor fi salvate fisierele PDF de iesire")
        args = parser.parse_args()
        linie = [f"{args.input_file}",f"{args.output_folder}"]
        date = [linie]
    else:
        print("Imparte un PDF in fisiere separate bazat pe sectiunile \"Furnizor:\".")
        print("Scriptul functioneaza:")
        print("   - fara nici un parametru (procesand fisierul din script <",input_file,">)")
        print("   - cu un parametru (fisier ce contine lista .pdf-urilor de procesat)")
        print("   - cu doi parametri (fisierul .pdf de procesat si directorul tinta)!")
        date = ""

    for linie in date:
        print(linie)
        if len(linie) == 0:
            print("Ignor linia goala")
        else:
            pdf_file, output_folder = linie        
            if os.path.isfile(f"{pdf_file}"):
                if pdf_file.lower().endswith(('.pdf')):
                    if os.path.exists(f"{output_folder}"):
                        print("Se proceseaza fisierul: ", pdf_file)
                        split_pdf_by_furnizor(pdf_file, output_folder)
                    else:
                        print("Nu exista directorul: ", output_folder)
                else:
                    print("Fisierul nu are extensia .pdf: ", pdf_file)
            else:
                print("Nu a fost gasit fisierul: ", pdf_file)
