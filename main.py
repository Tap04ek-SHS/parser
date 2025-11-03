import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import requests
import atexit
from datetime import datetime

# Данные для заполнения
CHAT_ID = 
imya = ""
familia = ""
otchestvo = ""
nomer_passporta = ""
email = ""
parrol = ""
TOKEN = ""


def send_notification():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "БИЛЕТ НАЙДЕН"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Не удалось отправить сообщение: {e}")


# Регистрируем функцию для вызова при завершении программы
atexit.register(send_notification)

# Настройка драйвера в HEADLESS режиме для фоновой работы
options = Options()
# Активируем HEADLESS-режим для работы без экрана!
options.add_argument("--headless=new")
# Убеждаемся, что разрешение установлено для стабильного рендеринга
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)


def check_for_tickets():
    """Бесконечная проверка наличия билетов"""
    check_count = 0

    while True:
        try:
            check_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Проверка #{check_count}...")

            driver.get(
                "https://pass.rw.by/ru/route/?from=%D0%9C%D0%BE%D0%B7%D1%8B%D1%80%D1%8C&from_exp=2100254&from_esr=151605&to=%D0%9C%D0%B8%D0%BD%D1%81%D0%BA-%D0%9F%D0%B0%D1%81%D1%81%D0%B0%D0%B6%D0%B8%D1%80%D1%81%D0%BA%D0%B8%D0%B9&to_exp=0&to_esr=0&front_date=13+%D0%BD%D0%BE%D1%8F.+2025&date=2025-11-10")

            # Ожидание загрузки страницы
            time.sleep(5)

            # Закрытие cookie-баннера если есть
            try:
                knopka_protiv_cookie = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="cookies-popup"]/div[2]/div/div[2]/button[1]'))
                )
                driver.execute_script("arguments[0].click();", knopka_protiv_cookie)
                print("Cookie баннер закрыт")
                time.sleep(2)
            except:
                pass  # Если нет cookie баннера - продолжаем

            # Проверка наличия кнопки "Выбрать"
            selectors = [
                '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/main/div[2]/div[3]/div[2]/div[1]/div[3]/div/div[1]/div/div[4]/div[2]/form/a'
            ]

            ticket_found = False
            for selector in selectors:
                try:
                    knopka_choosa = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print("БИЛЕТ НАЙДЕН! Кнопка 'Выбрать' обнаружена.")
                    ticket_found = True
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if ticket_found:
                # Нашли билет - переходим к бронированию
                process_booking()
                break
            else:
                print("Билеты еще не доступны. Обновляем страницу...")
                # Обновляем страницу и ждем перед следующей проверкой
                driver.refresh()
                time.sleep(10)  # Ждем загрузки страницы после обновления

        except Exception as e:
            print(f"Ошибка при проверке: {e}")
            # В случае ошибки ждем немного и продолжаем
            time.sleep(60)


def process_booking():
    """Обработка бронирования когда билет найден"""
    try:
        # Клик по кнопке выбора места
        selectors = [
            '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/main/div[2]/div[3]/div[2]/div[1]/div[3]/div/div[1]/div/div[4]/div[2]/form/a',
            '//a[contains(@class, "btn") and contains(text(), "Выбрать")]'
        ]

        for selector in selectors:
            try:
                knopka_choosa = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", knopka_choosa)
                driver.execute_script("arguments[0].click();", knopka_choosa)
                print("Переход к выбору места")
                break
            except:
                continue

        try:
            knopka_protiv_cookie = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cookies-popup"]/div[2]/div/div[2]/button[1]'))
            )
            driver.execute_script("arguments[0].click();", knopka_protiv_cookie)
            print("Cookie баннер закрыт")
            time.sleep(2)
        except:
            pass  # Если нет cookie баннера - продолжаем

        # Дальнейшие шаги бронирования...
        book_ticket()

    except Exception as e:
        print(f"Ошибка при бронировании: {e}")
        # Если ошибка при бронировании, начинаем проверку заново
        check_for_tickets()


def book_ticket():
    """Процесс бронирования билета"""
    try:
        # Прокрутка к ориентиру
        orientir = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app-place-choice"]/div[2]/div[2]/div[2]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", orientir)

        # Поиск вагонов
        massiv_vagonov = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pl-accord__link-wrap"))
        )
        print(f"Найдено вагонов: {len(massiv_vagonov)}")

        if massiv_vagonov:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                  massiv_vagonov[0])
            time.sleep(2)
            driver.execute_script("arguments[0].click();", massiv_vagonov[0])
            print("Вагон выбран")

        # Данные пассажира
        dannie_passagira = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-place-choice"]/div[2]/div[4]/div/form/div[1]/div/div/div/div[2]/div[2]/div/a'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", dannie_passagira)
        driver.execute_script("arguments[0].click();", dannie_passagira)

        # Заполнение данных...
        fill_passenger_data()

    except Exception as e:
        print(f"Ошибка при бронировании: {e}")


