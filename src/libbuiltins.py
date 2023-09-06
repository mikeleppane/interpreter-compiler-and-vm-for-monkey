from src.object import Builtin, Error, Integer, Object, String


def len_builtin(*args: Object) -> Object:
    if len(args) != 1:
        return Error(message=f"wrong number of arguments. got={len(args)}, want=1")
    arg = args[0]
    if isinstance(arg, String):
        return Integer(value=len(arg.value))
    return Error(message=f"argument to 'len' not supported, got {args[0].type()}")


builtins: dict[str, Builtin] = {
    "len": Builtin(fn=len_builtin),
}
