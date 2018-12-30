contract set_add{
    int x;
    function set(int a) public{
        x = a;
    }

    function get(int b) public returns (int) {
        return x + b;
    }
}