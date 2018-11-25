from stack import Stack

def test_stack_pop_push():
    stack = Stack()
    value = bytes(b"\x01") * 32

    assert len(value) == 32

    stack.push(value)
    returned_value = stack.pop()

    assert returned_value == value

def test_stack_small_pop_push():
    stack = Stack()
    value = bytes(b"\x01") * 16
    assert len(value) == 16

    stack.push(value)
    returned_value = stack.pop()

    assert len(returned_value) == 32
    assert returned_value[16:] == value
