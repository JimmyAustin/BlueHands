pragma solidity ^0.5.1;

contract bankCFOVuln {
    address cfo;
    mapping (address => uint) deposits;
    
    function setCFO(address newCFO) public {
        cfo = newCFO;
    }
    
    function deposit() payable public {
        deposits[msg.sender] += msg.value;
    }

    function _withdraw(address withdrawAddress, uint withdraw_amount) private {
        require(deposits[withdrawAddress] >= withdraw_amount);
        deposits[withdrawAddress] -= withdraw_amount;
        msg.sender.call.value(withdraw_amount)("");
    }

    function withdraw(uint amount) public {
        _withdraw(msg.sender, amount);
    }

    function cfoWithdraw(address withdraw_address, uint amount) public {
        require(msg.sender == cfo);
        _withdraw(withdraw_address, amount);
    }
}