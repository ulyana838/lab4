from django.shortcuts import render
from django.http import HttpResponse
from .forms import RecipeForm
import os
import xml.etree.ElementTree as ET

# Функция для создания или обновления XML файла
def create_or_update_xml_file(data):
    file_path = "recipes.xml"

    # Проверка существования файла и его размера
    if os.path.exists(file_path):
        if os.path.getsize(file_path) == 0:
            # Если файл пустой, создаем новый корневой элемент
            root = ET.Element("dish")
            tree = ET.ElementTree(root)
        else:
            # Если файл существует и не пустой, парсим его
            tree = ET.parse(file_path)
            root = tree.getroot()
    else:
        # Если файл не существует, создаем новый корневой элемент
        root = ET.Element("data")
        tree = ET.ElementTree(root)

    # Ключи для проверки дублирования записей
    keys = ['name', 'ingredients', 'instructions', 'cooking_time']

    # Проверка на дублирование записи
    is_duplicate = any(
        all(existing_entry.find(key).text == str(data[key]) for key in keys)
        for existing_entry in root.findall('entry')
    )

    if not is_duplicate:
        # Если запись не дублируется, добавляем новую запись
        entry = ET.SubElement(root, "entry")
        for key, value in data.items():
            recipt_min = ET.SubElement(entry, key)
            recipt_min.text = str(value)

        # Форматируем XML и сохраняем его
        ET.indent(tree, space="  ", level=0)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        return True
    else:
        # Если запись дублируется, возвращаем False
        return False

# Обработчик формы для добавления данных в XML файл
def xml_form(request):
    form = RecipeForm()
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            # Вызываем функцию для создания или обновления XML файла
            added = create_or_update_xml_file(form.cleaned_data)
            if added:
                # Если запись добавлена успешно, возвращаем сообщение об успехе
                return render(request, 'xml_form.html', {'form': form, 'success': True, 'message': "Запись добавлена"})
            else:
                # Если запись дублируется, возвращаем сообщение об ошибке
                return render(request, 'xml_form.html', {'form': form, 'success': False, 'message': "Дублирующая запись"})

    # Если метод не POST, просто отображаем форму
    return render(request, 'xml_form.html', {'form': form})

# Обработчик для отображения данных из XML файла
def display_xml_data(request):
    xml_file_path = 'recipes.xml'
    data = []
    errors = []

    # Проверка существования файла и его размера
    if os.path.exists(xml_file_path) and os.path.getsize(xml_file_path) > 0:
        try:
            # Разбор XML-файла
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            # Проход по элементам и добавление их в список
            for entry in root.findall('entry'):
                field_errors = [] # Для ошибок внутри одной записи

                # Извлечение данных из XML и проверка на наличие всех полей
                name = entry.find('name').text if entry.find('name') is not None else None
                ingredients = entry.find('ingredients').text if entry.find('ingredients') is not None else None
                instructions = entry.find('instructions').text if entry.find('instructions') is not None else None
                cooking_time = entry.find('cooking_time').text if entry.find('cooking_time') is not None else None

                if name is None:
                    field_errors.append("Отсутствует имя.")
                if ingredients is None:
                    field_errors.append("Отсутствуют ингредиенты.")
                if instructions is None:
                    field_errors.append("Отсутствуют инструкции.")
                if cooking_time is None:
                    field_errors.append("Отсутствует время приготовления.")

                if field_errors:
                    # Если есть ошибки в полях, добавляем их в список ошибок
                    errors.append(f"Ошибка в записи с name={name or 'None'}: " + "; ".join(field_errors))
                    errors.append(f"Ошибка в записи с name={ingredients or 'None'}: " + "; ".join(field_errors))
                    errors.append(f"Ошибка в записи с name={instructions or 'None'}: " + "; ".join(field_errors))
                    errors.append(f"Ошибка в записи с name={cooking_time or 'None'}: " + "; ".join(field_errors))

                # Добавляем данные в список для отображения
                data.append({
                    'name': name,
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'cooking_time': cooking_time,
                })

        except ET.ParseError:
            # Если файл поврежден, добавляем ошибку в список ошибок
            errors.append("XML-файл повреждён и не может быть разобран.")
    else:
        # Если файл не найден или пуст, добавляем ошибку в список ошибок
        errors.append("XML-файл не найден или пуст.")

    # Отображаем данные и ошибки на странице
    return render(request, 'display_xml_data.html', {'data': data, 'errors': errors})

