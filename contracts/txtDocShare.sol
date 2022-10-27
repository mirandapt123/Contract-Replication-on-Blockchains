pragma solidity ^0.4.25;

contract TxtDocShare {

    address owner_add;
    bool status;
    
    constructor() public {
        owner_add = msg.sender;
        status = true;
    }

    modifier owner() {
        require(msg.sender == owner_add, "Error: Access Denied.");
        _;
    }
    
    struct Doc {
        string docname;
        string text;
        uint8 version;
        address created_by;
        address last_upd_by;
        uint created_at;
        uint last_upd_at;
        bool status;
    }

    mapping(uint8=>Doc) public docs;
    
    uint8 numDocs;
    
    //function to add file to mapping

    function addDoc(string memory docname, string memory text) public owner returns(uint8) {
        uint8 docID = numDocs++; //assign id of the doc
        docs[docID] = Doc(docname,text,1, msg.sender, msg.sender, now, now, true); //add the values to the mapping
        return docID;
    }
    
    function getNumDocs() public view returns(uint8) {
    	uint8 numActiveDocs = 0;
        for(uint8 i = 0;i<numDocs;i++) {
            if(docs[i].status == true) {
                numActiveDocs ++;
            }
        }
        return numActiveDocs;
    }
    
    function setStatus(uint8 docID) public owner  {
    	docs[docID].status = false;
    }
    
    function getActiveDoc(uint8 docID) private view returns(uint8){
    	uint8 numActiveDocs = 0;
        for(uint8 i = 0;i<numDocs;i++) {
            if(docs[i].status == true && docID == numActiveDocs) {
                return numActiveDocs;
            }
            
            if(docs[i].status == true){
            	numActiveDocs ++;
            }
            
        }
        
        return uint8(-1);
    }
    
    function getVersion(uint8 docID) public view returns(uint8) {
        return docs[docID].version;
    }
    
    function getDoc(uint8 docID) public view returns (string memory, string memory, uint8, address, address, uint, uint) {
    	uint8 numDocs = getActiveDoc(docID);
        return (docs[numDocs].docname, docs[numDocs].text, docs[numDocs].version, docs[numDocs].created_by, docs[numDocs].last_upd_by, docs[numDocs].created_at, docs[numDocs].last_upd_at);
    }
    
    function editDoc(uint8 docID, string memory docname, string memory text, uint8 currentversion) public returns(uint8) {
    	uint8 numDocs = getActiveDoc(docID);
    	uint8 nextVersion = currentversion + 1;
    	bytes memory tempDocname = bytes(docname);
    	bytes memory tempText = bytes(text);
    	uint8 result = uint8(1);
    	
    	if(tempDocname.length != 0) {
    		docs[numDocs].docname = docname;
    	}
    	
    	if(tempText.length != 0) {
    		docs[numDocs].text = text;
    	}
    	
    	if(tempText.length != 0 || tempDocname.length != 0) {
    		docs[numDocs].version = nextVersion;
    		docs[numDocs].last_upd_by = msg.sender;
    		docs[numDocs].last_upd_at = now;
    		return result;
    	}
    	
    	result = uint8(-1);
    	return result;
    	
    } 

}
