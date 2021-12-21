import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('UJ_db.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS levels
                  (id INT PRIMARY KEY, UserName TEXT, messages INT, lvl INT)''')
        self.connection.commit()

        self.checker = False
        self.cursor.execute("SELECT UserName FROM levels")
        self.all_results = self.cursor.fetchall()
        self.max_id = 0

    def fill(self, members):    # Fill / check the table
        for i in range(len(members)):
            for j in self.all_results:
                if str(members[i]) == str(j[0]):
                    self.checker = True
                    break
            if self.checker:
                self.checker = False
                continue
            self.cursor.execute(f"""INSERT OR IGNORE INTO levels(id, UserName, messages, lvl)
               VALUES('{self.max_id+i}', '{members[i]}', '0', '1');""")
            self.connection.commit()
            self.max_id += i
        self.result()


    def result(self):   # output the table
        pass
        # self.cursor.execute("SELECT * FROM levels")
        # self.all_results = self.cursor.fetchall()
        # for i in self.all_results:
        #     print(i)


    def new_message(self, user:str) -> int: # earn points and increase the level00
        self.cursor.execute(f"UPDATE levels SET messages = messages +1 WHERE UserName='{user}'")
        self.connection.commit()
        self.cursor.execute(f"SELECT messages FROM levels WHERE UserName='{user}'")
        check_messages = self.cursor.fetchall()[0][0]
        if check_messages%20==0:
            self.cursor.execute(f"UPDATE levels SET lvl = lvl +1 WHERE UserName='{user}'")
            self.connection.commit()
            self.cursor.execute(f"SELECT lvl FROM levels WHERE UserName='{user}'")
            lvl_up = self.cursor.fetchall()
            return lvl_up[0][0]
        self.result()
        return 0


    def connect(self, user:str) -> bool:    # User Connect / Return
        self.cursor.execute(f"SELECT UserName FROM levels WHERE UserName='{user}'")
        new_user = self.cursor.fetchall()
        if len(new_user) < 1:
            self.max_id+=1
            self.cursor.execute(f"""INSERT INTO levels(id, UserName, messages, lvl)
               VALUES('{self.max_id}', '{user}', '0', '1');""")
            self.connection.commit()
            return True
            self.result()
        return False
        self.result()


    def lvl_list(self): # lvl_list
        self.cursor.execute("SELECT UserName FROM levels")
        self.all_users = self.cursor.fetchall()
        self.cursor.execute("SELECT lvl FROM levels")
        self.all_lvls = self.cursor.fetchall()
        return (self.all_users, self.all_lvls)
