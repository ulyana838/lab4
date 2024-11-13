from django.shortcuts import render, redirect  # Импортируем функции для рендеринга шаблонов и перенаправления запросов
from django.http import HttpResponse  # Импортируем класс для создания HTTP-ответов
from .forms import RecipeForm  # Импортируем форму для рецептов
from .models import RecipeModel  # Импортируем модель для рецептов
import os  # Импортируем модуль для работы с операционной системой
import xml.etree.ElementTree as ET  # Импортируем модуль для работы с XML
from django.db import connection  # Импортируем модуль для работы с базой данных
from django.shortcuts import get_object_or_404  # Импортируем функцию для получения объекта или возврата 404 ошибки
from django.http import JsonResponse  # Импортируем класс для создания JSON-ответов

# Функция для создания или обновления XML файла
def create_or_update_xml_file(data):
    file_path = "xml_files/recipes.xml"  # Путь к XML файлу

    # Проверка существования файла и его размера
    if os.path.exists(file_path):
        if os.path.getsize(file_path) == 0:
            # Если файл пустой, создаем новый корневой элемент
            root = ET.Element("data")
            tree = ET.ElementTree(root)
        else:
            # Если файл существует и не пустой, разбираем его
            tree = ET.parse(file_path)
            root = tree.getroot()  # Получение корневого элемента
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

def dublicates_in_db(cleaned_data, exclude_id=None):
    # Создаем запрос для поиска записей в базе данных, которые совпадают с данными из cleaned_data
    query = RecipeModel.objects.filter(
        name=cleaned_data['name'],  # Фильтруем по полю 'name'
        ingredients=cleaned_data['ingredients'],  # Фильтруем по полю 'ingredients'
        instructions=cleaned_data['instructions'],  # Фильтруем по полю 'instructions'
        cooking_time=cleaned_data['cooking_time'],  # Фильтруем по полю 'cooking_time'
    )

    # Если передан параметр exclude_id, исключаем запись с этим ID из результатов запроса
    if exclude_id is not None:
        query = query.exclude(id=exclude_id)

    # Возвращаем True, если существует хотя бы одна запись, удовлетворяющая условиям запроса, иначе False
    return query.exists()


# Обработчик формы для добавления данных в XML файл
def xml_form(request):
    form = RecipeForm()  # Создаем экземпляр формы
    if request.method == 'POST':
        form = RecipeForm(request.POST)  # Заполняем форму данными из POST-запроса
        if form.is_valid():  # Проверяем, прошли ли данные формы все установленные правила валидации
            cleaned_data = form.cleaned_data  # Получаем очищенные данные из формы

            if request.POST.get('save_to') == 'database':
                if dublicates_in_db(cleaned_data):
                    return render(request, 'xml_form.html', {'form': form, 'success': False, 'message': "Дублирующая запись"})
                else:
                    form.save()  # Сохраняем данные в базу данных
                    return render(request, 'xml_form.html', {'form': form, 'success': True, 'message': "Запись добавлена"})

            elif request.POST.get('save_to') == 'file':
                # Преобразуем данные в формат XML и дополняем существующий файл
                added = create_or_update_xml_file(form.cleaned_data)
                if added:
                    return render(request, 'xml_form.html', {'form': form, 'success': True, 'message': "Запись добавлена"})
                else:
                    return render(request, 'xml_form.html', {'form': form, 'success': False, 'message': "Дублирующая запись"})

    # Если метод не POST, просто отображаем форму
    return render(request, 'xml_form.html', {'form': form})

