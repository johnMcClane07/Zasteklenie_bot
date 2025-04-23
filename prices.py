DATA = [
    {"file_id": "AgACAgIAAxkBAAMbZ9f8FE73DW0ttKsjSAUelRA9_J4AAmAKMhscF8BKm4EMLDrMBZ8BAAMCAAN5AAM2BA", "name": "Одностворчатое окно"},
    {"file_id": "AgACAgIAAxkBAAMhZ9gDTd8HE-FFEoepgOzg8KlBhLEAAhTvMRutsMFKpOMn-lRmtvEBAAMCAAN5AAM2BA", "name": "Двухстворчатое окно"},
    {"file_id": "AgACAgIAAxkBAAMjZ9gDbSqQQJTyVHMFj9b7Np2FFGsAAhbvMRutsMFKsWib8bbXuqcBAAMCAAN5AAM2BA", "name": "Трехстворчатое окно"},
    {"file_id": "AgACAgIAAxkBAAMlZ9gDnbzojbNVQ2qg5UZQ4NRoA94AAhjvMRutsMFKrK99Uh3xXJ8BAAMCAAN3AAM2BA", "name": "Балконный блок"},
]  


COMPLECTIONS = [
    {"name": "Базовая комплектация", "code": "base", "description": "Профильная система: Proplex Litex, 58 мм\nОстекление: двухкамерный стеклопакет\nФурнитура: Futuruss КОМФОРТ"},
    {"name": "Комплектация Комфорт", "code": "comfort", "description": "Профильная система: Exprof Profekta, 70 мм\nОстекление: двухкамерный стеклопакет\nФурнитура: Futuruss SMART ОКНА"},
    {"name": "Комплектация Смарт", "code": "smart", "description": "Профильная система: Kommerling, 70 мм\nОстекление: двухкамерный стеклопакет TERMO control\nФурнитура: ROTO"}
]

ADDITIONAL_SERVICES = [
    {"index": 0, "name": "Ручка ", "code": "handle_white"},
    {"index": 1, "name": "Подоконник 200 мм, Белый", "code": "windowsill_white"},
    {"index": 2, "name": "Отлив ", "code": "sill_white"},
    {"index": 3, "name": "Откосы ПВХ ", "code": "window_sills_pvc"},
    {"index": 4, "name": "Ламинация снаружи Золотой дуб", "code": "lamination_outside_gold_oak"},
    {"index": 5, "name": "Ламинация внутри Золотой дуб", "code": "lamination_inside_gold_oak"},
    {"index": 6, "name": "Москитная сетка", "code": "mosquito_net"}
]

BASE_PRICE_PER_M2 = {
    "Одностворчатое окно": 5000,  
    "Двухстворчатое окно": 6000,  
    "Трехстворчатое окно": 7000,  
    "Балконный блок": 8000  
}

COMPLECTION_PRICES = {
    "base": 0,        
    "comfort": 2000,  
    "smart": 4000     
}

EXTRA_PRICES = {
    "handle_white": 300,
    "windowsill_white": 1200,
    "sill_white": 1000,
    "window_sills_pvc": 2500,
    "lamination_outside_gold_oak": 3500,
    "lamination_inside_gold_oak": 3500,
    "mosquito_net": 800
}