pragma solidity ^0.8.3;

import "./tokenErc20.sol";

contract ProxyErc20 {

    address erc20;
    address owner_add;
    uint8 version;
    address created_by;
    address last_upd_by;
    uint created_at;
    uint last_upd_at;
    uint tokens;
    uint priceForToken;
    address ownerTokens;
    
    struct Balance {
        address owner;
        uint256 numOfTokens;
    }

    mapping(uint8=>Balance) public balances;
    uint8 numBalance = 0;

    struct Allowed {
        address owner;
        address delegate;
        uint256 numOfTokens;
    }

    mapping(uint8=>Allowed) public allowance;
    uint8 numAllowed = 0;
    
    mapping(address => uint) public balanceExceeds;
    
    constructor(address erc20_) public {
        erc20 = erc20_;
        version = 1;
        created_by = msg.sender;
    	last_upd_by = msg.sender;
    	created_at = block.timestamp;
    	last_upd_at = block.timestamp;
    	TokenErc20 token = TokenErc20(erc20);
        balances[0] = Balance(msg.sender, token.getTotalSupply());
        numBalance = numBalance + 1;
        owner_add = msg.sender;
    }
    
    //owner
    function setSellTokens(uint price, uint numSellTokens, uint8 currentversion) public returns (bool) {
    	if(msg.sender != owner_add) {
    		return false;
    	}
    	
    	//ver se tem os tokens necessários
    	uint256 balance = getOnlyBalance(msg.sender);
    	
    	if(balance < numSellTokens) {
    		return false;
    	}
    	
    	ownerTokens = msg.sender;
    	tokens = numSellTokens;
    	priceForToken = price;
    	version = currentversion + 1;
    	last_upd_by = msg.sender;
    	last_upd_at = block.timestamp;
    	return true;
    }
    
    function getSellDetails() public view returns (address, uint, uint, uint8, address, address, uint, uint){
    	return (ownerTokens, tokens, priceForToken, version, created_by, last_upd_by, created_at, last_upd_at);
    }
    
    function getMyBalanceExceed() public returns (uint, uint8, address, address, uint, uint){
    	return (balanceExceeds[msg.sender], version, created_by, last_upd_by, created_at, last_upd_at);
    }
    
    
    function receiveMoney() public payable returns (bool) {
    	uint numOfTokens = 0;
    	if (priceForToken > 0 && msg.value > 0) {
    		numOfTokens = msg.value/priceForToken;
    	} else {
    		return false;
    	}
    	
    	if(numOfTokens > tokens) {
    		numOfTokens = tokens;
    	}
    	
    	if (transferErc20(msg.sender, numOfTokens, version, ownerTokens, false)) {
    		tokens -= numOfTokens;	
    		balanceExceeds[msg.sender] += msg.value - (numOfTokens * priceForToken);
    	} else {
    		return false;
    	}
    	
    	version = version + 1;
    	return true;
    }
    
    function withdrawMoney(address payable _to, uint _amount) public returns (bool) {
    	if(_amount > balanceExceeds[msg.sender]) {
    		return false;
    	}
    	
    	if(balanceExceeds[msg.sender] >= balanceExceeds[msg.sender] - _amount) {
    		balanceExceeds[msg.sender] -= _amount;
    		_to.transfer(_amount);
    	    	return true;
    	}
    	
    	return false;
    }
    
    function setPriceForToken(uint newPrice, uint8 currentversion) public returns (bool) {
    	if(msg.sender != ownerTokens) {
    		return false;
    	}
    	
    	if(newPrice > 0) {
    	    priceForToken = newPrice;
    	    version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
    	    return true;
    	}
    	
    	return false;
    }
    
    function setTokens(uint newTokens, uint8 currentversion) public returns (bool) {
    	if(msg.sender != ownerTokens) {
    		return false;
    	}
    	
    	uint256 balance = getOnlyBalance(msg.sender);
    	
    	if(newTokens > 0 && balance >= newTokens) {
    	    tokens = newTokens;
    	    version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
    	    return true;
    	}
    	
    	return false;
    }
    
    receive() external payable {
    	receiveMoney();
    }

    function setAllowedStruct(address owner_, address delegate_, uint256 numTokens) private {
        bool find = false;
        for(uint8 i = 0;i<numAllowed;i++) {
            if(allowance[i].owner == owner_ && allowance[i].delegate == delegate_) {
                allowance[i].numOfTokens = numTokens;
                find = true;
            }
        }

        if(!find) {
            allowance[numAllowed] = Allowed(owner_, delegate_, numTokens);
            numAllowed = numAllowed + 1;
        }
    }

    function setAllowedStructMinus(address owner_, address delegate_, uint256 numTokens) private {
        for(uint8 i = 0;i<numAllowed;i++) {
            if(allowance[i].owner == owner_ && allowance[i].delegate == delegate_) {
                allowance[i].numOfTokens = allowance[i].numOfTokens - numTokens;
            }
        }
    }

    function setBalanceStruct(address owner_, uint256 numTokens) private {
        bool find = false;
        for(uint8 i = 0;i<numBalance;i++) {
            if(balances[i].owner == owner_) {
                balances[i].numOfTokens = numTokens;
                find = true;
            }
        }

        if(!find) {
            balances[numBalance] = Balance(owner_, numTokens);
            numBalance = numBalance + 1;
        }
    }
    
    function getNameSymbolSupply() public view returns (string memory, string memory, uint256, uint8, address, address, uint, uint){
    	TokenErc20 token = TokenErc20(erc20);
    	string memory name = token.getName();
    	string memory symbol = token.getSymbol();
    	uint256 supply = token.getTotalSupply();
    	
    	return (name, symbol, supply, version, created_by, last_upd_by, created_at, last_upd_at);
    }
    
    function getNumBalances() public view returns(uint8) {
    	return numBalance;
    }

    function getBalanceStruct(uint8 numBalance_) public view returns(address, uint256, uint8) {
        return (balances[numBalance_].owner, balances[numBalance_].numOfTokens, version);
    }
    
    function getBalance(address add) public view returns(uint256, uint8) {
    	TokenErc20 token = TokenErc20(erc20);
    	return (token.balanceOf(add), version);
    }
    
    function getOnlyBalance(address add) public view returns(uint256) {
    	TokenErc20 token = TokenErc20(erc20);
    	return token.balanceOf(add);
    }
    
    //owner
    function setBalance(address add, uint256 amount, uint8 currentversion) public returns(bool) {
    	if(msg.sender != owner_add) {
    		return false;
    	}
    	
    	TokenErc20 token = TokenErc20(erc20);
    	bool result = token.setBalanceOf(add, amount);
    	
    	if(result) {
            version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
    	    setBalanceStruct(add, amount);	
    	}
    	
    	return result;
    }
    
    function approve(address delegate, uint256 numOfTokens, uint8 currentversion) public returns(bool) {
    	TokenErc20 token = TokenErc20(erc20);
    	bool result = token.approve(msg.sender, delegate, numOfTokens);
    	
    	if(result) {
            version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
            setAllowedStruct(msg.sender, delegate, numOfTokens);
    	}
    	
    	return result;
    }

    function getNumAllowance() public view returns(uint8) {
    	return numAllowed;
    }

    function getAllowance(uint8 numAllow) public view returns(address, address, uint256, uint8) {
    	return (allowance[numAllow].owner, allowance[numAllow].delegate, allowance[numAllow].numOfTokens, version);
    }
    
    function transferErc20(address receiver, uint256 numTokens, uint8 currentversion, address owner, bool isSender) public returns (bool) {
    	TokenErc20 token = TokenErc20(erc20);
    	if (isSender) {
	    	owner = msg.sender;
    	} 
    	
    	bool result = token.transfer(owner, receiver, numTokens);
    	
    	if(result) {
    	    version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
            setBalanceStruct(receiver, getOnlyBalance(receiver));
	    setBalanceStruct(owner, getOnlyBalance(owner));			
    	}
    	
    	return result;
    }
    
    //owner
    function setAllowance(address owner_, address delegate, uint256 numOfTokens, uint8 currentversion) public returns(bool) {
    	if(msg.sender != owner_add) {
    		return false;
    	}
    	
    	TokenErc20 token = TokenErc20(erc20);
    	bool result = token.setAllowance(owner_, delegate, numOfTokens);
    	
    	if(result) {
            version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
            setAllowedStruct(owner_, delegate, numOfTokens);
    	}
    	
    	return result;
    }
    
    function transferFromErc20(address owner, address buyer, uint256 numTokens, uint8 currentversion) public returns (bool) {
    	TokenErc20 token = TokenErc20(erc20);
    	bool result = token.transferFrom(msg.sender, owner, buyer, numTokens);
    	
    	if(result) {
            version = currentversion + 1;
    	    last_upd_by = msg.sender;
    	    last_upd_at = block.timestamp;
    	    setBalanceStruct(buyer, getOnlyBalance(buyer));	
            setBalanceStruct(owner, getOnlyBalance(owner));
            setAllowedStructMinus(owner, msg.sender, numTokens);		
    	}
    	
    	return result;
    }
}
