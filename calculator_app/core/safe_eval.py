import ast
import math


class SafeEvaluator:
    def __init__(self, deg_mode=False):
        self.deg_mode = deg_mode
        self.last_result = 0.0

    def _make_trig(self):
        deg = self.deg_mode

        def sin(x):
            return math.sin(math.radians(x) if deg else x)

        def cos(x):
            return math.cos(math.radians(x) if deg else x)

        def tan(x):
            return math.tan(math.radians(x) if deg else x)

        def asin(x):
            result = math.asin(x)
            return math.degrees(result) if deg else result

        def acos(x):
            result = math.acos(x)
            return math.degrees(result) if deg else result

        def atan(x):
            result = math.atan(x)
            return math.degrees(result) if deg else result

        return sin, cos, tan, asin, acos, atan

    
    def _nth_root(self, degree, value):
        try:
            deg = float(degree)
        except (TypeError, ValueError):
            raise ValueError("Root degree must be a number")
        if not math.isfinite(deg):
            raise ValueError("Root degree must be finite")
        if math.isclose(deg, 0.0, abs_tol=1e-12):
            raise ValueError("Zeroth root is undefined")

        try:
            val = float(value)
        except (TypeError, ValueError):
            raise ValueError("Root radicand must be a number")
        if not math.isfinite(val):
            raise ValueError("Root radicand must be finite")

        power = 1.0 / deg

        if math.isclose(val, 0.0, abs_tol=1e-12):
            if power < 0.0:
                raise ValueError("Negative degree root of zero is undefined")
            return 0.0

        if val < 0.0:
            deg_int = int(round(deg))
            if (not math.isclose(deg, deg_int, rel_tol=1e-9, abs_tol=1e-9)) or deg_int % 2 == 0:
                raise ValueError("Even root of a negative number is not real")
            return -((-val) ** power)

        return val ** power

    def _factorial(self, value):
        try:
            val = float(value)
        except (TypeError, ValueError):
            raise ValueError("阶乘参数必须是数字")
        if not math.isfinite(val):
            raise ValueError("阶乘参数必须是有限数")
        n = int(round(val))
        if not math.isclose(val, n, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError("阶乘参数必须是整数")
        if n < 0:
            raise ValueError("阶乘参数必须是非负整数")
        return math.factorial(n)

    def _allowed_names(self, extra_vars=None):
        sin, cos, tan, asin, acos, atan = self._make_trig()
        allowed = {
            "pi": math.pi,
            "e": math.e,
            "sqrt": math.sqrt,
            "pow": math.pow,
            "log": math.log,
            "log10": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "abs": abs,
            "sin": sin,
            "cos": cos,
            "tan": tan,
            "asin": asin,
            "acos": acos,
            "atan": atan,
            "arcsin": asin,
            "arccos": acos,
            "arctan": atan,
            "root": self._nth_root,
            "yroot": self._nth_root,
            "nthroot": self._nth_root,
            "fact": self._factorial,
            "factorial": self._factorial,
            "ans": self.last_result,
            "Ans": self.last_result,
        }
        if extra_vars:
            allowed.update(extra_vars)
        return allowed

    def _preprocess(self, expr):
        if not isinstance(expr, str):
            raise ValueError("Expression must be a string")
        expr = expr.replace("^", "**")
        expr = expr.replace("\u03C0", "pi")
        expr = expr.replace("\u221a", "sqrt")
        expr = expr.replace("√", "sqrt")
        expr = expr.replace("ANS", "Ans")
        replacements = {
            "sin^-1": "arcsin",
            "cos^-1": "arccos",
            "tan^-1": "arctan",
            "SIN^-1": "arcsin",
            "COS^-1": "arccos",
            "TAN^-1": "arctan",
            "sin⁻¹": "arcsin",
            "cos⁻¹": "arccos",
            "tan⁻¹": "arctan",
        }
        for key, value in replacements.items():
            expr = expr.replace(key, value)
        return expr

    def evaluate(self, expr, variables=None):
        expr = self._preprocess(expr)
        try:
            node = ast.parse(expr, mode="eval")
        except Exception as exc:
            raise ValueError(f"Invalid expression: {exc}")

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

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if hasattr(ast, "Num") and isinstance(node, ast.Num):
                return node.n
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Only numeric constants are allowed")
            if isinstance(node, ast.BinOp):
                op = type(node.op)
                if op not in allowed_ops:
                    raise ValueError("Operator not allowed")
                return allowed_ops[op](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp):
                op = type(node.op)
                if op not in allowed_unary:
                    raise ValueError("Unary operator not allowed")
                return allowed_unary[op](_eval(node.operand))
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    raise ValueError("Only simple function calls are allowed")
                fname = node.func.id
                if fname not in allowed or not callable(allowed[fname]):
                    raise ValueError(f"Function '{fname}' not allowed")
                args = [_eval(arg) for arg in node.args]
                if node.keywords:
                    raise ValueError("No keyword arguments allowed")
                return allowed[fname](*args)
            if isinstance(node, ast.Name):
                if node.id in allowed:
                    return allowed[node.id]
                raise ValueError(f"Name '{node.id}' not allowed")
            raise ValueError("Unsupported expression element")

        result = _eval(node)
        try:
            self.last_result = float(result)
        except Exception:
            pass
        return result
