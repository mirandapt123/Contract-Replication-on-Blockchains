pragma solidity ^0.8.3;

contract TokenErc20 {

    string public name;
    string public symbol;
    uint256 totalSupply;
    address owner_add;
    
    constructor(uint256 totalOfSupply, string memory name_, string memory symbol_) public {
        totalSupply = totalOfSupply;
        balances[msg.sender] = totalSupply;
        name = name_;
        symbol = symbol_;
        owner_add = msg.sender;
    }

    mapping(address => uint256) balances;
    mapping(address => mapping(address => uint256)) allowed;

    function getName() public view returns(string memory) {
    	return name;
    }
    
    function getSymbol() public view returns(string memory) {
    	return symbol;
    }

    function getTotalSupply() public view returns(uint256) {
    	return totalSupply;
    }
    
    function balanceOf(address tokenOwner) public view returns(uint256) {
    	return balances[tokenOwner];
    }
    
    function transfer(address owner, address receiver, uint256 numTokens) public returns (bool) {
    	require(numTokens <= balances[owner]);
    	balances[owner] = balances[owner] - numTokens;
    	balances[receiver] = balances[receiver] + numTokens;
    	emit Transfer(owner, receiver, numTokens);
    	return true;
    }
    
    function approve(address sender, address delegate, uint256 numTokens) public returns (bool) {
    	allowed[sender][delegate] = numTokens;
    	emit Approval(sender, delegate, numTokens);
    	return true;
    }
    
    function allowance(address owner, address delegate) public view returns(uint256) {
    	return allowed[owner][delegate];
    }
    
    function transferFrom(address sender, address owner, address buyer, uint256 numTokens) public returns (bool) {
    	require(numTokens <= balances[owner]);
    	require(numTokens <= allowed[owner][sender]);
    	balances[owner] = balances[owner] - numTokens;
    	allowed[owner][sender] = allowed[owner][sender] - numTokens;
    	balances[buyer] = balances[buyer] + numTokens;
    	emit Transfer(owner, buyer, numTokens);
    	return true;
    }
    
    //owner
    function setBalanceOf(address tokenOwner, uint256 amount) public returns (bool){
    	if(msg.sender != owner_add) {
    		return false;
    	}
    	
    	balances[tokenOwner] = amount;
    	return true;
    }
    
    //owner
    function setAllowance(address owner, address delegate, uint256 amount) public returns(bool) {
    	if(msg.sender != owner_add) {
    		return false;
    	}
    	
    	allowed[owner][delegate] = amount;
    	return true;
    }
    
    event Transfer(address indexed from, address indexed to, uint256 tokens);
    event Approval(address indexed tokenOwner, address indexed spender, uint256 tokens);
    
    
    
}
