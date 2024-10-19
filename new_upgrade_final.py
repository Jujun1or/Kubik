from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

# Инициализация Chrome с необходимыми параметрами
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Раскомментируйте, если хотите скрыть браузер
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL для доступа к страницам
url = 'https://kb-kubik.t8s.ru/Table/TeachersTime?Submitted=True&Page=0&School=46&BeginDate=2024-10-01T00%3A00%3A00&EndDate=2024-10-15T00%3A00%3A00&BeginTime=&EndTime=&Format=DayTimeEntity&Step=0%3A00&Week=false&UnitedColumns=false&Inverted=false'

try:
    driver.get(url)

    # Ожидание загрузки таблиц
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table.table-bordered'))
    )

    # Словарь для хранения всех данных
    all_teacher_data = {}
    teacher_profile_map = {}
    # Хранение связей между занятиями и преподавателями
    lesson_teacher_map = {}

    tables = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered')
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            teacher_cell = row.find_elements(By.TAG_NAME, 'th')
            if teacher_cell:
                teacher_info = teacher_cell[0].text.split('\n')[0].strip()
                hours_info = teacher_cell[0].text.split('\n')[1] if len(teacher_cell[0].text.split('\n')) > 1 else ''

                hours_match = re.search(r'\((\d+)', hours_info)
                hours_count = int(hours_match.group(1)) if hours_match else 0

                if teacher_info not in all_teacher_data:
                    all_teacher_data[teacher_info] = []

                cols = row.find_elements(By.TAG_NAME, 'td')
                for col in cols:
                    try:
                        lesson_link_element = col.find_element(By.TAG_NAME, 'a')
                        lesson_link = lesson_link_element.get_attribute('href').strip()
                        lesson_name = lesson_link_element.text.strip()

                        details = col.text.split('\n')
                        class_info = details[1][1:3] if len(details) > 1 else ''

                        profile_link_element = teacher_cell[0].find_elements(By.TAG_NAME, 'a')
                        if profile_link_element:
                            profile_link = profile_link_element[0].get_attribute('href').strip()
                            teacher_profile_map[
                                teacher_info] = profile_link  # Сохраняем ссылку на профиль преподавателя

                        lesson_details = {
                            'class_info': class_info,
                            'attendance': None,  # Посещаемость будет добавлена после парсинга страницы занятия
                            'lesson_link': lesson_link  # добавляем ссылку на занятие
                        }

                        if lesson_link not in lesson_teacher_map:
                            lesson_teacher_map[lesson_link] = []
                        lesson_teacher_map[lesson_link].append({
                            'teacher_info': teacher_info,
                            'hours_count': hours_count,
                            **lesson_details
                        })

                    except Exception as e:
                        print(f"Ошибка при обработке ячейки: {e}")

    # Теперь парсим страницы каждого занятия для получения информации о посещаемости
    for lesson_link, details in lesson_teacher_map.items():
        driver.get(lesson_link)

        try:
            # Проверяем наличие блока с учениками
            no_students_element = driver.find_element(By.XPATH,
                                                      '//fieldset[legend[text()="Занимающиеся ученики"]]/div[contains(text(), "Отсутствуют")]')
            result_attendance = 0
        except:
            try:
                # Ждем загрузку таблицы с учениками
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//fieldset[legend[text()="Занимающиеся ученики"]]/table'))
                )

                # Парсинг таблицы
                table = driver.find_element(By.XPATH, '//fieldset[legend[text()="Занимающиеся ученики"]]/table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                result_attendance = len(rows) - 1  # -1, чтобы исключить заголовок таблицы
            except Exception:
                result_attendance = 0  # Если таблица не найдена, посещаемость 0

        # Обновляем посещаемость для каждого учителя, связанного с этим занятием
        for detail in details:
            teacher_info = detail['teacher_info']
            all_teacher_data[teacher_info].append({
                'class_info': detail['class_info'],
                'attendance': result_attendance,  # Здесь обновляется посещаемость
                'level': 'Первый преподаватель'  # Позже можем обновить уровень
            })

    # Проходим по каждому профилю преподавателя, чтобы получить уровень
    for teacher_info, profile_link in teacher_profile_map.items():
        try:
            driver.get(profile_link)

            # Ожидание загрузки профиля
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-collapsable="100"]'))
            )

            # Принудительно показать скрытый элемент перед извлечением текста
            level_info_element = driver.find_element(By.CSS_SELECTOR, 'div[data-collapsable="100"]')
            driver.execute_script("arguments[0].style.display = 'block';", level_info_element)

            # Получение текста из элемента
            level_info = level_info_element.text

            # Определение уровня преподавателя на основе ключевых слов
            level = "Первый преподаватель"
            if any(keyword in level_info.lower() for keyword in ["2ой", "2 года", "второй", "второго"]):
                level = "Преподаватель 2 год"
            if any(keyword in level_info.lower() for keyword in ["вп", "ведушим", "ведущий"]):
                level = "Ведущий преподаватель"

            # Сохраняем информацию о уровне преподавателя
            all_teacher_data[teacher_info].append({
                'level': level
            })

        except Exception as e:
            print(f"Ошибка при получении данных профиля для {teacher_info}: {e}")
            all_teacher_data[teacher_info].append({
                'level': "Неизвестный уровень"
            })

    # Определение первого и второго преподавателя до обработки данных
    for lesson_link, details in lesson_teacher_map.items():
        if len(details) > 1:
            first_teacher = None
            highest_hours = -1

            for detail in details:
                hours_count = detail['hours_count']

                if hours_count > highest_hours:
                    highest_hours = hours_count
                    first_teacher = detail['teacher_info']

            for detail in details:
                teacher_info = detail['teacher_info']
                level = 'Первый преподаватель' if teacher_info == first_teacher else 'Второй преподаватель'

                # Обновляем данные в all_teacher_data, но не заменяем существующие значения level
                for teacher_detail in all_teacher_data[teacher_info]:
                    if 'class_info' in teacher_detail and teacher_detail['class_info'] == detail['class_info']:
                        # Если запись уже существует для этого класса, обновляем только level
                        teacher_detail['level'] = level
                        break
                else:
                    # Если запись отсутствует, добавляем новую
                    all_teacher_data[teacher_info].append({
                        'class_info': detail['class_info'],
                        'attendance': detail['attendance'],
                        'level': level
                    })

        else:
            # Если только один преподаватель, он первый
            detail = details[0]
            teacher_info = detail['teacher_info']

            # Обновляем данные в all_teacher_data, но не заменяем существующие значения level
            for teacher_detail in all_teacher_data[teacher_info]:
                if 'class_info' in teacher_detail and teacher_detail['class_info'] == detail['class_info']:
                    # Если запись уже существует для этого класса, обновляем только level
                    teacher_detail['level'] = 'Первый преподаватель'
                    break
            else:
                # Если запись отсутствует, добавляем новую
                all_teacher_data[teacher_info].append({
                    'class_info': detail['class_info'],
                    'attendance': detail['attendance'],
                    'level': 'Первый преподаватель'
                })

    # Удаляем пустые ключи, если они есть
    all_teacher_data.pop('', None)

    # Вывод итоговых данных

    # Вывод итоговых данных
    all_teacher_data.pop('', None)
    print(all_teacher_data)

