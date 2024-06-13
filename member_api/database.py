from flask import g
import sqlite3


def connect_db():
    """
    Estabelece uma conexão com o banco de dados SQLite.
    Configura a fábrica de linhas para retornar dicionários ao invés de tuplas.
    """
    sql = sqlite3.connect('questions.db')
    sql.row_factory = sqlite3.Row  # Retorna as linhas como dicionários ao invés de tuplas
    return sql

def get_db():
    """
    Obtém a conexão com o banco de dados armazenada em g.
    Se não existir, cria uma nova conexão e a armazena em g.
    """
    if not hasattr(g, 'sqlite_db'):  # Verifica se 'sqlite_db' não existe em 'g'
        g.sqlite_db = connect_db()  # Conecta ao banco de dados e armazena a conexão em 'g'
    return g.sqlite_db