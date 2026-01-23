from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.main_menu import get_main_menu
from services.prometheus import prometheus
from services.formatter import (
    format_service_status,
    format_stats,
    format_alerts,
    format_health
)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветствие и главное меню"""
    await message.answer(
        "🚀 <b>StellarTracker Observer Bot</b>\n\n"
        "Я помогу тебе мониторить систему StellarTracker.\n"
        "Выбери команду из меню ниже 👇",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )


@router.message(F.text == "ℹ️ Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка по командам"""
    await message.answer(
        "📖 <b>Справка по командам:</b>\n\n"
        "📊 <b>Статус</b> - Быстрая проверка состояния сервисов (UP/DOWN)\n\n"
        "📈 <b>Статистика</b> - Статистика за последние 24 часа:\n"
        "  • Количество запросов\n"
        "  • Успешные/Неудачные\n"
        "  • Обработанные объекты\n\n"
        "🚨 <b>Алерты</b> - Список активных алертов\n\n"
        "💚 <b>Здоровье</b> - Детальная информация:\n"
        "  • CPU, Memory, Disk usage\n"
        "  • Network I/O\n"
        "  • Request rate\n",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )


@router.message(F.text == "📊 Статус")
@router.message(Command("status"))
async def cmd_status(message: Message):
    """Статус сервисов"""
    loading_msg = await message.answer("⏳ Проверяю статус сервисов...")
    
    services = await prometheus.get_service_status()
    response = format_service_status(services)
    
    await loading_msg.delete()
    await message.answer(response, parse_mode="HTML", reply_markup=get_main_menu())


@router.message(F.text == "📈 Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика"""
    loading_msg = await message.answer("⏳ Собираю статистику за последние 24ч...")
    
    stats = await prometheus.get_stats_24h()
    response = format_stats(stats)
    
    await loading_msg.delete()
    await message.answer(response, parse_mode="HTML", reply_markup=get_main_menu())


@router.message(F.text == "🚨 Алерты")
@router.message(Command("alerts"))
async def cmd_alerts(message: Message):
    """Активные алерты"""
    loading_msg = await message.answer("⏳ Проверяю активные алерты...")
    
    alerts = await prometheus.get_active_alerts()
    response = format_alerts(alerts)
    
    await loading_msg.delete()
    await message.answer(response, parse_mode="HTML", reply_markup=get_main_menu())


@router.message(F.text == "💚 Здоровье")
@router.message(Command("health"))
async def cmd_health(message: Message):
    """Здоровье системы"""
    loading_msg = await message.answer("⏳ Проверяю здоровье системы...")
    
    health = await prometheus.get_system_health()
    response = format_health(health)
    
    await loading_msg.delete()
    await message.answer(response, parse_mode="HTML", reply_markup=get_main_menu())
