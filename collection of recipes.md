import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import openpyxl
import datetime
import re

# Введите ваш токен бота сюда
TOKEN = 'токен'

# Этапы диалога
CHOOSING_ACTION, ADD_RECIPE_NAME, ADD_RECIPE_INGREDIENTS, ADD_RECIPE_INSTRUCTION, FIND_RECIPE_INGREDIENTS = range(5)
ADD_PRODUCT_NAME, ADD_PRODUCT_CATEGORY = range(5, 7)

# Имя файла Excel
EXCEL_FILE = 'recipes.xlsx'
PRODUCTS_FILE = 'products.xlsx'  # файл для хранения продуктов

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Максимальное число рецептов в день на пользователя (по умолчанию)
DEFAULT_MAX_RECIPES_PER_DAY = 1

# Временное хранилище счетчиков по пользователям (user_id + date)
user_recipe_counts = {}

# Список VIP пользователей по ID
VIP_USERS = {тг айди}  # Замените на ваш Telegram user_id или добавьте свои


def init_excel():
    # Инициализация файла рецептов
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        sheet = wb.active
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(['Название', 'Ингредиенты', 'Инструкция'])
        wb.save(EXCEL_FILE)

    # Инициализация файла продуктов
    try:
        wb_products = openpyxl.load_workbook(PRODUCTS_FILE)
        sheet_products = wb_products.active
    except FileNotFoundError:
        wb_products = openpyxl.Workbook()
        sheet_products = wb_products.active
        sheet_products.append(['Продукт', 'Категория'])
        wb_products.save(PRODUCTS_FILE)


def save_recipe(name, ingredients, instruction):
    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb.active
    sheet.append([name, ingredients, instruction])
    wb.save(EXCEL_FILE)


def add_product(product_name, category):
    wb_products = openpyxl.load_workbook(PRODUCTS_FILE)
    sheet_products = wb_products.active
    sheet_products.append([product_name, category])
    wb_products.save(PRODUCTS_FILE)


def get_main_keyboard():
    reply_keyboard = [['Добавить рецепт', 'Найти рецепт'], ['Отмена']]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)


