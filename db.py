from config import DATABASE

if DATABASE == "sqlite":
    from database_s import *

elif DATABASE == "mongodb":
    from database_m import *
