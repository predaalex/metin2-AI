import builtins
import os
import shutil
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from tqdm import tqdm
import sys

import time


def print(*args, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    builtins.print(f"[{timestamp}] ", *args, **kwargs)




root_path = os.getcwd()

# dir = "documente_test"
dir = sys.argv[1]
path_to_files_to_convert = os.path.join(root_path, dir)  # MODIFY THE CONVERSION FILE
files_to_convert = [path for path in os.listdir(path_to_files_to_convert) if path.endswith(".xml") and "semnatura" not in path]
print(f"There are {len(files_to_convert)} files to be converted")

# Browser Setup
# EDGE_DRIVER_PATH = "edgedriver_win64/msedgedriver.exe"
EDGE_DRIVER_PATH = "../rustypot/edge_driver/msedgedriver.exe"
EDGE_DRIVER_PATH = sys.argv[2]
# Set up Edge options for silent printing
options = Options()
options.add_argument("--log-level=3")  # Suppresses INFO and WARNING logs
options.add_argument('--kiosk-printing')  # Enable silent printing

# Specify a default download directory for saving printed PDFs
download_dir = os.path.join(path_to_files_to_convert, f"{dir}_pdf")

if not os.path.exists(download_dir):
    os.mkdir(download_dir)
    print(f"directory has been created!\n{download_dir}")
else:
    base_name_files_to_convert = [path[:-4] for path in files_to_convert]
    files_already_converted = os.listdir(download_dir)
    for file_already_converted_path in files_already_converted:
        base_name_file_already_converted_path = file_already_converted_path[:-4]
        if base_name_file_already_converted_path in base_name_files_to_convert:
            print(f"{base_name_file_already_converted_path}.xml Already converted")
            files_to_convert.remove(f"{base_name_file_already_converted_path}.xml")
    print(f"There are {len(files_to_convert)} files left to be converted")
    # shutil.rmtree(download_dir)
    # os.mkdir(download_dir)
    # print(f"NEW directory has been created!\n{download_dir}")

preferences = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,  # Disable download prompt
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "printing.print_preview_sticky_settings.appState": """
    {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    """,
    "savefile.default_directory": download_dir  # Set default save location
}

options.add_experimental_option("prefs", preferences)

# Initialize the Edge WebDriver
driver = webdriver.Edge(service=Service(EDGE_DRIVER_PATH), options=options)


try:
    #### 1. OPEN PAGE #####
    # Open the target webpage
    driver.get("https://www.anaf.ro/uploadxml/")  # Replace with the actual URL

    # driver.maximize_window()

    time.sleep(2)
    #### 1. OPEN PAGE #####
    progress_bar = tqdm(total=len(files_to_convert))
    # for file_path in tqdm(files_to_convert):
    while len(files_to_convert) > 0:
        file_path = files_to_convert.pop(0)
        progress_bar.set_description(f"Processing {file_path}")
        try :
            #### 2. SELECT THE RECEIPT XML ####
            # Step 1: Select a file
            file_input_locator = (By.ID, "upload_fisier")
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(file_input_locator)
            )
            # full_file_path = f"{path_to_files_to_convert}/{file_path}"
            full_file_path = os.path.join(path_to_files_to_convert, file_path)
            file_input.send_keys(full_file_path)
            # print(f"File {file_path} selected successfully!")

            # Step 2: Trigger the enable() function using JavaScript
            driver.execute_script("enable();")

            # Step 3: Wait for the 'Incarcare XML' button to become enabled and click it
            upload_button_locator = (By.ID, "uploadXml")
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(upload_button_locator)
            )
            upload_button.click()
            # print("Upload button clicked!")

            ##### 3. DOWNLOAD RECEIPT ####
            # Step 1. Press download butto
            download_button_locator = (By.ID, "downloadPdf")
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(download_button_locator)
            )
            download_button.click()
            # print("Download button clicked!")

            driver.execute_script("window.print();")

            time.sleep(3)
            driver.back()
            # rename downloaded element
            initial_download_file_path = os.path.join(download_dir, "download.pdf")
            new_download_file_path = os.path.join(download_dir, f"{file_path[:-4]}.pdf")
            os.rename(initial_download_file_path, new_download_file_path)
            progress_bar.update(1)
        except Exception as e:
            # print(f"ERROR handled for file {file_path}. It will be retried")
            files_to_convert.append(file_path)
            progress_bar.total += 1
            progress_bar.update(1)
            progress_bar.refresh()

    print(f"Conversion finished!")
finally:
    # Close the browser
    driver.quit()
