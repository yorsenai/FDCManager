import sqlite3
from os.path import getsize

class FCDMgr:
    def __init__(self) -> None:
        self.cursor = None


    def isConnected(self):
        " Проверяет, подключен ли менеджер к базе данных "
        if self.cursor is None:
            return False
        return True

    def connectDataBase(self, database : str):
        " Подключение менеджера к базе данных "
        try:
            connection = sqlite3.connect(f"file:{database}?mode=rw", uri = True)
        except sqlite3.OperationalError:
            return 1
        if getsize(database) < 100:
            return 2
        self.cursor = connection.cursor()
        return 0

    

    def getTableAttributes(self, table_name):
        " Получает список всех атрибутов таблицы "

        self.cursor.execute(f"PRAGMA table_xinfo({table_name});")
        columns = self.cursor.fetchall()
        attrs = list()

        for column in columns:
            attrs.append(column[1])
        return attrs

    def getAllAttributes(self):
        " Получает список всех атрибутов базы данных "

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        attrs = list()

        for table in tables:
            attrs += self.getTableAttributes(table[0])

        return attrs

    

    def getPrimaryKey(self, table_name):
        " Получает первичный ключ таблицы "
        self.cursor.execute(f"PRAGMA table_xinfo({table_name});")
        columns = self.cursor.fetchall()

        for column in columns:
            if column[5]:
                return column[1]
        return None

    def getPrimaryDependencies(self, tables : list):
        " Получение списка функциональных зависимостей атрибутов от первичного ключа их отношения "
        deps = list()

        for table in tables:
            table_name = table[0]
            # Получение списка столбцов в таблице
            self.cursor.execute(f"PRAGMA table_xinfo({table_name});")
            columns = self.cursor.fetchall()
            
            # Для каждого столбца
            primary_key = self.getPrimaryKey(table_name = table_name)
            if not primary_key:
                continue
            for column in columns:
                attribute = column[1]
                is_primary = column[5]

                if not is_primary:
                    deps.append(f"{primary_key}-->{attribute}")
        return deps

    def getForeignDependencies(self, tables : list):
        " Получение списка функциональных зависимостей атрибутов от внуешнего ключа "
        deps = list()
        for table in tables:
            table_name = table[0]
            # Получение списка столбцов в таблице
            self.cursor.execute(f"PRAGMA table_xinfo({table_name});")
            columns = self.cursor.fetchall()
            
            # Для каждого столбца
            for column in columns:
                attribute = column[1]

                # Проверка, является ли столбец внешним ключом
                self.cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                foreign_keys = self.cursor.fetchall()

                for foreign_key in foreign_keys:
                    if attribute == foreign_key[3]:
                        referenced_table = foreign_key[2]
                        
                        # Определение функциональной зависимости между внешним и первичным ключом
                        referenced_attribute = self.getPrimaryKey(table_name = referenced_table)
                        deps.append(f"{referenced_attribute} --> {attribute}")

        return deps


    def getFunctionalDependencies(self):
        " Построение списка функциональных зависимостей "

        if not self.isConnected():
            #TODO: ALERT GUI 
            print("NOT CONNECTED")
            return

        # Получение списка таблиц в базе данных
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        dependencies_list = list()

        dependencies_list += self.getPrimaryDependencies(tables = tables)
        dependencies_list += self.getForeignDependencies(tables = tables)

        
        return dependencies_list
    
    def getClosure(self, attribute):
        " Построение замыкания для атрибута "
        if not self.isConnected():
            #TODO: ALERT GUI 
            print("NOT CONNECTED")
            return

        closure = list()  
        closure.append(attribute) # Начальное замыкание содержит целевыой атрибут

        deps = self.getFunctionalDependencies()

        while True:
            changed = False
            new_closure = list(set(closure))  # Новое замыкание на основе текущего

            for dependency in deps:
                left_side, right_side = dependency.split("-->")
                if left_side in closure and right_side not in closure:
                    new_closure.append(right_side.split("\n")[0])
                    changed = True

            if not changed:
                break # Если замыкание не изменилось, значит оно построено.

            closure = list(set(new_closure))

        return closure