# Обработчик для управления XML файлом (загрузка и скачивание)
def manage_xml(request):
    errors = []
    success_message = None
    file_path = "recipes.xml"

    # Обработка запроса на скачивание файла
    # Проверяем, был ли запрос на скачивание файла через GET-запрос
    if request.method == 'GET' and 'download' in request.GET:
        # Проверяем, существует ли файл recipes.xml
        if os.path.exists(file_path):
                # Если файл существует, открываем его для чтения в двоичном режиме
                with open(file_path, 'rb') as xml_file:
                    response = HttpResponse(xml_file.read(), content_type='application/xml')
                    # Устанавливаем заголовок для скачивания файла (Content-Disposition)
                    response['Content-Disposition'] = 'attachment; filename="recipes.xml"'
                   # Возвращаем ответ для скачивания файла
                    return response
        else:
            # Если файл не найден, добавляем ошибку в список ошибок
            errors.append("XML-файл не найден для скачивания.")

    # Обработка запроса на загрузку файла
    if request.method == 'POST' and 'upload' in request.FILES:
        uploaded_file = request.FILES['upload'] # Получаем загруженный файл

        try:
            tree = ET.parse(uploaded_file) # Пробуем разобрать XML файл
            root = tree.getroot()

            if root.tag != 'data':
                # Если корневой элемент не 'data', добавляем ошибку в список ошибок
                errors.append("Неверный формат XML файла. Ожидается корневой элемент <data>.")
            else:
                # Загрузка существующего файла, если он существует
                if os.path.exists(file_path):
                    existing_tree = ET.parse(file_path)
                    existing_root = existing_tree.getroot()
                else:
                    existing_root = ET.Element("data")
                    existing_tree = ET.ElementTree(existing_root)

                keys = ['name', 'ingredients', 'instructions', 'cooking_time']
                records_added = 0

                for entry in root.findall('entry'):
                    new_entry_data = {key: entry.find(key).text if entry.find(key) is not None else None for key in keys}

                    if any(new_entry_data[key] is None for key in keys):
                        # Если есть неполные данные в записи, добавляем ошибку в список ошибок
                        errors.append(f"Неполные данные в записи: {new_entry_data}")
                        continue

                    entry_errors = []

                    if int(new_entry_data['cooking_time']) < 0:
                            entry_errors.append(f"Ошибка: время приготовления не может быть отрицательным.")
                    # Если есть ошибки для текущей записи, добавляем их в общий список ошибок
                    if entry_errors:
                        # Если есть ошибки в записи, добавляем их в список ошибок
                        errors.append(f"Запись с ошибками: {new_entry_data}.{', '.join(entry_errors)}")
                        continue

                    # Проверка на дублирование записи
                    is_duplicate = any(
                        all(existing_entry.find(key).text == new_entry_data[key] for key in keys)
                        for existing_entry in existing_root.findall('entry')
                    )

                    if not is_duplicate:
                        # Если запись не дублируется, добавляем новую запись
                        new_entry = ET.SubElement(existing_root, "entry")
                        for key, value in new_entry_data.items():
                            recipt_min = ET.SubElement(new_entry, key)
                            recipt_min.text = value
                        records_added += 1
                    else:
                        # Если запись дублируется, добавляем ошибку в список ошибок
                        errors.append(f"Дублирующая запись: {new_entry_data}")

                if records_added > 0:
                    # Если добавлены новые записи, сохраняем изменения в файл
                    ET.indent(existing_tree, space="  ", level=0)
                    existing_tree.write(file_path, encoding="utf-8", xml_declaration=True)
                    success_message = f"Добавлено {records_added} новых записей в XML файл."
                else:
                    # Если новые записи не были добавлены, добавляем сообщение об этом
                    success_message = "Новые записи не были добавлены, так как все записи были дубликатами или содержали ошибки."

        except ET.ParseError:
            # Если произошла ошибка парсинга XML файла, добавляем ошибку в список ошибок
            errors.append("Ошибка парсинга XML файла. Файл поврежден или не является корректным XML.")

    # Отображаем ошибки и сообщение об успехе на странице
    return render(request, 'upload_download_xml.html', {'errors': errors, 'success_message': success_message})
