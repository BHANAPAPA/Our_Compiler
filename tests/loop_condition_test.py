import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from evaluator import *


@pytest.mark.parametrize("expression, expected", [
    ("if 5 < 10 then 1 else 0 end", "1"),
    ("if 5 < 10 then if 2 < 3 then 1 else 0 end else 0 end", "1"),
    ("if 0 < 1 then 1 else 0 end", "1"),
    ("if 2 < 3 then if 4 > 5 then 0 else 1 end else 2 end", "1"),
    ("if 5 == 5 then 10 end", "10")
])
def test_conditional_expressions(expression, expected, capfd):
    execute(f"display({expression})")
    captured = capfd.readouterr()
    assert captured.out.strip() == expected

def test_for_loop_sum(capfd):
    code2 = """
    var integer sum=0;
    for (var i=1;i<10;i+=1){
        sum+=i;
    };
    displayl sum;
    display "done";
    """
    execute(code2)
    captured = capfd.readouterr()
    assert "45" in captured.out
    assert "done" in captured.out

def test_loop_function(capfd):
    prog = """fn loopFunction(n) {
        var i = 0;
        while (i < n) {
            displayl(i);
            i = i + 1;
        };
    };
    var x = 5;
    displayl("Calling loopFunction with x=5");
    loopFunction(x); 
    """
    execute(prog)
    captured = capfd.readouterr()
    assert "Calling loopFunction with x=5" in captured.out
    assert captured.out.strip().endswith("0\n1\n2\n3\n4")

def test_char_ascii_operations(capfd):
    prog = """var a= char (66);
    displayl a;
    var b= ascii("A");
    displayl b;
    var c= char (ascii('x') + ascii (char(1)));
    displayl c;"""
    execute(prog)
    captured = capfd.readouterr()
    assert "B" in captured.out
    assert "65" in captured.out
    assert "y" in captured.out

def test_conditional_execution_1(capfd):
    prog = """var x = 10;
    displayl if x > 5 then 
                { 
                    if x > 8 
                    then 
                        displayl "greater than 8"; end; 
                } 
            else { 
                displayl "less than 5";
                displayl "not greater than 5";
             } end;"""
    execute(prog)
    captured = capfd.readouterr()
    assert "greater than 8" in captured.out
    

def test_conditional_execution_2(capfd):
    prog = """var x = 0;
    displayl if x > 5 then 
                { 
                    if x > 8 
                    then 
                        displayl "greater than 8"; end; 
                } 
            else { 
                displayl "less than 5";
                displayl "not greater than 5";
             } end;"""
    execute(prog)
    captured = capfd.readouterr()
    assert "less than 5" in captured.out
    assert "not greater than 5" in captured.out

if __name__ =="__main__":
    prog="""
    var x=1000;
    while (x>0){
        if (x%3==0 or x%5==0)
        then
        {
            displayl x;
        }
        else{
            displayl "Not divisible by 3 or 5";
        }
        end;
        x=x-1;
    };
"""
    prog="""fn loopFunction(n) {
        var i = 0;
        while (i < n) {
            displayl(i);
            i = i + 1;
        };
    };
    var x = 5;
    displayl("Calling loopFunction with x=5");
    loopFunction(x);"""

    print(parse(prog))
    print(execute(prog))

    