finally:
    driver.quit()


teacher_payment = {}

for teacher_name, lessons in all_teacher_data.items():
    total_payment = 0  # Переменная для суммирования оплаты за занятия
    print(f"Преподаватель: {teacher_name}")
    teacher_status = lessons[-1]['level']
    for lesson in lessons[:-1]:
        day_payment = 0
        class_info = lesson['class_info']  # Получаем информацию о классе
        attendance = int(lesson['attendance'])  # Получаем посещаемость

        # Определяем уровень преподавателя (если он есть в уроке)
        if lesson['level'] != 'Второй преподаватель':
            level = teacher_status
        else:
            level = 'Второй преподаватель'

        # Вывод информации о занятии
        print(f"  Класс: {class_info}, Посещаемость: {attendance}, Статус: {level}")

        # Расчет оплаты для первого преподавателя
        if level == 'Первый преподаватель':
            if class_info[0:2] == 'ПШ':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 400
                else:
                    day_payment += 400 + (attendance - 2) * 50
            elif class_info[0] == 'П':
                if int(class_info[1]) <= 5:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 400
                    else:
                        day_payment += 400 + (attendance - 2) * 50
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 600
                    else:
                        day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'Р':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 400
                    else:
                        day_payment += 400 + (attendance - 2) * 50
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 600
                    else:
                        day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'М':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 460
                    else:
                        day_payment += 460 + (attendance - 2) * 60
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 600
                    else:
                        day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'X':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 600
                else:
                    day_payment += 600 + (attendance - 2) * 75

            elif class_info[0] == 'Ш':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 400
                else:
                    day_payment += 400 + (attendance - 2) * 50
            else:
                print("Ошибка расчета для ", teacher_name)
                exit(1)

        # Расчет оплаты для второго преподавателя
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
                        day_payment += 0
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

        elif level == 'Преподаватель 2 год':
            if class_info[0:2] == 'ПШ':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 420
                else:
                    day_payment += 420 + (attendance - 2) * 60
            elif class_info[0] == 'П':
                if int(class_info[1]) <= 5:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 420
                    else:
                        day_payment += 420 + (attendance - 2) * 60
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 630
                    else:
                        day_payment += 630 + (attendance - 2) * 90

            elif class_info[0] == 'Р':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 420
                    else:
                        day_payment += 420 + (attendance - 2) * 60
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 630
                    else:
                        day_payment += 630 + (attendance - 2) * 90

            elif class_info[0] == 'М':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 484
                    else:
                        day_payment += 484 + (attendance - 2) * 72
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 630
                    else:
                        day_payment += 630 + (attendance - 2) * 72

            elif class_info[0] == 'X':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 630
                else:
                    day_payment += 630 + (attendance - 2) * 90

            elif class_info[0] == 'Ш':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 420
                else:
                    day_payment += 420 + (attendance - 2) * 60
            else:
                print("Ошибка расчета для ", teacher_name)
                exit(1)

        elif level == 'Ведущий преподаватель':
            if class_info[0:2] == 'ПШ':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 440
                else:
                    day_payment += 440 + (attendance - 2) * 70
            elif class_info[0] == 'П':
                if int(class_info[1]) <= 5:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 440
                    else:
                        day_payment += 440 + (attendance - 2) * 70
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 660
                    else:
                        day_payment += 660 + (attendance - 2) * 105

            elif class_info[0] == 'Р':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 440
                    else:
                        day_payment += 440 + (attendance - 2) * 70
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 660
                    else:
                        day_payment += 660 + (attendance - 2) * 105

            elif class_info[0] == 'М':
                if int(class_info[1]) <= 2:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 508
                    else:
                        day_payment += 508 + (attendance - 2) * 84
                else:
                    if attendance == 0:
                        day_payment += 0
                    elif attendance in [1, 2]:
                        day_payment += 660
                    else:
                        day_payment += 660 + (attendance - 2) * 105

            elif class_info[0] == 'X':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 660
                else:
                    day_payment += 660 + (attendance - 2) * 105

            elif class_info[0] == 'Ш':
                if attendance == 0:
                    day_payment += 0
                elif attendance in [1, 2]:
                    day_payment += 440
                else:
                    day_payment += 440 + (attendance - 2) * 70
            else:
                print("Ошибка расчета для ", teacher_name)
                exit(1)

        else:
            print("Неизвестный статус преподавателя")
        # Вывод оплаты за занятие
        print("Оплата за занятие: ", day_payment)
        total_payment += day_payment
    teacher_payment[teacher_name] = {
        'total_payment': total_payment,  # Общая сумма
        'payment_na_ryki': total_payment * 0.9  # Сумма с вычетом 10%
    }

    # Вывод общей оплаты за период для преподавателя
    print("Оплата за выбранный период: ", total_payment)
    print("\n")  # Дополнительный переход на новую строку для удобства

    # Вывод общей оплаты за период для преподавателя
    print("Оплата за выбранный период: ", total_payment)
    print("\n")  # Дополнительный переход на новую строку для удобства

print("Оплата всех преподавателей:")
for teacher, payment_info in teacher_payment.items():
    print(f"Преподаватель: {teacher}")
    print(f"  Общая оплата: {payment_info['total_payment']}")
    print(f"  На руки: {payment_info['payment_na_ryki']}")
    print("-" * 40)