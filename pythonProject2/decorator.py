def bold(x):
    def wrapper():
       
        return "<b>" + x() + "</b>"
    return wrapper
   
def italic(x):
    def wrapper():
        return "<i>" + x() + "</i>"
    return wrapper
   
@bold
@italic
def bolditalic():
    return "hello"
print(bolditalic())


def excam(f):
    def wrapper(name):
        return f(name) + '!'

    return wrapper


@excam
def greet(name):
    return name


print(greet("Hello"))