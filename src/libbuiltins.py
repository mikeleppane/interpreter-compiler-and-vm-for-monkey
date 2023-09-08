from src.object import Array, Builtin, Error, Integer, Null, Object, String


def len_builtin(*args: Object) -> Object:
    if len(args) != 1:
        return Error(message=f"wrong number of arguments. got={len(args)}, want=1")
    arg = args[0]
    if isinstance(arg, String):
        return Integer(value=len(arg.value))
    if isinstance(arg, Array):
        return Integer(value=len(arg.elements))
    return Error(message=f"argument to 'len' not supported, got {args[0].type()}")


def first_builtin(*args: Object) -> Object:
    if len(args) != 1:
        return Error(message=f"wrong number of arguments. got={len(args)}, want=1")
    arr = args[0]
    if not isinstance(arr, Array):
        return Error(message=f"argument to 'first' must be ARRAY, got {args[0].type()}")
    if len(arr.elements) > 0:
        return arr.elements[0]
    return Null()


def last_builtin(*args: Object) -> Object:
    if len(args) != 1:
        return Error(message=f"wrong number of arguments. got={len(args)}, want=1")
    arr = args[0]
    if not isinstance(arr, Array):
        return Error(message=f"argument to 'last' must be ARRAY, got {args[0].type()}")
    try:
        return arr.elements[-1]
    except IndexError:
        return Null()


def rest_builtin(*args: Object) -> Object:
    if len(args) != 1:
        return Error(message=f"wrong number of arguments. got={len(args)}, want=1")
    arr = args[0]
    if not isinstance(arr, Array):
        return Error(message=f"argument to 'rest' must be ARRAY, got {args[0].type()}")
    try:
        return Array(elements=list(arr.elements[1:]))
    except IndexError:
        return Null()


def push_builtin(*args: Object) -> Object:
    if len(args) != 2:
        return Error(message=f"wrong number of arguments. got={len(args)}, want=2")
    arr = args[0]
    if not isinstance(arr, Array):
        return Error(message=f"argument to 'push' must be ARRAY, got {args[0].type()}")
    try:
        new_arr = list(arr.elements)
        new_arr.append(args[1])
        return Array(elements=new_arr)
    except IndexError:
        return Null()


def puts_builtin(*args: Object) -> Object:
    for arg in args:
        print(arg.inspect())
    return Null()


builtins: dict[str, Builtin] = {
    "len": Builtin(fn=len_builtin),
    "first": Builtin(fn=first_builtin),
    "last": Builtin(fn=last_builtin),
    "rest": Builtin(fn=rest_builtin),
    "push": Builtin(fn=push_builtin),
    "puts": Builtin(fn=puts_builtin),
}
