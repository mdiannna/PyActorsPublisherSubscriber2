from flask import session

def most_frequent(List): 
    return max(set(List), key = List.count) 


def set_session_var(name, value):
	session[name] = value


def get_session_var(name):
	return session.get[name]