# Обработчик для отображения данных из XML файла
def display_xml_data(request):
    xml_file_path = 'xml_files/recipes.xml'  # Путь к XML файлу
    data = []  # Список для хранения данных из XML файла
    errors = []  # Список для хранения ошибок

    # Проверка существования файла и его размера
    if os.path.exists(xml_file_path) and os.path.getsize(xml_file_path) > 0:
        try:
            # Разбор XML-файла
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            # Проход по элементам и добавление их в список
            for entry in root.findall('entry'):
                field_errors = []  # Для ошибок внутри одной записи

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
    errors = []  # Список для хранения ошибок
    success_message = None  # Сообщение об успешном выполнении операции
    file_path = "xml_files/recipes.xml"  # Путь к XML файлу

    # Обработка запроса на скачивание файла
    # Проверяем, был ли запрос на скачивание файла через GET-запрос
    if request.method == 'GET' and 'download' in request.GET:
        # Проверяем, существует ли файл recipes.xml
        if os.path.exists(file_path):
            # Если файл существует, открываем его для чтения в двоичном режиме
            with open(file_path, 'rb') as xml_file:
                response = HttpResponse(xml_file.read(), content_type='application/xml')  # Создаем HTTP-ответ с содержимым файла
                # Устанавливаем заголовок для скачивания файла (Content-Disposition)
                response['Content-Disposition'] = 'attachment; filename="xml_files/recipes.xml"'
                # Возвращаем ответ для скачивания файла
                return response
        else:
            # Если файл не найден, добавляем ошибку в список ошибок
            errors.append("XML-файл не найден для скачивания.")

    # Обработка запроса на загрузку файла
    if request.method == 'POST' and 'upload' in request.FILES:
        uploaded_file = request.FILES['upload']  # Получаем загруженный файл

        try:
            tree = ET.parse(uploaded_file)  # Пробуем разобрать XML файл
            root = tree.getroot()  # Получаем корневой элемент XML файла

            if root.tag != 'data':
                # Если корневой элемент не 'data', добавляем ошибку в список ошибок
                errors.append("Неверный формат XML файла. Ожидается корневой элемент <data>.")
            else:
                # Загрузка существующего файла, если он существует
                if os.path.exists(file_path):
                    existing_tree = ET.parse(file_path)  # Разбираем существующий XML файл
                    existing_root = existing_tree.getroot()  # Получаем корневой элемент существующего XML файла
                else:
                    existing_root = ET.Element("data")  # Создаем новый корневой элемент
                    existing_tree = ET.ElementTree(existing_root)  # Создаем новое дерево XML

                keys = ['name', 'ingredients', 'instructions', 'cooking_time']  # Ключи для проверки данных
                records_added = 0  # Счетчик добавленных записей

                for entry in root.findall('entry'):  # Проходим по всем элементам 'entry' в загруженном файле
                    new_entry_data = {key: entry.find(key).text if entry.find(key) is not None else None for key in keys}  # Извлекаем данные из элемента 'entry'

                    if any(new_entry_data[key] is None for key in keys):
                        # Если есть неполные данные в записи, добавляем ошибку в список ошибок
                        errors.append(f"Неполные данные в записи: {new_entry_data}")
                        continue

                    entry_errors = []  # Список для хранения ошибок текущей записи

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
                        new_entry = ET.SubElement(existing_root, "entry")  # Создаем новый элемент 'entry'
                        for key, value in new_entry_data.items():
                            recipt_min = ET.SubElement(new_entry, key)  # Создаем дочерний элемент для каждого ключа
                            recipt_min.text = value  # Устанавливаем текст дочернего элемента
                        records_added += 1  # Увеличиваем счетчик добавленных записей
                    else:
                        # Если запись дублируется, добавляем ошибку в список ошибок
                        errors.append(f"Дублирующая запись: {new_entry_data}")

                if records_added > 0:
                    # Если добавлены новые записи, сохраняем изменения в файл
                    ET.indent(existing_tree, space="  ", level=0)  # Форматируем XML
                    existing_tree.write(file_path, encoding="utf-8", xml_declaration=True)  # Сохраняем XML файл
                    success_message = f"Добавлено {records_added} новых записей в XML файл."  # Устанавливаем сообщение об успехе
                else:
                    # Если новые записи не были добавлены, добавляем сообщение об этом
                    success_message = "Новые записи не были добавлены, так как все записи были дубликатами или содержали ошибки."

        except ET.ParseError:
            # Если произошла ошибка парсинга XML файла, добавляем ошибку в список ошибок
            errors.append("Ошибка парсинга XML файла. Файл поврежден или не является корректным XML.")

    # Отображаем ошибки и сообщение об успехе на странице
    return render(request, 'upload_download_xml.html', {'errors': errors, 'success_message': success_message})

def display_db_data(request):
    entries = RecipeModel.objects.all()  # Получаем все записи из базы данных
    return render(request, 'display_db_data.html', {'entries': entries})  # Отображаем данные на странице

#удаление записи из бд
def delete_entry(request, id):
    entry = get_object_or_404(RecipeModel, id=id)  # Получаем запись по ID или возвращаем 404 ошибку
    if request.method == 'POST':
        entry.delete()  # Удаляем запись
        return redirect('display_db_data')  # Перенаправляем на страницу отображения данных
    return render(request, 'delete_entry.html', {'entry': entry})  # Отображаем страницу подтверждения удаления

# редактирование записи из бд
def edit_entry(request, id):
    # Получаем запись по ID или возвращаем 404 ошибку, если запись не найдена
    entry = get_object_or_404(RecipeModel, id=id)

    # Проверяем, является ли запрос POST-запросом
    if request.method == 'POST':
        # Заполняем форму данными из POST-запроса и существующей записи
        form = RecipeForm(request.POST, instance=entry)

        # Проверяем, прошли ли данные формы все установленные правила валидации
        if form.is_valid():
            # Проверяем, существует ли дублирующая запись в базе данных, исключая текущую запись
            if dublicates_in_db(form.cleaned_data, exclude_id=entry.id):
                # Если дублирующая запись существует, отображаем форму с сообщением об ошибке
                return render(request, 'edit_entry.html', {'form': form, 'entry': entry, 'success': False, 'message': "Дублирующая запись"})
            else:
                # Если дублирующая запись не существует, сохраняем изменения в базу данных
                form.save()
                # Перенаправляем на страницу отображения данных
                return redirect('display_db_data')
        else:
            # Если данные формы не прошли валидацию, создаем форму с данными существующей записи
            form = RecipeForm(instance=entry)
    else:
        # Если запрос не является POST-запросом, создаем форму с данными существующей записи
        form = RecipeForm(instance=entry)

    # Отображаем страницу редактирования записи с формой и текущей записью
    return render(request, 'edit_entry.html', {'form': form, 'entry': entry})

def search_entries(request):
    # Получаем параметр запроса 'query' из GET-запроса, если он отсутствует, используем пустую строку
    query = request.GET.get('query', '')

    # Фильтруем записи в базе данных, которые содержат параметр запроса в любом из полей:
    # 'name', 'ingredients', 'instructions', 'cooking_time'
    results = RecipeModel.objects.filter(
        name__icontains=query
    ) | RecipeModel.objects.filter(
        ingredients__icontains=query
    ) | RecipeModel.objects.filter(
        instructions__icontains=query
    ) | RecipeModel.objects.filter(
        cooking_time__icontains=query
    )

    # Преобразуем результаты фильтрации в список словарей, где каждый словарь содержит данные одной записи
    entries = [{
        'id': entry.id,  # ID записи
        'name': entry.name,  # Название рецепта
        'ingredients': entry.ingredients,  # Ингредиенты рецепта
        'instructions': entry.instructions,  # Инструкции по приготовлению
        'cooking_time': entry.cooking_time,  # Время приготовления
    } for entry in results]

    # Возвращаем JSON-ответ, содержащий список записей
    return JsonResponse({'entries': entries})
