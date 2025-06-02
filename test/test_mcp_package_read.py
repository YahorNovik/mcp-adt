#!/usr/bin/env python3
"""
Тест MCP сервера для читання пакета через Cline
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_package_read():
    """Тестує MCP сервер для читання пакета"""
    print("=" * 80)
    print("ТЕСТ MCP СЕРВЕРА ДЛЯ ЧИТАННЯ ПАКЕТА")
    print("=" * 80)
    
    try:
        # Параметри для підключення до MCP сервера
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            env=None
        )
        
        print("🔄 Підключаємося до MCP сервера...")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Підключено до MCP сервера")
                
                # Отримуємо список доступних інструментів
                print("\n🔧 Отримуємо список інструментів...")
                tools = await session.list_tools()
                
                print(f"📋 Знайдено {len(tools.tools)} інструментів:")
                for tool in tools.tools:
                    print(f"   • {tool.name}: {tool.description}")
                
                # Шукаємо інструмент get_package_structure
                package_tool = None
                for tool in tools.tools:
                    if tool.name == "get_package_structure":
                        package_tool = tool
                        break
                
                if not package_tool:
                    print("❌ Інструмент get_package_structure не знайдено!")
                    return False
                
                print(f"\n✅ Знайдено інструмент: {package_tool.name}")
                print(f"📝 Опис: {package_tool.description}")
                
                # Викликаємо інструмент для читання пакета ZOK_LAB
                print(f"\n🔄 Читаємо пакет ZOK_LAB через MCP...")
                
                result = await session.call_tool(
                    "get_package_structure",
                    arguments={"package_name": "ZOK_LAB"}
                )
                
                print(f"📊 Результат MCP виклику:")
                print(f"   Тип: {type(result)}")
                
                if hasattr(result, 'content') and result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        # Парсимо JSON відповідь
                        try:
                            data = json.loads(content.text)
                            if isinstance(data, list):
                                print(f"✅ УСПІШНО ПРОЧИТАНО ПАКЕТ ЧЕРЕЗ MCP!")
                                print(f"📦 Кількість об'єктів: {len(data)}")
                                
                                # Групуємо по типах
                                types_count = {}
                                for obj in data:
                                    obj_type = obj.get('OBJECT_TYPE', 'Unknown')
                                    types_count[obj_type] = types_count.get(obj_type, 0) + 1
                                
                                print(f"\n📊 Статистика по типах:")
                                for obj_type, count in sorted(types_count.items()):
                                    print(f"   {obj_type}: {count}")
                                
                                print(f"\n📋 Перші 5 об'єктів:")
                                for i, obj in enumerate(data[:5]):
                                    name = obj.get('OBJECT_NAME', 'No name')
                                    obj_type = obj.get('OBJECT_TYPE', 'Unknown')
                                    desc = obj.get('OBJECT_DESCRIPTION', 'No description')
                                    print(f"   {i+1}. {obj_type}: {name} - {desc}")
                                
                                return True
                            else:
                                print(f"❌ Неочікуваний формат даних: {type(data)}")
                                print(f"📄 Дані: {data}")
                                return False
                        except json.JSONDecodeError as e:
                            print(f"❌ Помилка парсингу JSON: {e}")
                            print(f"📄 Текст відповіді: {content.text}")
                            return False
                    else:
                        print(f"❌ Немає тексту в відповіді")
                        print(f"📄 Content: {content}")
                        return False
                else:
                    print(f"❌ Немає контенту в результаті")
                    print(f"📄 Result: {result}")
                    return False
                
    except Exception as e:
        print(f"❌ Помилка при тестуванні MCP: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("Тест MCP сервера для читання пакета ZOK_LAB")
    print("Перевіряє, чи працює виправлений package_structure.py через MCP")
    print("=" * 80)
    
    success = await test_mcp_package_read()
    
    print("\n" + "=" * 80)
    print("ПІДСУМОК MCP ТЕСТУ")
    print("=" * 80)
    
    if success:
        print("🎉 MCP СЕРВЕР ПРАЦЮЄ З ВИПРАВЛЕНИМ КОДОМ!")
        print("✅ Cline тепер може читати пакети через MCP")
        print("✅ Проблему з cookies вирішено в MCP контексті")
    else:
        print("❌ MCP сервер не працює правильно")
        print("💡 Можливо потрібно перезапустити MCP сервер")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
