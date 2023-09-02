"""Helper functions to use with Database"""


def sqlalchemy_uri_generator(
    username: str,
    password: str,
    host: str,
    db_name: str,
    driver: str = 'postgresql'
) -> str:
    """
    Build the database URI from params
    """
    return f'{driver}://{username}:{password}@{host}/{db_name}'
