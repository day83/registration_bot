import psycopg2
from configparser import ConfigParser
from User import User
import logging
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Db:

    def __init__(self):
        self.check_tables()
        self.fetch_users()

    def config(self, filename='database.conf', section='postgresql'):
        parser = ConfigParser()
        parser.read(filename)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in file {1}'.format(section, filename))
        return db

    def connect(self):
        connection = None
        try:
            params = self.config()
            connection = psycopg2.connect(**params)

        except (Exception, psycopg2.DatabaseError) as error:
            raise error

        finally:
            return connection

    def check_tables(self):
        try:
            connection = self.connect()

            with connection.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT PRIMARY KEY NOT NULL,
                        username TEXT,
                        full_name TEXT,
                        quest TEXT,
                        bot_active BOOL,
                        last_visit TEXT
                    )
                ''')
                connection.commit()

        except Exception as error:
            logging.exception(f"Error: db.check_tables()")
            logging.exception(error)

        finally:
            if connection:
                connection.close()

    def fetch_users(self):
        try:
            connection = self.connect()

            cursor = connection.cursor()

            cursor.execute("SELECT id FROM users")

            while row := cursor.fetchone():
                user_id = row[0]
                cursor_jr = connection.cursor()
                cursor_jr.execute(f"SELECT * FROM users WHERE id = {user_id}")
                if row := cursor_jr.fetchone():
                    id, username, full_name, quest, bot_active, last_visit = row
                    user = User(*row)

        except Exception as error:
            logging.exception('Error: fetch_users()')
            logging.exception(error)

        finally:
            if connection:
                connection.close()

    def save(self, obj):
        class_name = type(obj).__name__
        if class_name == 'User':
            user = obj
            user.last_visit = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                connection = self.connect()

                cursor = connection.cursor()

                cursor.execute(f"SELECT * FROM users WHERE id = {user.id}")
                if not cursor.fetchone():
                    cursor.execute(f'''
                            INSERT INTO users (id, username, full_name, quest, bot_active, last_visit)
                            VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (user.id, user.username, user.full_name, user.quest, user.bot_active, user.last_visit))
                else:
                    cursor.execute(f'''
                            UPDATE users SET
                                username = %s,
                                full_name = %s,
                                quest = %s,
                                bot_active = %s,
                                last_visit = %s
                            WHERE id = %s
                    ''', (user.username, user.full_name, user.quest, user.bot_active, user.last_visit, user.id))
                connection.commit()

            except Exception as error:
                logging.exception(f"Error: db.save({user.id})")
                logging.exception(error)

            finally:
                if connection:
                    connection.close()

    def check_in(self, user):
        user.last_visit = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(f"UPDATE users SET last_visit = %s WHERE id = %s", (user.last_visit, user.id))
            connection.commit()

        except Exception as e:
            logging.exception(f"db.check_in({user.id})")
            logging.exception(e)

        finally:
            if connection:
                connection.close()

    def stop_activity(self, user):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(f"UPDATE users SET bot_active = FALSE WHERE id = %s", (user.id,))
            connection.commit()

        except Exception as error:
            logging.exception(f"db.stop_activity({user.id})")
            logging.exception(error)

        finally:
            if connection:
                connection.close()

if __name__ == '__main__':
    # Select users from within this script
    db = Db()
    for user in User.objects:
        print(User.objects.get(user))
        print('--')
