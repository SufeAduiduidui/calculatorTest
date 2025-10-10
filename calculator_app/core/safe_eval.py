import math
import ast

#安全计算器核心
class SafeEvaluator:
    def __init__(self, deg_mode=False):
        self.deg_mode = deg_mode
        self.last_result = 0.0

    def _make_trig(self):
        deg = self.deg_mode
        def sin(x): return math.sin(math.radians(x) if deg else x)
        def cos(x): return math.cos(math.radians(x) if deg else x)
        def tan(x): return math.tan(math.radians(x) if deg else x)
        def asin(x):
            y = math.asin(x); return math.degrees(y) if deg else y
        def acos(x):
            y = math.acos(x); return math.degrees(y) if deg else y
        def atan(x):
            y = math.atan(x); return math.degrees(y) if deg else y
        return sin, cos, tan, asin, acos, atan

    def _allowed_names(self, extra_vars=None):
        sin, cos, tan, asin, acos, atan = self._make_trig()
        allowed = {
            "pi": math.pi, "e": math.e,
            "sqrt": math.sqrt, "pow": math.pow,
            "log": math.log, "log10": math.log10, "ln": math.log,
            "exp": math.exp, "abs": abs,
            "sin": sin, "cos": cos, "tan": tan,
            "asin": asin, "acos": acos, "atan": atan,
            "ans": self.last_result, "Ans": self.last_result,
        }
        if extra_vars:
            allowed.update(extra_vars)
        return allowed

#预处理输入的表达式
    def _preprocess(self, expr):
        expr = expr.replace("^", "**")
        expr = expr.replace("\u03C0", "pi")
        expr = expr.replace("√", "sqrt")
        return expr


    def evaluate(self, expr, variables=None):
        expr = self._preprocess(expr)
        try:
            node = ast.parse(expr, mode="eval")
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

        allowed_ops = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b,
            ast.FloorDiv: lambda a, b: a // b,
            ast.Mod: lambda a, b: a % b,
            ast.Pow: lambda a, b: a ** b,
        }
        allowed_unary = {
            ast.UAdd: lambda a: +a,
            ast.USub: lambda a: -a,
        }

        allowed = self._allowed_names(variables)

        def _eval(n):
            if isinstance(n, ast.Expression):
                return _eval(n.body)
            if hasattr(ast, "Num") and isinstance(n, ast.Num):
                return n.n
            if isinstance(n, ast.Constant):
                if isinstance(n.value, (int, float)):
                    return n.value
                raise ValueError("Only numeric constants are allowed")
            if isinstance(n, ast.BinOp):
                op = type(n.op)
                if op not in allowed_ops:
                    raise ValueError("Operator not allowed")
                return allowed_ops[op](_eval(n.left), _eval(n.right))
            if isinstance(n, ast.UnaryOp):
                op = type(n.op)
                if op not in allowed_unary:
                    raise ValueError("Unary operator not allowed")
                return allowed_unary[op](_eval(n.operand))
            if isinstance(n, ast.Call):
                if not isinstance(n.func, ast.Name):
                    raise ValueError("Only simple function calls are allowed")
                fname = n.func.id
                if fname not in allowed or not callable(allowed[fname]):
                    raise ValueError(f"Function '{fname}' not allowed")
                args = [_eval(a) for a in n.args]
                if len(n.keywords) != 0:
                    raise ValueError("No keyword arguments allowed")
                return allowed[fname](*args)
            if isinstance(n, ast.Name):
                if n.id in allowed:
                    return allowed[n.id]
                raise ValueError(f"Name '{n.id}' not allowed")
            raise ValueError("Unsupported expression element")

        result = _eval(node)
        try:
            self.last_result = float(result)
        except Exception:
            pass
        return result
