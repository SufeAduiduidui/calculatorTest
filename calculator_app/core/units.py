#进制转换
class UnitConverter:
    LENGTH_FACTORS = {
        "km": 1000.0, "m": 1.0, "cm": 0.01, "mm": 0.001,
        "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254,
    } #各单位相对米的转换因子
    MASS_FACTORS = {
        "t": 1000.0, "kg": 1.0, "g": 0.001, "lb": 0.45359237, "oz": 0.028349523125,
    }
    TEMP_UNITS = ["C", "F", "K"]#预处理单位


    @staticmethod
    def convert_length(value, from_u, to_u):
        if from_u not in UnitConverter.LENGTH_FACTORS or to_u not in UnitConverter.LENGTH_FACTORS:
            raise ValueError("unsupported length unit")

        meters = value * UnitConverter.LENGTH_FACTORS[from_u]
        return meters / UnitConverter.LENGTH_FACTORS[to_u]#输入值转为米再/目标单位转化因子
    @staticmethod
    def convert_mass(value, from_u, to_u):
        if from_u not in UnitConverter.MASS_FACTORS or to_u not in UnitConverter.MASS_FACTORS:
            raise ValueError("Unsupported mass unit")
        kg = value * UnitConverter.MASS_FACTORS[from_u]
        return kg / UnitConverter.MASS_FACTORS[to_u]
    @staticmethod
    def convert_temp(value, from_u, to_u):
        from_u, to_u = from_u.upper(), to_u.upper()
        if from_u not in UnitConverter.TEMP_UNITS or to_u not in UnitConverter.TEMP_UNITS:
            raise ValueError("Unsupported temperature unit")
        if from_u == "C":
            k = value + 273.15
        elif from_u == "F":
            k = (value - 32) * 5.0/9.0 + 273.15
        else:
            k = value
        if to_u == "C":
            return k - 273.15
        elif to_u == "F":
            return (k - 273.15) * 9.0/5.0 + 32
        else:
            return k