def fill_passenger_data():
    """Заполнение данных пассажира"""
    try:
        # Заполнение email
        email_pole = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="form-auth"]/fieldset/div[1]/label/div[2]/input'))
        )
        email_pole.clear()
        email_pole.send_keys(email)
        print("Email введен")

        # Заполнение пароля
        password_pole = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="form-auth"]/fieldset/div[2]/div[1]/div/label/div[2]/input'))
        )
        password_pole.clear()
        password_pole.send_keys(parrol)
        print("Пароль введен")

        # Вход
        voiti_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="form-auth"]/fieldset/div[3]/input'))
        )
        driver.execute_script("arguments[0].click();", voiti_button)
        print("Вход выполнен")
        time.sleep(3)

        # Повторный поиск вагонов после входа
        select_vagon_after_login()

        # Данные пассажира после входа
        dannie_passagira1 = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '//*[@id="app-place-choice"]/div[2]/div[4]/div/form/div[1]/div/div/div/div[2]/div[2]/div/a'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", dannie_passagira1)
        driver.execute_script("arguments[0].click();", dannie_passagira1)
        print("Переход к данным пассажира")
        time.sleep(2)

        # Заполнение данных пассажира
        fill_passenger_info()

    except Exception as e:
        print(f"Ошибка в fill_passenger_data: {e}")
        raise


def select_vagon_after_login():
    """Повторный поиск и выбор вагона после входа"""
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            print(f"Попытка {attempt + 1} найти вагоны после входа...")

            # Поиск вагонов
            massiv_vagonov = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pl-accord__link-wrap"))
            )
            print(f"Найдено вагонов: {len(massiv_vagonov)}")

            if massiv_vagonov:
                # Прокрутка к первому вагону
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                      massiv_vagonov[0])
                time.sleep(2)

                # Клик по первому вагону
                driver.execute_script("arguments[0].click();", massiv_vagonov[0])
                print("Вагон выбран после входа")
                time.sleep(3)
                return True

        except Exception as e:
            print(f"Ошибка при поиске вагонов (попытка {attempt + 1}): {e}")
            if attempt < max_attempts - 1:
                print("Повторная попытка через 3 секунды...")
                time.sleep(3)
                driver.refresh()
                time.sleep(5)
            else:
                print("Не удалось найти вагоны после всех попыток")
                return False


def fill_passenger_info():
    """Заполнение информации о пассажире"""
    try:
        # Фамилия
        pole_familii = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="passengersInfo"]/div[3]/div[2]/div/form/fieldset/div[1]/div[1]/div/label/div[2]/input'))
        )
        pole_familii.clear()
        pole_familii.send_keys(familia)
        print("Фамилия введена")
        time.sleep(0.5)

        # Имя
        pole_imeni = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="passengersInfo"]/div[3]/div[2]/div/form/fieldset/div[1]/div[2]/div/label/div[2]/input'))
        )
        pole_imeni.clear()
        pole_imeni.send_keys(imya)
        print("Имя введено")
        time.sleep(0.5)

        # Отчество
        pole_otchestvo = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="passengersInfo"]/div[3]/div[2]/div/form/fieldset/div[1]/div[3]/div/label/div[2]/input'))
        )
        pole_otchestvo.clear()
        pole_otchestvo.send_keys(otchestvo)
        print("Отчество введено")
        time.sleep(0.5)

        # Паспорт
        pole_passport = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH,
                                              '//*[@id="passengersInfo"]/div[3]/div[2]/div/form/fieldset/div[1]/div[5]/div/label/div[2]/input'))
        )
        pole_passport.clear()
        pole_passport.send_keys(nomer_passporta)
        print("Паспорт введен")
        time.sleep(0.5)

        # Чекбокс
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="contact-info_form"]/div/div[1]/div/label/div/div'))
        )
        driver.execute_script("arguments[0].click();", checkbox)
        print("Чекбокс отмечен")
        time.sleep(1)

        # Оформление заказа
        offormit_zakaz = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="contact-info_form"]/div/div[2]/button'))
        )
        driver.execute_script("arguments[0].click();", offormit_zakaz)
        print("Заказ оформлен!")

    except Exception as e:
        print(f"Ошибка при заполнении данных пассажира: {e}")
        raise

# Запуск бесконечной проверки
try:
    check_for_tickets()
except KeyboardInterrupt:
    print("Программа остановлена пользователем")
finally:
    driver.quit()
