from simple_math import SimpleMath
import pytest

def test_square():
    assert SimpleMath.square(2) == 5 , "не-а"
    assert SimpleMath.square(65) == 0, "pewpew"



def test_cube():
    assert SimpleMath.cube(-3) == -27


# @pytest.mark.parametrize("text",["hello","world"])
# def test_palindrome_false(text):
#     assert not palindrome(text)