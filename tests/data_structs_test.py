import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from evaluator import *
from pprint import pprint

@pytest.mark.parametrize("code, expected_output", [
    # Test 1: Basic assignment and reassignment
    ("""
    var a =[1,2,3,4];
    var b =20;
    a[1]=b;
    displayl a;
    displayl a[2];
    var c=[10,11,12,13];
    c[1]=a[2]+b;
    displayl c;
    """, "[1, 20, 3, 4]\n3\n[10, 23, 12, 13]"),
    
    # Test 2: Access first and last element
    ("""
    var a =[10, 20, 30, 40];
    displayl a[0];
    displayl a[3];
    """, "10\n40"),
    
    # Test 3: Modify using arithmetic operations
    ("""
    var a =[5, 10, 15, 20];
    a[2] = a[2] + a[1];
    a[8-6-1] = a[0] * a[3];
    displayl a;
    var b=[20,11];
    a=b;
    displayl a;
    """, "[5, 100, 25, 20]\n[20, 11]"),

])
def test_array_operations(code, expected_output, capfd):
    execute(code)
    captured = capfd.readouterr()
    assert captured.out.strip() == expected_output


@pytest.mark.parametrize("code, expected_output", [
    ("""
    var a = [1,2,3,4,5];
    a.PushFront(0);
    displayl a;
    a.PushBack(6);
    displayl a;
    displayl a.PopFront;
    displayl a[a.Length-1];
    displayl a;
    displayl a.PopBack;
    displayl a;
    displayl a.Length;
    a.Insert(3, 10);
    displayl a;
    a.Remove(1);
    displayl a;
    a.Clear;
    displayl a;
    displayl a.Length;
    """, 
    """[0, 1, 2, 3, 4, 5]
[0, 1, 2, 3, 4, 5, 6]
0
6
[1, 2, 3, 4, 5, 6]
6
[1, 2, 3, 4, 5]
5
[1, 2, 3, 10, 4, 5]
[1, 3, 10, 4, 5]
[]
0""")
])
def test_array_functions(code, expected_output, capfd):
    execute(code)
    captured = capfd.readouterr()
    assert captured.out.strip() == expected_output


@pytest.mark.parametrize("code, expected_output", [
    # Test arithmetic operations with variables
    ("""
    var x = 1;
    var y = 2;
    var z = 4;
    var p = x * y - z;
    displayl p;
    """, "-2"),
    # Test floating-point operations with combined operators
    ("""
    var a = 5.5;
    var b = 2.2;
    displayl (a * b) - a + (a % b);
    displayl (a / b) + (a ^ 2) - b; 
    displayl (a > b) and (a < (b + 10)); 
    displayl not (a == b);
    """, "7.700000000000001\n30.55\nTrue\nTrue"),

    # # Test floating-point operations with variables, numbers, and combined operators
    ("""
    var x = -3.3;
    displayl (x + 1.1) * (x - 1.1) / (x % 1.1 + 1.0);
    displayl (x ^ 2.0) - (x * 2.0) + (x / 2.0);
    """, "9.679999999999996\n15.839999999999998"),

    # # Test floating-point operations inside a loop with combined operators
    ("""
    var y = 1.0;
    for (var i = 0.5; i <= 2.0; i = i + 0.5) {
        displayl (y + i) * (y * i) - (y / i);
    }
    """, "-1.25\n1.0\n3.0833333333333335\n5.5"),
    # # Test floating-point operations inside a function with combined operators
    ("""
    fn calculate(x, y) {
        displayl (x + y) * (x - y) / (x % y + 1.0);
        displayl (x ^ y) - (x * y) + (x / y);
    }
    calculate(4.4, 2.2);
    """, "14.520000000000003\n18.35729647727544"),

    # # Test floating-point operations in a loop and function combined with mixed operators
    ("""
    fn compute(x, y) {
        (x * y) + (y / x) - (x % y);
    }
    var z = 1.0;
    for (var j = 0.5; j <= 2.0; j += 0.5) {
        z = compute(z, j);
        displayl z;
    }
    """, "1.0\n2.0\n3.25\n5.865384615384615"),
    # Test floating-point addition with variables
    ("""
    var a = 2.34;
    var b = 1.23;
    displayl a + b;
    """, "3.57"),
    # Test floating-point variables in a while loop
    ("""
    var a = 0.5;
    while (a < 2.5) {
        displayl a;
        a = a + 0.5;
    }
    """, "0.5\n1.0\n1.5\n2.0"),

    # Test floating-point variables in a for loop
    ("""
    for (var b = 1.0; b <= 2.0; b = b + 0.5) {
        displayl b;
    }
    """, "1.0\n1.5\n2.0"),

    # Test floating-point variables inside a function
    ("""
    fn multiplyByTwo(x) {
        x * 2.0;
    }
    var c = 1.25;
    displayl multiplyByTwo(c);
    """, "2.5"),

    # Test floating-point variables in a function and a loop combined
    ("""
    fn addAndDisplay(x, y) {
        var result = x + y;
        displayl result;
        result;
    }
    var d = 0.5;
    for (var e = 1.0; e <= 2.0; e = e + 0.5) {
        d = addAndDisplay(d, e);
    }
    """, "1.5\n3.0\n5.0"),

    # Test floating-point variables in a while loop and function combined
    ("""
    fn subtractAndDisplay(x, y) {
        var result = x - y;
        displayl result;
        result;
    };
    var f = 5.0;
    var g = 0.5;
    while (f > 0.0) {
        f = subtractAndDisplay(f, g);
    }
    """, "4.5\n4.0\n3.5\n3.0\n2.5\n2.0\n1.5\n1.0\n0.5\n0.0")
])
def test_floating_point_operations(code, expected_output, capfd):
    execute(code)
    captured = capfd.readouterr()
    assert captured.out.strip() == expected_output

if __name__ == "__main__":
    
    prog= """
    var y = 1.0;
    for (var i = 0.5; i <= 2.0; i = i + 0.5) {
        displayl (y + i) * (y * i) - (y / i);
    }
    """ 


    pprint(list(lex(prog)))
    pprint(parse(prog))
    execute(prog)