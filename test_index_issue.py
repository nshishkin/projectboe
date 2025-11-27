"""
Демонстрация проблемы с индексом при удалении юнита.
"""

# Симуляция turn_order
turn_order = ["Unit1", "Unit2", "Unit3", "Unit4", "Unit5"]
current_unit_index = 2  # Ход Unit3 (index 2)

print("До удаления:")
print(f"  turn_order = {turn_order}")
print(f"  current_unit_index = {current_unit_index}")
print(f"  Current unit: {turn_order[current_unit_index]}")

# Unit3 убивает Unit2 (index 1) - юнит ДО текущего
print("\nUnit3 убивает Unit2 (юнит ПЕРЕД текущим):")
turn_order_new = [u for u in turn_order if u != "Unit2"]
print(f"  turn_order = {turn_order_new}")
print(f"  current_unit_index = {current_unit_index} (НЕ ИЗМЕНИЛСЯ!)")
print(f"  Current unit: {turn_order_new[current_unit_index]} (БЫЛО Unit3, СТАЛО Unit4 - ОШИБКА!)")
print(f"  Должен быть: Unit3, индекс должен стать {current_unit_index - 1}")

print("\n" + "="*60)

# Сброс
turn_order = ["Unit1", "Unit2", "Unit3", "Unit4", "Unit5"]
current_unit_index = 2

# Unit3 убивает Unit4 (index 3) - юнит ПОСЛЕ текущего
print("\nUnit3 убивает Unit4 (юнит ПОСЛЕ текущего):")
turn_order_new = [u for u in turn_order if u != "Unit4"]
print(f"  turn_order = {turn_order_new}")
print(f"  current_unit_index = {current_unit_index} (НЕ ИЗМЕНИЛСЯ)")
print(f"  Current unit: {turn_order_new[current_unit_index]} (Unit3 - ПРАВИЛЬНО!)")
print(f"  Это ОК, потому что юнит ПОСЛЕ текущего")
