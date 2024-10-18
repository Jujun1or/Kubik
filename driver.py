from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Укажите параметры для Chrome (если нужно)
chrome_options = Options()
# Пример: chrome_options.add_argument("--headless")  # запуск в фоновом режиме, без GUI

# Инициализация драйвера с помощью webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url = 'https://kb-kubik.t8s.ru/Table/TeachersTime?Submitted=True&Page=0&School=46&BeginDate=2024-10-01T00%3A00%3A00&EndDate=2024-10-15T00%3A00%3A00&BeginTime=&EndTime=&Format=DayTimeEntity&Step=&Week=false&UnitedColumns=false&Inverted=false'
# Ваш код для работы с браузером
driver.get(url)

print("Chrome Version: ", driver.capabilities['browserVersion'])
print("ChromeDriver Version: ", driver.capabilities['chrome']['chromedriverVersion'])
try:
    # Ожидание загрузки таблицы (замените селектор на правильный)
    table = WebDriverWait(driver, 60).until(
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