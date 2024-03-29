import unittest
import os
import utils.database_connections as dbc


PG_HOST = 'PG_HOST'
PG_PORT = 'PG_PORT'
PG_USER = 'PG_USER'
PG_PASS = 'PG_PASS'
PG_DB = 'PG_DB'

REDIS_HOST = 'REDIS_HOST'
REDIS_PORT = 'REDIS_PORT'
REDIS_DB = 'REDIS_DB'

CLIENTS_WITH_CARTS = 2


class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = None

    def query_1(self):
        count = self.con.query_1()
        self.assertEqual(count, CLIENTS_WITH_CARTS)

    def query_2(self):
        count = self.con.query_2(1)
        self.assertEqual(count, 2)
        count = self.con.query_2(2)
        self.assertEqual(count, 3)
        count = self.con.query_2(3)
        self.assertEqual(count, 0)
        count = self.con.query_2(4)
        self.assertEqual(count, 0)

    def query_3(self):
        count = self.con.query_3(1)
        self.assertEqual(count, 2)
        count = self.con.query_3(2)
        self.assertEqual(count, 1)
        count = self.con.query_3(3)
        self.assertEqual(count, 0)
        count = self.con.query_3(4)
        self.assertEqual(count, 0)

    def query_4(self):
        count = self.con.query_4()
        self.assertEqual(count, 2)

    def query_5(self):
        self.assertTrue(self.con.query_5(1, 1))
        self.assertTrue(self.con.query_5(1, 2))
        self.assertFalse(self.con.query_5(1, 3))
        self.assertFalse(self.con.query_5(1, 4))

        self.assertFalse(self.con.query_5(2, 1))
        self.assertTrue(self.con.query_5(2, 2))

        self.assertFalse(self.con.query_5(4, 4))


class PostgresQueriesTest(DatabaseTest):
    @classmethod
    def setUpClass(cls):
        cls.con = dbc.PostgresConnection(cls._get_config())

        cur = cls.con.con.cursor()
        cur.execute("""
            DROP TABLE IF EXISTS carts CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """)
        cls.con.con.commit()

        cur.execute("""
            DROP TABLE IF EXISTS carts;
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS products;
            
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY,
                full_name TEXT NOT NULL
            );
            
            create sequence users_id_seq;
            
            alter table users alter column id set default nextval('public.users_id_seq');
            
            alter sequence users_id_seq owned by users.id;
            
            CREATE TABLE IF NOT EXISTS products (
                id INT PRIMARY KEY,
                title text NOT NULL,
                description text NOT NULL,
                price INT NOT NULL
            );
            
            create sequence products_id_seq;
            
            alter table products alter column id set default nextval('public.products_id_seq');
            
            alter sequence products_id_seq owned by products.id;
            
            CREATE TABLE IF NOT EXISTS carts (
                product_id INT,
                user_id INT,
                quantity INT NOT NULL,
                UNIQUE(user_id, product_id),
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                PRIMARY KEY (product_id, user_id)
            );
        """)

        cls.con.con.commit()
        cur.close()

    @classmethod
    def tearDownClass(cls):
        cls.con.delete_carts()
        cls.con.delete_products()
        cls.con.delete_users()

        cls.con.close()

    @classmethod
    def _get_config(cls):
        host = os.getenv(PG_HOST)
        port = os.getenv(PG_PORT)
        user = os.getenv(PG_USER)
        pw = os.getenv(PG_PASS)
        db = os.getenv(PG_DB)

        config = dbc.PostgresConnection.DEFAULT_CONFIG.copy()

        if host is not None:
            config['host'] = host
        if port is not None:
            config['port'] = str(port)
        if user is not None:
            config['username'] = user
        if pw is not None:
            config['password'] = pw
        if db is not None:
            config['database'] = db

        return config

    def setUp(self) -> None:
        self.con.delete_carts()
        self.con.delete_products()
        self.con.delete_users()

        self.con.insert_user("Prueba1", 1)
        self.con.insert_user("Prueba2", 2)
        self.con.insert_user("Prueba3", 3)

        self.con.insert_product("Producto1", "", 1000000, 1)
        self.con.insert_product("Producto2", "", 1000000, 2)
        self.con.insert_product("Producto3", "", 1000000, 3)

        self.con.insert_cart(1, 1, 2)
        self.con.insert_cart(1, 2, 2)
        self.con.insert_cart(2, 2, 1)

    def test_query_1(self):
        self.query_1()

    def test_query_2(self):
        self.query_2()

    def test_query_3(self):
        self.query_3()

    def test_query_4(self):
        self.query_4()

    def test_query_5(self):
        self.query_5()


class RedisQueriesTest(DatabaseTest):
    @classmethod
    def setUpClass(cls):
        cls.con = dbc.RedisConnection(cls._get_config())

    @classmethod
    def tearDownClass(cls):
        cls.con.delete_all()
        cls.con.close()

    @classmethod
    def _get_config(cls):
        host = os.getenv(REDIS_HOST)
        port = os.getenv(REDIS_PORT)
        db = os.getenv(REDIS_DB)

        config = dbc.RedisConnection.DEFAULT_CONFIG.copy()

        if host is not None:
            config['host'] = host
        if port is not None:
            config['port'] = int(port)
        if db is not None:
            config['database'] = int(db)

        return config

    def setUp(self) -> None:
        self.con.delete_all()

        self.con.insert_cart(1, 1, 2)
        self.con.insert_cart(1, 2, 2)
        self.con.insert_cart(2, 2, 1)

    def test_query_1(self):
        self.query_1()

    def test_query_2(self):
        self.query_2()

    def test_query_3(self):
        self.query_3()

    def test_query_4(self):
        self.query_4()

    def test_query_5(self):
        self.query_5()
