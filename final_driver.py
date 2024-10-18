from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Инициализация Chrome с необходимыми параметрами
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Раскомментируйте, если хотите скрыть браузер
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL для доступа к страницам
url = 'https://kb-kubik.t8s.ru/Table/TeachersTime?Submitted=True&Page=0&School=46&BeginDate=2024-10-01T00%3A00%3A00&EndDate=2024-10-15T00%3A00%3A00&BeginTime=&EndTime=&Format=DayTimeEntity&Step=&Week=false&UnitedColumns=false&Inverted=false'

try:
    # Показать страницу
    driver.get(url)

    # Ожидание загрузки таблиц
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table.table-bordered'))
    )

    # Словарь для хранения всех данных
    all_teacher_data = {}

    # Находим все таблицы на странице
    tables = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered')

    for table in tables:
        # Сбор данных из строк таблицы
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            # Извлечение имени преподавателя
            teacher_cell = row.find_elements(By.TAG_NAME, 'th')
            if teacher_cell:
                # Извлечение имени преподавателя без лишней информации (после '\n')
                teacher_name = teacher_cell[0].text.split('\n')[0].strip()  # Берем только первую часть
                if teacher_name not in all_teacher_data:
                    all_teacher_data[teacher_name] = []

                    # Сбор данных из ячеек (td)
                cols = row.find_elements(By.TAG_NAME, 'td')
                for col in cols:
                    try:
                        # Найдем элемент <a> внутри ячейки
                        lesson_link_element = col.find_element(By.TAG_NAME, 'a')
                        lesson_name = lesson_link_element.text.strip()  # Игнорируем lesson_name

                        # Извлечение информации о классе, времени и количестве учеников
                        details = col.text.split('\n')
                        class_info = details[1][1:3] if len(details) > 1 else ''
                        attendance = col.find_element(By.CLASS_NAME, 'LinkWrapper24').find_element(By.TAG_NAME,
                                                                                                   'div').text.strip()

                        # Сохранение информации о занятии (оставляем только класс и посещаемость)
                        all_teacher_data[teacher_name].append({
                            'class_info': class_info,
                            'attendance': attendance,
                            'level': 'ВОТ ЗДЕСЬ ДОЛЖНО БЫТЬ НАПИСАНО ПЕРВЫЙ ПРЕПОДАВАТЕЛЬ ИЛИ ВТОРОЙ ПРЕПОДАВАТЕЛЬ'
                        })

                    except Exception as e:
                        print(f"Ошибка при обработке ячейки: {e}")

                        # Выводим собранные данные
    print(all_teacher_data)

except Exception as e:
    print(f'Ошибка: {e}')
finally:
    driver.quit()