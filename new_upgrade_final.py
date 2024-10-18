from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
from collections import defaultdict

# Инициализация Chrome с необходимыми параметрами
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Раскомментируйте, если хотите скрыть браузер
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL для доступа к страницам
url = 'https://kb-kubik.t8s.ru/Table/TeachersTime?Submitted=True&Page=0&School=46&BeginDate=2024-10-01T00%3A00%3A00&EndDate=2024-10-15T00%3A00%3A00&BeginTime=&EndTime=&Format=DayTimeEntity&Step=&Week=false&UnitedColumns=false&Inverted=false'

try:
    driver.get(url)

    # Ожидание загрузки таблиц
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table.table-bordered'))
    )

    # Словарь для хранения всех данных преподавателей с профилем
    teacher_profile_map = {}

    # Словарь для хранения всех данных после посещения страниц профилей
    all_teacher_data = defaultdict(list)  # Используем defaultdict для автоматического создания списков

    tables = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered')
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            teacher_cell = row.find_elements(By.TAG_NAME, 'th')
            if teacher_cell:
                # Получаем информацию о преподавателе и ссылку на профиль
                teacher_info = teacher_cell[0].text.split('\n')[0].strip()

                profile_link_element = teacher_cell[0].find_elements(By.TAG_NAME, 'a')
                if profile_link_element:
                    profile_link = profile_link_element[0].get_attribute('href').strip()
                    teacher_profile_map[teacher_info] = profile_link  # Сохраняем ссылку на профиль преподавателя

    # Теперь проходим по каждому профилю, чтобы получить информацию о уровне преподавателя
    for teacher_info, profile_link in teacher_profile_map.items():
        try:
            driver.get(profile_link)

            # Ожидание загрузки профиля
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-collapsable="100"]'))
            )

            # Принудительно показать скрытый элемент перед извлечением текста
            level_info_element = driver.find_element(By.CSS_SELECTOR, 'div[data-collapsable="100"]')
            driver.execute_script("arguments[0].style.display = 'block';", level_info_element)

            # Получение текста из элемента
            level_info = level_info_element.text

            # Определение уровня преподавателя на основе ключевых слов
            if any(keyword in level_info for keyword in ["2 год", "2", "второй", "Второй", "второго"]):
                level = "Преподаватель 2 год"
            elif "ведущий" in level_info.lower():
                level = "Ведущий преподаватель"
            else:
                level = "Первый преподаватель"  # По умолчанию

            # Сохраняем информацию о уровне преподавателя
            all_teacher_data[teacher_info].append({
                'level': level
            })

        except Exception as e:
            print(f"Ошибка при получении данных профиля для {teacher_info}: {e}")
            all_teacher_data[teacher_info].append({
                'level': "Неизвестный уровень"
            })

    # Вывод всех данных
    print(all_teacher_data)

except Exception as e:
    print(f"Ошибка во время выполнения: {e}")

finally:
    driver.quit()

for teacher_name, lessons in all_teacher_data.items():
    total_payment = 0  # Переменная для суммирования оплаты за занятия
    print(f"Преподаватель: {teacher_name}")
    for lesson in lessons:
        day_payment = 0
        class_info = lesson['class_info']  # Получаем информацию о классе
        attendance = int(lesson['attendance'])  # Получаем посещаемость
        level = lesson['level']

        # Вывод информации о занятии
        print(f"  Класс: {class_info}, Посещаемость: {attendance}")
        if level == 'Первый преподаватель':
            if class_info[0:2] == 'ПШ':
                if attendance == 0:
                    day_payment += 0
                elif attendance == 1 or attendance == 2:
                    day_payment += 400
                else:
                    day_payment += 400 + (attendance - 2) * 50
            elif class_info[0] == 'П':
                if int(class_info[1]) <= 5:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance == 1 or attendance == 2:
                        day_payment += 400
                    else:
                        day_payment += 400 + (attendance - 2) * 50
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance == 1 or attendance == 2:
                        day_payment += 600
                    else:
                        day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'Р':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance == 1 or attendance == 2:
                        day_payment += 400
                    else:
                        day_payment += 400 + (attendance - 2) * 50
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance == 1 or attendance == 2:
                        day_payment += 600
                    else:
                        day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'М':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance == 1 or attendance == 2:
                        day_payment += 460
                    else:
                        day_payment += 460 + (attendance - 2) * 60
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance == 1 or attendance == 2:
                        day_payment += 600
                    else:
                        day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'X':
                if attendance == 0:
                    day_payment += 0
                elif attendance == 1 or attendance == 2:
                    day_payment += 600
                else:
                    day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'Ш':
                if attendance == 0:
                    day_payment += 0
                elif attendance == 1 or attendance == 2:
                    day_payment += 400
                else:
                    day_payment += 400 + (attendance - 2) * 50
            else:
                print("Ошибка расчета для ", teacher_name)
                exit(1)

        elif level == 'Второй преподаватель':
            if class_info[0:2] == 'ПШ':
                if attendance == 0:
                    day_payment += 0
                else:
                    day_payment += 400
            elif class_info[0] == 'П':
                if int(class_info[1]) <= 5:
                    if attendance == 0:
                        day_payment += 0
                    else:
                        day_payment += 400
                else:
                    if attendance == 0:
                        day_payment += 0
                    else:
                        day_payment += 600

            elif class_info[0] == 'Р':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    else:
                        day_payment += 400
                else:
                    if attendance == 0:
                        day_payment += 00
                    else:
                        day_payment += 600

            elif class_info[0] == 'M':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    else:
                        day_payment += 460
                else:
                    if attendance == 0:
                        day_payment += 0
                    else:
                        day_payment += 600

            elif class_info[0] == 'X':
                if attendance == 0:
                    day_payment += 0
                else:
                    day_payment += 600

            elif class_info[0] == 'Ш':
                if attendance == 0:
                    day_payment += 0
                else:
                    day_payment += 400
            else:
                print("Ошибка расчета для ", teacher_name)
                exit(1)

        print("Оплата за занятие: ", day_payment)
        total_payment += day_payment
    print("Оплата за выбранный период: ", total_payment)

    print("\n")  # Дополнительный переход на новую строку для удобства
