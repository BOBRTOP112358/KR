import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import openpyxl
import datetime

# Введите ваш токен бота сюда
TOKEN = '7400358552:AAHV7_6vC_OnUEikSZ_xQrXZhMVwEEy9YG4'

# Этапы диалога
CHOOSING_ACTION, ADD_RECIPE_NAME, ADD_RECIPE_INGREDIENTS, ADD_RECIPE_INSTRUCTION, FIND_RECIPE_INGREDIENTS = range(5)

# Имя файла Excel
EXCEL_FILE = 'recipes.xlsx'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Максимальное число рецептов в день на пользователя (по умолчанию)
DEFAULT_MAX_RECIPES_PER_DAY = 1

# Временное хранилище счетчиков по пользователям (user_id + date)
user_recipe_counts = {}

# Список VIP пользователей по ID
VIP_USERS = {6382538882}  # Замените на ваш Telegram user_id или добавьте свои

def init_excel():
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        sheet = wb.active
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(['Название', 'Ингредиенты', 'Инструкция'])
        wb.save(EXCEL_FILE)

def save_recipe(name, ingredients, instruction):
    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb.active
    sheet.append([name, ingredients, instruction])
    wb.save(EXCEL_FILE)

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
        await update.message.reply_text('Введите продукты у вас есть через запятую:', reply_markup=get_cancel_keyboard())
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
    await update.message.reply_text('Введите ингредиенты через запятую:', reply_markup=get_cancel_keyboard())
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

    await update.message.reply_text('Рецепт сохранен!', reply_markup=ReplyKeyboardRemove())

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

# Команда для изменения лимита (только для админа или вас)
async def set_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
   user_id = update.effective_user.id

   # Проверьте права доступа (например только вы или определённый пользователь)
   # Для простоты разрешим только вам (замените на свой ID или список админов)
   ADMIN_IDs = {6382538882}  # замените на ваш ID или список ID админов

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
       },
       fallbacks=[]
   )

   application.add_handler(conv_handler)

   # Добавляем команду /set_limit для изменения лимита
   application.add_handler(CommandHandler('set_limit', set_limit))

   application.run_polling()

if __name__ == '__main__':
   main()
