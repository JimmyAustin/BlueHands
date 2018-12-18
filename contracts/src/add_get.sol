contract Addition{
    int x;
    function add(int a, int b) public{
        x = a + b;
    }

    function get() public returns (int) {
        return x;
    }
}