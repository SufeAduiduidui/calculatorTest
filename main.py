#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from calculator_app.app import CalculatorApp

def main():
    try:
        app = CalculatorApp()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
