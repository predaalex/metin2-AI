import builtins
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from tqdm import tqdm

# Timestamped logging
def print(*args, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    builtins.print(f"[{timestamp}]", *args, **kwargs)

# Configurable values
document_folder = "documente_iunie"
edge_driver_path = "../rustypot/edge_driver/msedgedriver.exe"
# document_folder = sys.argv[1]
# edge_driver_path = sys.argv[2]


# Path setup
root_path = os.getcwd()
xmldoc_dir = os.path.join(root_path, document_folder)
pdf_output_dir = os.path.join(xmldoc_dir, f"{document_folder}_pdf")

# Gather XML files (excluding those with 'semnatura')
xml_files = [f for f in os.listdir(xmldoc_dir) if f.endswith(".xml") and "semnatura" not in f]
print(f"Found {len(xml_files)} XML files to convert.")

# Create or update PDF output directory
if not os.path.exists(pdf_output_dir):
    os.mkdir(pdf_output_dir)
    print(f"Created output directory: {pdf_output_dir}")
else:
    existing_pdfs = {os.path.splitext(f)[0] for f in os.listdir(pdf_output_dir)}
    xml_files = [f for f in xml_files if os.path.splitext(f)[0] not in existing_pdfs]
    print(f"{len(xml_files)} files left to convert after skipping already converted ones.")

# Set Edge browser options
edge_options = Options()
edge_options.add_argument("--log-level=3")
edge_options.add_argument("--kiosk-printing")

# Silent PDF download preferences
prefs = {
    "download.default_directory": pdf_output_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "printing.print_preview_sticky_settings.appState": """
    {
        \"recentDestinations\": [{\"id\": \"Save as PDF\", \"origin\": \"local\", \"account\": \"\"}],
        \"selectedDestinationId\": \"Save as PDF\",
        \"version\": 2
    }
    """,
    "savefile.default_directory": pdf_output_dir
}
edge_options.add_experimental_option("prefs", prefs)

# Start Edge WebDriver
driver = webdriver.Edge(service=Service(edge_driver_path), options=edge_options)

try:
    driver.get("https://www.anaf.ro/uploadxml/")
    time.sleep(2)

    progress_bar = tqdm(total=len(xml_files))

    while xml_files:
        xml_file = xml_files.pop(0)
        progress_bar.set_description(f"Processing {xml_file}")

        try:
            # Upload XML file
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "upload_fisier"))
            )
            file_input.send_keys(os.path.join(xmldoc_dir, xml_file))

            # Enable upload button
            driver.execute_script("enable();")

            # Click upload button
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "uploadXml"))
            )
            upload_button.click()

            # Wait and click download PDF button
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "downloadPdf"))
            )
            download_button.click()

            # Trigger printing (Save as PDF)
            driver.execute_script("window.print();")
            time.sleep(3)

            # Navigate back
            driver.back()

            # Rename the downloaded file
            original_pdf = os.path.join(pdf_output_dir, "download.pdf")
            renamed_pdf = os.path.join(pdf_output_dir, f"{os.path.splitext(xml_file)[0]}.pdf")
            os.rename(original_pdf, renamed_pdf)

            progress_bar.update(1)

        except Exception as e:
            print(f"Error with file {xml_file}: {e}. Retrying later.")
            xml_files.append(xml_file)
            progress_bar.total += 1
            progress_bar.update(1)
            progress_bar.refresh()
            driver.get("https://www.anaf.ro/uploadxml/")

    print("Conversion completed successfully.")

finally:
    driver.quit()
