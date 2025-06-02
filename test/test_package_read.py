#!/usr/bin/env python3
"""
Тест для читання пакета ZOK_LAB
"""

import sys
import os

# Додаємо шлях до src для імпорту модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_read_zok_lab_package():
    """Тестує читання пакета ZOK_LAB"""
    print("=" * 80)
    print("ТЕСТ ЧИТАННЯ ПАКЕТА ZOK_LAB")
    print("=" * 80)
    
    try:
        # Імпортуємо функцію для читання пакетів
        from src.tools.package_structure import get_package_structure
        
        package_name = "ZOK_LAB"
        print(f"🔄 Читаємо пакет: {package_name}")
        
        # Викликаємо функцію
        result = get_package_structure(package_name)
        
        print(f"\n✅ УСПІШНО ПРОЧИТАНО ПАКЕТ!")
        print(f"📦 Кількість об'єктів: {len(result)}")
        
        if result:
            print(f"\n📋 Об'єкти в пакеті ZOK_LAB:")
            print("-" * 80)
            
            # Групуємо по типах
            types_dict = {}
            for obj in result:
                obj_type = obj.get('OBJECT_TYPE', 'Unknown')
                if obj_type not in types_dict:
                    types_dict[obj_type] = []
                types_dict[obj_type].append(obj)
            
            # Виводимо по типах
            for obj_type in sorted(types_dict.keys()):
                objects = types_dict[obj_type]
                print(f"\n🔹 {obj_type} ({len(objects)} об'єктів):")
                for obj in objects:
                    name = obj.get('OBJECT_NAME', 'No name')
                    desc = obj.get('OBJECT_DESCRIPTION', 'No description')
                    uri = obj.get('OBJECT_URI', 'No URI')
                    print(f"   • {name} - {desc}")
                    print(f"     URI: {uri}")
            
            print(f"\n📊 Статистика по типах:")
            for obj_type, objects in sorted(types_dict.items()):
                print(f"   {obj_type}: {len(objects)}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Помилка при читанні пакета: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    print("Тест читання пакета ZOK_LAB")
    print("Використовує виправлений package_structure.py")
    print("=" * 80)
    
    # Тест читання пакета
    success, result = test_read_zok_lab_package()
    
    print("\n" + "=" * 80)
    print("ПІДСУМОК")
    print("=" * 80)
    
    if success and result:
        print("🎉 ПАКЕТ ZOK_LAB УСПІШНО ПРОЧИТАНО!")
        print(f"📦 Знайдено {len(result)} об'єктів")
        print("✅ MCP сервер працює правильно")
    else:
        print("❌ Не вдалося прочитати пакет")
    
    print("=" * 80)
