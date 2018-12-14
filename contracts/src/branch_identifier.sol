pragma solidity ^0.5.1;

contract branchTest {
  function renderAdd (int value) public pure returns (int) {
    if (value == 5) {
      return 1;
    } else {
      return 0;
    }
  }
}