def get_cancel_keyboard():
    reply_keyboard = [['Отмена']]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_keyboard()
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    return CHOOSING_ACTION


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == 'Добавить рецепт':
        await update.message.reply_text('Введите название рецепта:', reply_markup=get_cancel_keyboard())
        return ADD_RECIPE_NAME
    elif text == 'Найти рецепт':
        await update.message.reply_text('Введите продукты у вас есть через запятую:',
                                        reply_markup=get_cancel_keyboard())
        return FIND_RECIPE_INGREDIENTS
    elif text == 'Отмена':
        await update.message.reply_text('Действие отменено.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)
    else:
        await update.message.reply_text('Пожалуйста выберите действие из меню.', reply_markup=get_main_keyboard())
        return CHOOSING_ACTION


async def add_recipe_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Отмена':
        await update.message.reply_text('Добавление рецепта отменено.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)
    context.user_data['recipe_name'] = update.message.text.strip()
    await update.message.reply_text('Введите ингредиенты через запятую и после # его группу:', reply_markup=get_cancel_keyboard())
    return ADD_RECIPE_INGREDIENTS


async def add_recipe_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Отмена':
        await update.message.reply_text('Добавление рецепта отменено.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)
    ingredients = update.message.text.strip()
    context.user_data['ingredients'] = ingredients
    await update.message.reply_text('Введите инструкцию по приготовлению:', reply_markup=get_cancel_keyboard())
    return ADD_RECIPE_INSTRUCTION


async def add_recipe_instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Отмена':
        await update.message.reply_text('Добавление рецепта отменено.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)

    user_id = update.effective_user.id
    today_str = datetime.date.today().isoformat()
    user_day_key = f"{user_id}_{today_str}"

    # Проверка VIP статус
    is_vip = user_id in VIP_USERS

    # Получение лимита для пользователя (если не VIP)
    max_recipes_per_day = DEFAULT_MAX_RECIPES_PER_DAY if not is_vip else float('inf')

    count_today = user_recipe_counts.get(user_day_key, 0)

    if not is_vip and count_today >= max_recipes_per_day:
        await update.message.reply_text(
            f"Вы достигли лимита {max_recipes_per_day} рецептов за сегодня.",
            reply_markup=ReplyKeyboardRemove()
        )
        return await start(update, context)

    name = context.user_data['recipe_name']
    ingredients = context.user_data['ingredients']
    instruction = update.message.text.strip()

    save_recipe(name, ingredients, instruction)

    user_recipe_counts[user_day_key] = count_today + 1

    # После сохранения рецепта предлагаем добавить продукт с категорией через хештеги?
    # Или отдельная команда? Для этого добавим команду /addproduct

    # Возвращаемся к старту или меню.


    return await start(update, context)


# --- Новая команда /addproduct ---
async def add_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название продукта и категорию через пробел или хештег:\nНапример:\nМолоко #напитки",
        reply_markup=get_cancel_keyboard()
    )
    return ADD_PRODUCT_NAME


async def add_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Отмена':
        await update.message.reply_text('Добавление продукта отменено.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)

    text = update.message.text.strip()
    # Разделяем название и категорию по пробелу или ищем хештеги внутри текста.
    match_hashtag = re.search(r'#(\w+)', text)

    if match_hashtag:
        category = match_hashtag.group(1)
        product_name = text[:match_hashtag.start()].strip()
    else:
        product_name_parts = text.split()
        product_name = " ".join(product_name_parts[:-1]) if len(product_name_parts) > 1 else text
        category_match_list = re.findall(r'#(\w+)', text)
        category = category_match_list[0] if category_match_list else "Общее"

    add_product(product_name.strip(), category.strip())

    await update.message.reply_text(f"Продукт '{product_name}' добавлен в категорию '{category}'.",
                                    reply_markup=ReplyKeyboardRemove())

    return await start(update, context)

async def find_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Отмена':
        await update.message.reply_text('Поиск рецептов отменен.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)

    user_ingredients = [ing.strip().lower() for ing in update.message.text.split(',')]

    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb.active

    matching_recipes = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        recipe_name, ingredients_str, instruction = row
        recipe_ings = [ing.strip().lower() for ing in ingredients_str.split(',')]

        # Проверка если все введенные пользователем ингредиенты есть в рецепте
        if all(ing in recipe_ings for ing in user_ingredients):
            matching_recipes.append((recipe_name, ingredients_str, instruction))

    if matching_recipes:
        response = 'Найденные рецепты:\n'
        for name, ings, instr in matching_recipes:
            response += f"\n*{name}*\nИнгредиенты: {ings}\nИнструкция: {instr}\n"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('Рецепты не найдены.')

   # После поиска возвращаемся к старту или завершаем диалог
    return await start(update, context)

async def set_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
   user_id = update.effective_user.id

   # Проверьте права доступа (например только вы или определённый пользователь)
   # Для простоты разрешим только вам (замените на свой ID или список админов)
   ADMIN_IDs = {тг айди}  # замените на ваш ID или список ID админов

   if user_id not in ADMIN_IDs:
       await update.message.reply_text("У вас нет прав для выполнения этой команды.")
       return

   # Проверка аргумента лимита
   if len(context.args) != 1 or not context.args[0].isdigit():
       await update.message.reply_text("Использование: /set_limit <число>")
       return

   new_limit = int(context.args[0])
   global DEFAULT_MAX_RECIPES_PER_DAY
   DEFAULT_MAX_RECIPES_PER_DAY = new_limit

   await update.message.reply_text(f"Лимит рецептов в день установлен на {new_limit}.")

# --- Команда /products_by_category ---
async def products_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Использование: /products_by_category <категория>")
        return

    category_query = " ".join(context.args).strip().lower()

    wb_products = openpyxl.load_workbook(PRODUCTS_FILE)
    sheet_products = wb_products.active

    products_in_category = []
    for row in sheet_products.iter_rows(min_row=2, values_only=True):
        product_name, category = row
        if category and category.lower() == category_query:
            products_in_category.append(product_name)

    if products_in_category:
        response = "Продукты в категории '{}':\n".format(category_query.capitalize())
        response += "\n".join(products_in_category)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(f'Нет продуктов в категории "{category_query}".')


# --- Обновляем main() ---
def main():
    init_excel()

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                             handle_action)],
            ADD_RECIPE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.Regex('^Отмена$'),
                                             add_recipe_name)],
            ADD_RECIPE_INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.Regex('^Отмена$'),
                                                    add_recipe_ingredients)],
            ADD_RECIPE_INSTRUCTION: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.Regex('^Отмена$'),
                                                    add_recipe_instruction)],
            FIND_RECIPE_INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.Regex('^Отмена$'),
                                                    find_recipes)],
            # Добавляем обработчик для команды /addproduct и /products_by_category
            # через отдельные handlers вне конверсации или как команды.
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('set_limit', set_limit))

    # Новые команды вне конверсации:
    application.add_handler(CommandHandler('addproduct', add_product_command))
    application.add_handler(CommandHandler('products_by_category', products_by_category))

    application.run_polling()


if __name__ == '__main__':
    main()
