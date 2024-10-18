import requests
from bs4 import BeautifulSoup


# Функция для получения HTML-контента страницы
def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Ошибка при запросе страницы: {response.status_code}")
        return None


# Функция для поиска таблицы внутри второго <div class="col-12"> внутри <div id="divContent">
def find_table_in_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Ищем div с id "divContent"
    div_content = soup.find('div', id='divContent')

    if div_content:
        print("divContent is found")
        # Находим все div с class="col-12" внутри div с id="divContent"
        col_divs = div_content.find_all('div', class_='col-12')

        # Проверяем, что второй div найден
        if len(col_divs) > 1:
            second_col_div = col_divs[1]

            # Ищем таблицу внутри второго div с class="col-12"
            table = second_col_div.find('table')

            if table:
                print("Таблица найдена!")
                return table
            else:
                print("Таблица не найдена.")
        else:
            print("Второй <div class='col-12'> не найден.")
    else:
        print("Элемент с id='divContent' не найден.")

    return None


# Основная функция
def main():
    url = "https://kb-kubik.t8s.ru/Table/TeachersTime?Submitted=True&Page=0&School=46&BeginDate=2024-10-01T00%3A00%3A00&EndDate=2024-10-01T00%3A00%3A00&BeginTime=&EndTime=&Format=DayTimeEntity&Step=&Week=false&UnitedColumns=true&UnitedColumns=false&Inverted=false"

    # Получаем HTML-контент страницы
    page_content = get_page_content(url)

    if page_content:
        # Ищем таблицу внутри нужного div
        table = find_table_in_content(page_content)

        if table:
            print("HTML таблицы:")
            print(table.prettify())  # Выводим HTML-код таблицы для просмотра
        else:
            print("Таблица не найдена на странице.")


# Запуск программы
if __name__ == "__main__":
    main()
