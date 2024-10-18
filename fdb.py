from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Укажите путь к вашему драйверу (это должен быть путь к chromedriver, а не к chrome)
driver_path = 'C:/Users/rmedv/source/repos/chrome-win64/chromedriver.exe'  # Замените на ваш путь к chromedriver
url = 'https://kb-kubik.t8s.ru/Table/TeachersTime?Submitted=True&Page=0&School=46&BeginDate=2024-10-14T00%3A00%3A00&EndDate=2024-12-14T00%3A00%3A00&BeginTime=&EndTime=&Format=DayTimeEntity&Step=&Week=false&UnitedColumns=true&UnitedColumns=false&Inverted=false'

chrome_options = Options()
chrome_service = Service(driver_path)

# Инициализация драйвера
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get(url)

try:
    # Ожидание загрузки таблицы (замените селектор на правильный)
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered'))  # Используйте селектор для вашего класса
    )

    # Получение данных из таблицы
    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if cols:  # Проверяем, есть ли колонки в строке
            data = [col.text for col in cols]
            print(data)

except Exception as e:
    print(f'Ошибка: {e}')
finally:
    driver.quit()