import os
import win32print
import win32api

printer_name = win32print.GetDefaultPrinter()

printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)

print(f"Available printers:")
for flags, description, name, comment in printers:
    print(f"Printer Name: {name}")

print(f"Default Printer Name: {printer_name}")

folder_path = "documente_iunie/documente_iunie_pdf"
pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

for pdf_file in pdf_files:
    full_path = os.path.join(folder_path, pdf_file)
    print(f"Printing: {full_path}")
    win32api.ShellExecute(
        0,
        "print",
        full_path,
        None,
        ".",
        0
    )
